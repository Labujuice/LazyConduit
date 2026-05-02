import re
import os

class PromptParser:
    def __init__(self):
        # Regex to match [description](path)
        self.pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    def parse(self, prompt):
        """
        Parses the prompt and returns a list of dictionaries containing
        description and absolute file path for each match.
        """
        matches = self.pattern.findall(prompt)
        files = []
        for desc, path in matches:
            # Resolve to absolute path relative to current working directory
            # but you might want to handle it differently later
            abs_path = os.path.abspath(path)
            files.append({
                "description": desc,
                "original_path": path,
                "abs_path": abs_path,
                "exists": os.path.exists(abs_path)
            })
        return files

if __name__ == "__main__":
    parser = PromptParser()
    test_prompt = "請分析 [這張圖](./assets/img.png) 還有 [這份文件](/tmp/doc.pdf)"
    results = parser.parse(test_prompt)
    for r in results:
        print(f"Found: {r['description']} -> {r['abs_path']} (Exists: {r['exists']})")
