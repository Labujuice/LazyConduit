import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import base64
import threading
import time
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

        # Duplication protection
        self.last_msg_hash = None
        self.last_msg_time = 0

        # Subscribers
        self.text_sub = self.create_subscription(String, '/lazy_conduit/text_input', self.text_callback, 10)
        self.image_sub = self.create_subscription(Image, '/lazy_conduit/vision_input', self.image_callback, 10)
        self.vision_prompt_sub = self.create_subscription(String, '/lazy_conduit/vision_prompt', self.vision_prompt_callback, 10)
        
        # Publisher
        self.output_pub = self.create_publisher(String, '/lazy_conduit/output', 10)
        
        self.get_logger().info(f"LazyConduit Node started. Model: {model_name}")

    def is_duplicate(self, content):
        """Check if message is a duplicate within 2.0s."""
        now = time.time()
        msg_hash = hash(content)
        if msg_hash == self.last_msg_hash and (now - self.last_msg_time) < 2.0:
            return True
        self.last_msg_hash = msg_hash
        self.last_msg_time = now
        return False

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
        """Handle pure text prompts."""
        if self.is_duplicate(msg.data):
            self.get_logger().warn(f"DEBUG: Ignoring duplicate text: {msg.data[:20]}...")
            return
        self.thread_pool.submit(self.process_request, msg.data, None)

    def vision_prompt_callback(self, msg):
        """Handle vision instructions using the latest cached image."""
        if self.is_duplicate(msg.data):
            self.get_logger().warn(f"DEBUG: Ignoring duplicate vision prompt.")
            return
            
        with self.lock:
            img = self.latest_image_b64
        
        if img is None:
            self.get_logger().warn("Vision prompt received but no image available yet.")
            return
        
        self.thread_pool.submit(self.process_request, msg.data, [img])

    def process_request(self, raw_data, images):
        """Main processing logic (Parser -> Converter -> LLM -> Publish)."""
        import time
        import json
        start_t = time.time()
        
        # 1. Parse JSON if applicable, otherwise treat as raw prompt
        target_model = self.get_parameter('model').get_parameter_value().string_value
        prompt = raw_data
        
        try:
            data = json.loads(raw_data)
            if isinstance(data, dict) and "prompt" in data:
                prompt = data["prompt"]
                if "model" in data:
                    target_model = data["model"]
        except:
            pass # Not JSON, use defaults

        self.get_logger().info(f"--- [START] Request using model [{target_model}] ---")
        
        try:
            # Update client model for this specific request
            if self.client.model != target_model:
                self.client.model = target_model

            file_links = self.parser.parse(prompt)
            final_images = images if images else []
            final_prompt = prompt
            
            for link in file_links:
                if link["exists"]:
                    mime, data = self.converter.convert(link["abs_path"])
                    if isinstance(data, list):
                        final_images.extend(data)
                        final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", "[Media]")
                    else:
                        final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"\n{data}\n")
            
            if final_images:
                # Use LLaVA or similar prompt style if needed, otherwise just append
                final_prompt = "Analyze these images: " + final_prompt

            response = self.client.ask(final_prompt, media=final_images if final_images else None)
            
            out_msg = String()
            out_msg.data = response
            self.output_pub.publish(out_msg)
            
            end_t = time.time()
            self.get_logger().info(f"--- [DONE] Response Published at {end_t:.3f} (Took {end_t-start_t:.2f}s) ---")
            
        except Exception as e:
            self.get_logger().error(f"Processing failed: {str(e)}")
