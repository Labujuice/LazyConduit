import os
import base64
import mimetypes
import io

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None

try:
    from odf import text, teletype
    from odf.opendocument import load
except ImportError:
    load = None

class FileConverter:
    def __init__(self, quality=100):
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
            ".odt": "application/vnd.oasis.opendocument.text",
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

    def convert_pdf_to_images(self, file_path, pages_spec="all"):
        """Converts specified PDF pages to base64 image strings."""
        if not fitz:
            return "Error: pymupdf (fitz) not installed. Please run 'pip install pymupdf'."
        
        try:
            images = []
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Parse pages_spec
            target_pages = []
            if not pages_spec or pages_spec == "all":
                target_pages = list(range(total_pages))
            else:
                try:
                    for part in pages_spec.split(","):
                        if "-" in part:
                            start, end = map(int, part.split("-"))
                            target_pages.extend(range(start-1, end))
                        else:
                            target_pages.append(int(part)-1)
                except Exception:
                    return f"Error: Invalid pages format '{pages_spec}'"

            for p_idx in target_pages:
                if 0 <= p_idx < total_pages:
                    page = doc[p_idx]
                    zoom = self.quality / 72
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    images.append(base64.b64encode(img_data).decode("utf-8"))
            
            doc.close()
            return images
        except Exception as e:
            return f"Error converting PDF: {str(e)}"

    def convert_docx_to_text(self, file_path):
        """Extracts text from a DOCX file."""
        if not Document:
            return "Error: python-docx not installed. Please run 'pip install python-docx'."
        
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error converting DOCX: {str(e)}"

    def convert_odt_to_text(self, file_path):
        """Extracts text from an ODT file."""
        if not load:
            return "Error: odfpy not installed. Please run 'pip install odfpy'."
        
        try:
            textdoc = load(file_path)
            all_text = []
            paragraphs = textdoc.getElementsByType(text.P)
            for p in paragraphs:
                all_text.append(teletype.extractText(p))
            return "\n".join(all_text)
        except Exception as e:
            return f"Error converting ODT: {str(e)}"

    def convert(self, file_path, pages="all"):
        """
        Main conversion logic.
        """
        if not os.path.exists(file_path):
            return None, f"Error: File not found: {file_path}"

        mime_type = self.detect_type(file_path)
        
        # 1. Handle PDF
        if mime_type == "application/pdf":
            data = self.convert_pdf_to_images(file_path, pages_spec=pages)
            if isinstance(data, str) and data.startswith("Error"):
                return "text/plain", data
            return mime_type, data
        
        # 2. Handle DOCX
        if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or file_path.endswith(".docx"):
            data = self.convert_docx_to_text(file_path)
            return "text/plain", data

        # 3. Handle ODT
        if mime_type == "application/vnd.oasis.opendocument.text" or file_path.endswith(".odt"):
            data = self.convert_odt_to_text(file_path)
            return "text/plain", data

        # 4. Handle Text
        if mime_type == "text/plain":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return mime_type, f.read()
        
        # 5. Handle Images (Return as list for consistency)
        if mime_type.startswith("image/"):
            return mime_type, [self.to_base64(file_path)]
        
        # Default: Don't treat as image if it's not recognized
        return "text/plain", f"Error: Unsupported file format '{mime_type}' for {file_path}"

if __name__ == "__main__":
    converter = FileConverter()
    print(f"Type of test.pdf: {converter.detect_type('test.pdf')}")
