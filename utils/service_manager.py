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
        """Check if Ollama service is active via systemd or REST API."""
        # Method 1: Check via network API (Most reliable for Docker/Remote)
        try:
            import requests
            import os
            host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip('/')
            response = requests.get(f"{host}/api/tags", timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass

        # Method 2: Fallback to local process check (Original method)
        try:
            result = subprocess.run(['systemctl', 'is-active', 'ollama'], capture_output=True, text=True)
            return result.stdout.strip() == 'active'
        except:
            return False

if __name__ == "__main__":
    manager = OllamaServiceManager()
    print(f"Checking status: {'Running' if manager.is_running() else 'Stopped'}")
    
    success, msg = manager.start()
    print(f"Start attempt: {msg}")
    
    print(f"Final status: {'Running' if manager.is_running() else 'Stopped'}")
