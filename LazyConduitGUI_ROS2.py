import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import threading
import subprocess
import time
import sys

# Attempt to import rclpy (will only work inside Docker/ROS environment)
try:
    import rclpy
    from utils.ros_node import LazyConduitNode
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False

from utils.service_manager import OllamaServiceManager
from utils.parser import PromptParser
from utils.converter import FileConverter
from utils.llm_client import LLMClient

class LazyConduitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LazyConduit v1.0 - ROS2 Integrated")
        self.root.geometry("1440x850") # Slightly taller for ROS2 panel
        self.root.configure(bg="#f8f9fa")
        
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.service_manager = OllamaServiceManager()
        self.parser_tool = PromptParser()
        self.converter = FileConverter()
        
        self.ollama_online = False
        self.ros_node = None
        self.ros_thread = None
        
        self.setup_ui()
        self.refresh_models()
        self.periodic_check()

    def setup_ui(self):
        # ... (header omitted for brevity)
        # 1. Header
        header = tk.Frame(self.root, bg="#212529", height=45)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="LazyConduit v1.0", fg="#f8f9fa", bg="#212529", font=("Arial", 12, "bold")).pack(pady=10)

        # 2. ROS2 Dashboard
        ros_bar = tk.LabelFrame(self.root, text=" 🤖 ROS2 Dashboard ", bg="#e9ecef", font=("Arial", 10, "bold"))
        ros_bar.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        
        self.ros_status_label = tk.Label(ros_bar, text="ROS2: NOT INITIALIZED", bg="#e9ecef", fg="#6c757d")
        self.ros_status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.ros_btn = tk.Button(ros_bar, text="Launch ROS2 Node", command=self.toggle_ros, state=tk.NORMAL if ROS2_AVAILABLE else tk.DISABLED)
        self.ros_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        if not ROS2_AVAILABLE:
            tk.Label(ros_bar, text="(rclpy not found)", fg="#dc3545", bg="#e9ecef").pack(side=tk.LEFT)

        # 3. Control Bar (Bottom)
        ctrl = tk.Frame(self.root, bg="#f8f9fa", height=60)
        ctrl.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        # Changed to a label/disabled button for status only
        self.status_btn = tk.Button(ctrl, text="Service Status", width=22, state=tk.DISABLED, disabledforeground="white")
        self.status_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(ctrl, text="Model:", bg="#f8f9fa").pack(side=tk.LEFT, padx=5)
        self.model_combo = ttk.Combobox(ctrl, width=25)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        
        self.gen_btn = tk.Button(ctrl, text="GENERATE / SUBMIT", bg="#28a745", fg="white", width=25, 
                                  font=("Arial", 10, "bold"), command=self.start_generation)
        self.gen_btn.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(ctrl, text="Clear All", width=10, command=self.clear_all).pack(side=tk.RIGHT, padx=10)

        # 4. Main Container (Middle)
        container = tk.Frame(self.root, bg="#f8f9fa")
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)
        container.grid_rowconfigure(0, weight=2)
        container.grid_rowconfigure(1, weight=3)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        f_in = tk.LabelFrame(container, text=" 📝 Input ", bg="white")
        f_in.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.input_text = tk.Text(f_in, undo=True, wrap=tk.WORD, font=("Consolas", 11), borderwidth=0)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.input_text.bind("<<Modified>>", self.on_input_change)

        f_pre = tk.LabelFrame(container, text=" 👁️ Preview ", bg="white")
        f_pre.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.preview_text = scrolledtext.ScrolledText(f_pre, wrap=tk.WORD, font=("Consolas", 11), bg="#f1f3f5", borderwidth=0)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        f_out = tk.LabelFrame(container, text=" 🚀 Output / ROS2 Log ", bg="white")
        f_out.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(f_out, wrap=tk.WORD, font=("Consolas", 11), bg="white", borderwidth=0)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def toggle_ros(self):
        if self.ros_node is None:
            self.start_ros()
        else:
            self.stop_ros()

    def start_ros(self):
        if not ROS2_AVAILABLE: return
        try:
            if not rclpy.ok():
                rclpy.init()
            self.ros_node = LazyConduitNode()
            self.ros_thread = threading.Thread(target=lambda: rclpy.spin(self.ros_node), daemon=True)
            self.ros_thread.start()
            self.ros_status_label.config(text="● ROS2: NODE RUNNING", fg="#28a745")
            self.ros_btn.config(text="Stop ROS2 Node", bg="#dc3545", fg="white")
            self.output_text.insert(tk.END, "[ROS2] Node started. Listening to /lazy_conduit/...\n")
        except Exception as e:
            messagebox.showerror("ROS2 Error", str(e))

    def stop_ros(self):
        if self.ros_node:
            # We don't shutdown rclpy, just destroy the node so we can restart
            self.ros_node.destroy_node()
            self.ros_node = None
            self.ros_status_label.config(text="○ ROS2: STOPPED", fg="#6c757d")
            self.ros_btn.config(text="Launch ROS2 Node", bg="#f8f9fa", fg="black")
            self.output_text.insert(tk.END, "[ROS2] Node stopped.\n")

    # (Previous helper methods like setup_tags, on_input_change, etc. remain same)
    def on_input_change(self, event=None):
        if self.input_text.edit_modified():
            content = self.input_text.get("1.0", tk.END).strip()
            self.input_text.edit_modified(False)

    def periodic_check(self):
        def task():
            self.ollama_online = self.service_manager.is_running()
            self.root.after(0, self.update_status_ui)
            self.root.after(3000, self.periodic_check)
        threading.Thread(target=task, daemon=True).start()

    def update_status_ui(self):
        txt = "● Ollama: RUNNING" if self.ollama_online else "○ Ollama: STOPPED"
        bg = "#28a745" if self.ollama_online else "#dc3545"
        self.status_btn.config(text=txt, bg=bg, fg="white")

    def toggle_ollama(self):
        target = self.service_manager.stop if self.ollama_online else self.service_manager.start
        threading.Thread(target=target, daemon=True).start()

    def refresh_models(self):
        def task():
            try:
                # Use API instead of CLI command for Docker compatibility
                host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                if "://" not in host: host = f"http://{host}"
                
                api_url = f"{host.rstrip('/')}/api/tags"
                import requests
                response = requests.get(api_url, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    models = [m['name'] for m in data.get('models', [])]
                    self.root.after(0, lambda: self.model_combo.config(values=models))
                    if models: self.root.after(0, lambda: self.model_combo.set(models[0]))
            except Exception as e:
                print(f"Failed to fetch models via API: {e}")
                # Fallback
                self.root.after(0, lambda: self.model_combo.config(values=["gemma3:1b", "gemma4:latest"]))
        threading.Thread(target=task, daemon=True).start()

    def start_generation(self):
        prompt = self.input_text.get("1.0", tk.END).strip()
        model = self.model_combo.get()
        if not prompt or not model: return
        self.gen_btn.config(state=tk.DISABLED, text="GENERATING...")
        self.output_text.insert(tk.END, "Thinking... 🧠\n")
        threading.Thread(target=self.run_llm_task, args=(prompt, model), daemon=True).start()

    def run_llm_task(self, prompt, model):
        client = LLMClient(model=f"ollama/{model}")
        response = client.ask(prompt)
        self.root.after(0, lambda: self.finish_gen(response))

    def finish_gen(self, response):
        self.output_text.insert(tk.END, f"\n--- Response ---\n{response}\n")
        self.gen_btn.config(state=tk.NORMAL, text="GENERATE / SUBMIT")

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = LazyConduitGUI(root)
    root.mainloop()
