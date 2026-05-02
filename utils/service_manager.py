import subprocess
import os

class OllamaServiceManager:
    def __init__(self, script_path="scripts/ollama_manager.sh"):
        self.script_path = os.path.abspath(script_path)

    def start(self):
        """Starts the Ollama service."""
        try:
            result = subprocess.run([self.script_path, "start"], capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def stop(self):
        """Stops the Ollama service."""
        try:
            result = subprocess.run([self.script_path, "stop"], capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def is_running(self):
        """Checks if the Ollama service is running."""
        try:
            result = subprocess.run([self.script_path, "status"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

if __name__ == "__main__":
    manager = OllamaServiceManager()
    print(f"Checking status: {'Running' if manager.is_running() else 'Stopped'}")
    
    success, msg = manager.start()
    print(f"Start attempt: {msg}")
    
    print(f"Final status: {'Running' if manager.is_running() else 'Stopped'}")
