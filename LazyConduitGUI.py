import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import threading
import subprocess
import time
from utils.service_manager import OllamaServiceManager
from utils.parser import PromptParser
from utils.converter import FileConverter
from utils.llm_client import LLMClient

class LazyConduitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LazyConduit - Final GUI")
        self.root.geometry("1440x800")
        self.root.configure(bg="#f8f9fa")
        
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.input_file = os.path.join(self.temp_dir, "input_tmp.md")
        self.output_file = os.path.join(self.temp_dir, "output_tmp.md")
        
        self.service_manager = OllamaServiceManager()
        self.parser_tool = PromptParser()
        self.converter = FileConverter()
        
        self.ollama_online = False
        self.setup_ui()
        self.refresh_models()
        self.periodic_check()

    def setup_ui(self):
        # 1. Header (Top)
        header = tk.Frame(self.root, bg="#212529", height=45)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="LazyConduit v1.0", fg="#f8f9fa", bg="#212529", font=("Arial", 12, "bold")).pack(pady=10)

        # 2. Control Bar (Bottom - Pack this BEFORE the main container)
        ctrl = tk.Frame(self.root, bg="#f8f9fa", height=60)
        ctrl.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        self.status_btn = tk.Button(ctrl, text="Service Status", width=22, relief=tk.GROOVE, command=self.toggle_ollama)
        self.status_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(ctrl, text="Model:", bg="#f8f9fa", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.model_combo = ttk.Combobox(ctrl, width=25)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        
        self.gen_btn = tk.Button(ctrl, text="GENERATE / SUBMIT", bg="#28a745", fg="white", width=25, 
                                  font=("Arial", 10, "bold"), command=self.start_generation)
        self.gen_btn.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(ctrl, text="Clear All", width=10, command=self.clear_all).pack(side=tk.RIGHT, padx=10)

        # 3. Main Container (Middle - Will take remaining space)
        container = tk.Frame(self.root, bg="#f8f9fa")
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # Grid Config for container
        container.grid_rowconfigure(0, weight=2) # Top row (Input/Preview)
        container.grid_rowconfigure(1, weight=3) # Bottom row (Output)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # 1. Input Box (Top Left)
        f_in = tk.LabelFrame(container, text=" 📝 Input (Markdown Prompt) ", bg="white", font=("Arial", 10, "bold"))
        f_in.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.input_text = tk.Text(f_in, undo=True, wrap=tk.WORD, font=("Consolas", 11), borderwidth=0)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.input_text.bind("<<Modified>>", self.on_input_change)

        # 2. Preview Box (Top Right)
        f_pre = tk.LabelFrame(container, text=" 👁️ Preview (Styled) ", bg="white", font=("Arial", 10, "bold"))
        f_pre.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.preview_text = scrolledtext.ScrolledText(f_pre, wrap=tk.WORD, font=("Consolas", 11), bg="#f1f3f5", borderwidth=0)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.setup_tags(self.preview_text)

        # 3. Output Box (Bottom Full Width)
        f_out = tk.LabelFrame(container, text=" 🚀 Output (LLM Response) ", bg="white", font=("Arial", 10, "bold"))
        f_out.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.output_text = scrolledtext.ScrolledText(f_out, wrap=tk.WORD, font=("Consolas", 11), bg="white", borderwidth=0)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.setup_tags(self.output_text)

    def setup_tags(self, widget):
        """Stable markdown tagging system."""
        widget.tag_configure("h1", font=("Arial", 14, "bold"), foreground="#0056b3")
        widget.tag_configure("h2", font=("Arial", 12, "bold"), foreground="#17a2b8")
        widget.tag_configure("quote", foreground="#6c757d", background="#f8f9fa", lmargin1=20, lmargin2=20)
        widget.tag_configure("code", background="#e9ecef", font=("Consolas", 10))

    def render_pseudo_markdown(self, widget, content):
        """Thread-safe UI update for markdown content."""
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        for line in content.split("\n"):
            if line.startswith("# "):
                widget.insert(tk.END, line[2:] + "\n", "h1")
            elif line.startswith("## "):
                widget.insert(tk.END, line[3:] + "\n", "h2")
            elif line.startswith("> "):
                widget.insert(tk.END, line[2:] + "\n", "quote")
            elif line.startswith("```"):
                widget.insert(tk.END, line + "\n", "code")
            else:
                widget.insert(tk.END, line + "\n")
        widget.config(state=tk.DISABLED)

    def on_input_change(self, event=None):
        if self.input_text.edit_modified():
            content = self.input_text.get("1.0", tk.END).strip()
            with open(self.input_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.update_preview(content)
            self.input_text.edit_modified(False)

    def update_preview(self, content):
        file_links = self.parser_tool.parse(content)
        md_content = content
        for link in file_links:
            if link["exists"]:
                mime, data = self.converter.convert(link["abs_path"])
                if isinstance(data, list):
                    rep = f"\n> **📎 Attachment:** `{link['description']}` ({len(data)} items)\n"
                else:
                    rep = f"\n> **📄 File Snippet ({link['description']}):**\n> {data[:100]}...\n"
                md_content = md_content.replace(f"[{link['description']}]({link['original_path']})", rep)
        self.render_pseudo_markdown(self.preview_text, md_content)

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.NORMAL); self.preview_text.delete("1.0", tk.END); self.preview_text.config(state=tk.DISABLED)
        self.output_text.config(state=tk.NORMAL); self.output_text.delete("1.0", tk.END); self.output_text.config(state=tk.DISABLED)

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
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                models = [line.split()[0] for line in result.stdout.strip().split("\n")[1:] if line.split()]
                self.root.after(0, lambda: self.model_combo.config(values=models))
                if models: self.root.after(0, lambda: self.model_combo.set(models[0]))
            except: pass
        threading.Thread(target=task, daemon=True).start()

    def start_generation(self):
        prompt = self.input_text.get("1.0", tk.END).strip()
        model = self.model_combo.get()
        if not prompt or not model: return
        self.gen_btn.config(state=tk.DISABLED, text="GENERATING...")
        self.output_text.config(state=tk.NORMAL); self.output_text.delete("1.0", tk.END); self.output_text.insert(tk.END, "Thinking... 🧠\n")
        threading.Thread(target=self.run_llm_task, args=(prompt, model), daemon=True).start()

    def run_llm_task(self, prompt, model):
        file_links = self.parser_tool.parse(prompt)
        images_b64, final_prompt = [], prompt
        for link in file_links:
            if link["exists"]:
                mime, data = self.converter.convert(link["abs_path"])
                if isinstance(data, list): images_b64.extend(data); final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"[Media: {link['description']}]")
                else: final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"\n{data}\n")
        if images_b64: final_prompt = "請分析以下圖片內容：\n" + final_prompt
        
        client = LLMClient(model=f"ollama/{model}")
        response = client.ask(final_prompt, media=images_b64 if images_b64 else None)
        
        with open(self.output_file, "w", encoding="utf-8") as f: f.write(response)
        self.root.after(0, self.finish_gen, response)

    def finish_gen(self, response):
        self.render_pseudo_markdown(self.output_text, response)
        self.gen_btn.config(state=tk.NORMAL, text="GENERATE / SUBMIT")

if __name__ == "__main__":
    root = tk.Tk()
    app = LazyConduitGUI(root)
    root.mainloop()
