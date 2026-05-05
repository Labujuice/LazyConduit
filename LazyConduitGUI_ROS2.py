import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import threading
import subprocess
import time
import sys
import cv2

# Attempt to import rclpy (will only work inside Docker/ROS environment)
try:
    import rclpy
    from std_msgs.msg import String
    from sensor_msgs.msg import Image
    from cv_bridge import CvBridge
    from utils.ros_node import LazyConduitNode
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False

from utils.service_manager import OllamaServiceManager
from utils.parser import PromptParser
from utils.converter import FileConverter
from utils.llm_client import LLMClient

class LazyConduitGUI_ROS2:
    def __init__(self, root):
        self.root = root
        self.root.title("LazyConduit v1.0 - ROS2 DEBUG")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f8f9fa")
        
        self.service_manager = OllamaServiceManager()
        if ROS2_AVAILABLE:
            self.bridge = CvBridge()
        
        self.ollama_online = False
        self.ros_node = None
        self.ros_executor = None
        self.ros_thread = None
        
        # Test Publishers
        self.test_text_pub = None
        self.test_img_pub = None
        self.test_prompt_pub = None
        
        self.setup_ui()
        self.refresh_models()
        self.periodic_check()

    def setup_ui(self):
        # 1. Header
        header = tk.Frame(self.root, bg="#212529", height=45)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="LazyConduit ROS2 DEBUG CONSOLE", fg="#f8f9fa", bg="#212529", font=("Arial", 12, "bold")).pack(pady=10)

        # 2. ROS2 Dashboard
        ros_bar = tk.LabelFrame(self.root, text=" 🤖 ROS2 Controls ", bg="#e9ecef", font=("Arial", 10, "bold"))
        ros_bar.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        
        row1 = tk.Frame(ros_bar, bg="#e9ecef")
        row1.pack(fill=tk.X, padx=10, pady=5)
        
        self.ros_status_label = tk.Label(row1, text="ROS2: STOPPED", bg="#e9ecef", fg="#6c757d")
        self.ros_status_label.pack(side=tk.LEFT, padx=5)
        
        self.ros_btn = tk.Button(row1, text="Launch ROS2 Node", command=self.toggle_ros, state=tk.NORMAL if ROS2_AVAILABLE else tk.DISABLED)
        self.ros_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(row1, text="Scan Discovery", command=self.scan_nodes).pack(side=tk.LEFT, padx=5)

        # 3. Test Publication Area
        test_bar = tk.LabelFrame(self.root, text=" 📡 Topic Publisher (Simulator) ", bg="#f1f3f5", font=("Arial", 10, "bold"))
        test_bar.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        
        t_row1 = tk.Frame(test_bar, bg="#f1f3f5")
        t_row1.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(t_row1, text="Text Input:", bg="#f1f3f5", width=12).pack(side=tk.LEFT)
        self.test_text_entry = tk.Entry(t_row1)
        self.test_text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.pub_text_btn = tk.Button(t_row1, text="PUB TEXT", width=12, bg="#007bff", fg="white", command=self.pub_test_text, state=tk.DISABLED)
        self.pub_text_btn.pack(side=tk.LEFT, padx=5)

        t_row2 = tk.Frame(test_bar, bg="#f1f3f5")
        t_row2.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(t_row2, text="Vision Path:", bg="#f1f3f5", width=12).pack(side=tk.LEFT)
        self.test_img_path = tk.Entry(t_row2)
        self.test_img_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(t_row2, text="Browse", command=self.browse_test_img).pack(side=tk.LEFT, padx=2)
        self.pub_vision_btn = tk.Button(t_row2, text="PUB VISION", width=12, bg="#17a2b8", fg="white", command=self.pub_test_vision, state=tk.DISABLED)
        self.pub_vision_btn.pack(side=tk.LEFT, padx=5)

        # 4. Model & Service Status Bar
        status_bar = tk.Frame(self.root, bg="#f8f9fa")
        status_bar.pack(side=tk.TOP, fill=tk.X, padx=20, pady=5)
        self.ollama_status_btn = tk.Button(status_bar, text="Ollama: ???", width=20, state=tk.DISABLED, disabledforeground="white")
        self.ollama_status_btn.pack(side=tk.LEFT, padx=5)
        tk.Label(status_bar, text="Model:", bg="#f8f9fa").pack(side=tk.LEFT, padx=5)
        self.model_combo = ttk.Combobox(status_bar, width=25)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        tk.Button(status_bar, text="Clear Log", command=self.clear_log).pack(side=tk.RIGHT, padx=5)

        # 5. Log Area
        log_frame = tk.LabelFrame(self.root, text=" 🚀 System Log / ROS2 Output ", bg="white", font=("Arial", 10, "bold"))
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.output_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Arial", 10), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def toggle_ros(self):
        if self.ros_node is None: self.start_ros()
        else: self.stop_ros()

    def start_ros(self):
        if not ROS2_AVAILABLE: return
        selected_model = self.model_combo.get() or "gemma3:1b"
        self.request_counter = 0 # Reset counter on start
        
        self.ros_btn.config(state=tk.DISABLED)
        self.root.after(1000, lambda: self.ros_btn.config(state=tk.NORMAL))

        try:
            if not rclpy.ok(): rclpy.init()
            
            # Pass model as a parameter to the node
            self.ros_node = LazyConduitNode()
            # Set the parameter dynamically before spinning
            param = rclpy.parameter.Parameter('model', rclpy.Parameter.Type.STRING, f"ollama/{selected_model}")
            self.ros_node.set_parameters([param])
            
            self.ros_executor = rclpy.executors.SingleThreadedExecutor()
            self.ros_executor.add_node(self.ros_node)
            
            # Sub to output
            self.ros_node.create_subscription(String, '/lazy_conduit/output', self.ros_output_callback, 10)
            
            # Simulation Pubs
            self.test_text_pub = self.ros_node.create_publisher(String, '/lazy_conduit/text_input', 10)
            self.test_img_pub = self.ros_node.create_publisher(Image, '/lazy_conduit/vision_input', 10)
            self.test_prompt_pub = self.ros_node.create_publisher(String, '/lazy_conduit/vision_prompt', 10)

            self.ros_thread = threading.Thread(target=self.ros_executor.spin, daemon=True)
            self.ros_thread.start()
            
            self.ros_status_label.config(text=f"● ROS2: {selected_model}", fg="#28a745")
            self.ros_btn.config(text="Stop ROS2 Node", bg="#dc3545", fg="white")
            self.pub_text_btn.config(state=tk.NORMAL)
            self.pub_vision_btn.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"[SYSTEM] Node started with model: {selected_model}\n")
        except Exception as e:
            messagebox.showerror("ROS2 Error", str(e))

    def stop_ros(self):
        if self.ros_node:
            try:
                if self.ros_executor:
                    self.ros_executor.shutdown()
                self.ros_node.destroy_node()
                # Give some time for thread to finish
                time.sleep(0.2)
            except: pass
            self.ros_node = None
            self.ros_executor = None
            self.ros_status_label.config(text="○ ROS2: STOPPED", fg="#6c757d")
            self.ros_btn.config(text="Launch ROS2 Node", bg="#f8f9fa", fg="black")
            self.pub_text_btn.config(state=tk.DISABLED)
            self.pub_vision_btn.config(state=tk.DISABLED)
            self.output_text.insert(tk.END, "[SYSTEM] ROS2 Node stopped.\n")

    def ros_output_callback(self, msg):
        """Handle structured JSON response from ROS2."""
        t_str = time.strftime('%H:%M:%S')
        try:
            import json
            data = json.loads(msg.data)
            idx = data.get("index", "?")
            dur = data.get("duration", 0.0)
            content = data.get("content", msg.data)
            
            display_txt = f"\n[{t_str}] [# {idx}] ⏱️ {dur:.2f}s >> {content}\n"
        except:
            display_txt = f"\n[{t_str}] [RAW] >> {msg.data}\n"

        self.root.after(0, lambda: self.output_text.insert(tk.END, display_txt))
        self.root.after(0, lambda: self.output_text.see(tk.END))

    def pub_test_text(self):
        txt = self.test_text_entry.get().strip()
        model = self.model_combo.get() or "gemma3:1b"
        if txt and self.test_text_pub:
            # Debounce
            self.pub_text_btn.config(state=tk.DISABLED)
            self.root.after(500, lambda: self.pub_text_btn.config(state=tk.NORMAL))
            
            self.request_counter += 1
            import json, time
            payload = json.dumps({
                "index": self.request_counter,
                "timestamp": time.time(),
                "model": f"ollama/{model}", 
                "prompt": txt
            }, ensure_ascii=False)
            
            msg = String()
            msg.data = payload
            self.test_text_pub.publish(msg)
            t_send = time.strftime('%H:%M:%S')
            self.output_text.insert(tk.END, f"📤 [{t_send}] [#{self.request_counter}] -> {txt} ({model})\n")

    def browse_test_img(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if path:
            self.test_img_path.delete(0, tk.END)
            self.test_img_path.insert(0, path)

    def pub_test_vision(self):
        path = self.test_img_path.get().strip()
        prompt = self.test_text_entry.get().strip() or "Describe this image."
        model = self.model_combo.get() or "gemma3:1b"
        if path and os.path.exists(path) and self.test_img_pub:
            # Debounce
            self.pub_vision_btn.config(state=tk.DISABLED)
            self.root.after(500, lambda: self.pub_vision_btn.config(state=tk.NORMAL))
            
            cv_img = cv2.imread(path)
            if cv_img is not None:
                img_msg = self.bridge.cv2_to_imgmsg(cv_img, encoding="bgr8")
                self.test_img_pub.publish(img_msg)
                
                self.request_counter += 1
                import json, time
                payload = json.dumps({
                    "index": self.request_counter,
                    "timestamp": time.time(),
                    "model": f"ollama/{model}", 
                    "prompt": prompt
                }, ensure_ascii=False)
                
                p_msg = String()
                p_msg.data = payload
                self.test_prompt_pub.publish(p_msg)
                t_send = time.strftime('%H:%M:%S')
                self.output_text.insert(tk.END, f"📤 [{t_send}] [#{self.request_counter}] -> (Vision) {prompt} ({model})\n")

    def scan_nodes(self):
        if not ROS2_AVAILABLE: return
        try:
            if not rclpy.ok(): rclpy.init()
            temp = rclpy.create_node('scanner_temp')
            nodes = temp.get_node_names()
            temp.destroy_node()
            self.output_text.insert(tk.END, f"[SCAN] Active Nodes: {', '.join(nodes)}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"[SCAN ERROR] {e}\n")

    def periodic_check(self):
        def task():
            self.ollama_online = self.service_manager.is_running()
            self.root.after(0, self.update_status_ui)
            self.root.after(3000, self.periodic_check)
        threading.Thread(target=task, daemon=True).start()

    def update_status_ui(self):
        txt = "● Ollama: RUNNING" if self.ollama_online else "○ Ollama: STOPPED"
        bg = "#28a745" if self.ollama_online else "#dc3545"
        self.ollama_status_btn.config(text=txt, bg=bg)

    def refresh_models(self):
        def task():
            try:
                host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                import requests
                response = requests.get(f"{host.rstrip('/')}/api/tags", timeout=3)
                if response.status_code == 200:
                    models = [m['name'] for m in response.json().get('models', [])]
                    self.root.after(0, lambda: self.model_combo.config(values=models))
                    if models: self.root.after(0, lambda: self.model_combo.set(models[0]))
            except: pass
        threading.Thread(target=task, daemon=True).start()

    def clear_log(self):
        self.output_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LazyConduitGUI_ROS2(root)
    root.mainloop()
