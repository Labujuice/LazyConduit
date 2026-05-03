import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import base64
import threading
from concurrent.futures import ThreadPoolExecutor
from .parser import PromptParser
from .converter import FileConverter
from .llm_client import LLMClient

class LazyConduitNode(Node):
    def __init__(self):
        super().__init__('lazy_conduit_node')
        
        # Parameters
        self.declare_parameter('model', 'ollama/gemma3:1b')
        self.declare_parameter('ollama_url', 'http://localhost:11434/api/generate')
        
        model_name = self.get_parameter('model').get_parameter_value().string_value
        api_url = self.get_parameter('ollama_url').get_parameter_value().string_value
        
        # Tools
        self.client = LLMClient(model=model_name, api_url=api_url)
        self.parser = PromptParser()
        self.converter = FileConverter()
        self.bridge = CvBridge()
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        
        # State
        self.latest_image_b64 = None
        self.lock = threading.Lock()

        # Subscribers
        self.text_sub = self.create_subscription(String, '/lazy_conduit/text_input', self.text_callback, 10)
        self.image_sub = self.create_subscription(Image, '/lazy_conduit/vision_input', self.image_callback, 10)
        self.vision_prompt_sub = self.create_subscription(String, '/lazy_conduit/vision_prompt', self.vision_prompt_callback, 10)
        
        # Publisher
        self.output_pub = self.create_publisher(String, '/lazy_conduit/output', 10)
        
        self.get_logger().info(f"LazyConduit Node started. Model: {model_name}")

    def image_callback(self, msg):
        """Update the latest image cache."""
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            _, buffer = cv2.imencode('.png', cv_img)
            b64_str = base64.b64encode(buffer).decode('utf-8')
            with self.lock:
                self.latest_image_b64 = b64_str
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {str(e)}")

    def text_callback(self, msg):
        """Handle pure text prompts (supports markdown file injection)."""
        self.thread_pool.submit(self.process_request, msg.data, None)

    def vision_prompt_callback(self, msg):
        """Handle vision instructions using the latest cached image."""
        with self.lock:
            img = self.latest_image_b64
        
        if img is None:
            self.get_logger().warn("Vision prompt received but no image available yet.")
            return
        
        self.thread_pool.submit(self.process_request, msg.data, [img])

    def process_request(self, prompt, images):
        """Main processing logic (Parser -> Converter -> LLM -> Publish)."""
        try:
            self.get_logger().info(f"Processing prompt: {prompt[:50]}...")
            
            # 1. Parse & Convert files
            file_links = self.parser.parse(prompt)
            final_images = images if images else []
            final_prompt = prompt
            
            for link in file_links:
                if link["exists"]:
                    mime, data = self.converter.convert(link["abs_path"])
                    if isinstance(data, list):
                        final_images.extend(data)
                        final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", "[Attached Media]")
                    else:
                        final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"\n{data}\n")
            
            if final_images:
                final_prompt = "Analyze the image(s) and follow instruction:\n" + final_prompt

            # 2. Call LLM
            response = self.client.ask(final_prompt, media=final_images if final_images else None)
            
            # 3. Publish Output
            out_msg = String()
            out_msg.data = response
            self.output_pub.publish(out_msg)
            self.get_logger().info("Response published to /lazy_conduit/output")
            
        except Exception as e:
            self.get_logger().error(f"Processing failed: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = LazyConduitNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
