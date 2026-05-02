import os
import base64
import mimetypes

class FileConverter:
    def __init__(self, quality=150):
        self.quality = quality

    def detect_type(self, file_path):
        """Detects the file type based on extension or mime type."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        
        ext = os.path.splitext(file_path)[1].lower()
        mapping = {
            ".pdf": "application/pdf",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".mp3": "audio/mpeg",
            ".mp4": "video/mp4"
        }
        return mapping.get(ext, "application/octet-stream")

    def to_base64(self, file_path):
        """Converts file content to base64 string."""
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def convert(self, file_path):
        """
        Main conversion logic. 
        For Phase 2 initial implementation, we'll return mime_type and base64/text.
        """
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"

        mime_type = self.detect_type(file_path)
        
        # Simple text handling
        if mime_type == "text/plain":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return mime_type, f.read()
        
        # Others to base64 (Standard for Ollama/Gemini multimodal)
        # Note: PDF might need special treatment (convert to images) in a later update
        return mime_type, self.to_base64(file_path)

if __name__ == "__main__":
    converter = FileConverter()
    # Dummy test
    print(f"Type of test.pdf: {converter.detect_type('test.pdf')}")
    print(f"Type of photo.jpg: {converter.detect_type('photo.jpg')}")
