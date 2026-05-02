import requests
import json

class LLMClient:
    def __init__(self, model="ollama/gemma3:1b"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"

    def call_ollama(self, prompt, images=None):
        """Calls local Ollama API."""
        model_name = self.model.replace("ollama/", "")
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        if images:
            payload["images"] = images

        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "No response from model.")
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"

    def call_gemini(self, prompt, parts=None):
        """Placeholder for Gemini API call."""
        return "Gemini integration coming soon..."

    def ask(self, prompt, media=None):
        if self.model.startswith("ollama"):
            # Ollama expects list of base64 images
            return self.call_ollama(prompt, images=media)
        elif self.model.startswith("gemini"):
            return self.call_gemini(prompt, parts=media)
        else:
            return f"Unsupported model source: {self.model}"
