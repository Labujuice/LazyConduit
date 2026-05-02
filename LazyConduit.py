import argparse
import sys
import os
from utils.service_manager import OllamaServiceManager

def main():
    parser = argparse.ArgumentParser(description="LazyConduit: Data conversion and LLM interaction tool.")
    
    # Required arguments
    parser.add_argument("prompt", type=str, help="The prompt to send to the LLM, can include [desc](path) for files.")
    
    # Optional arguments
    parser.add_argument("--model", type=str, default="ollama/gemma3:1b", help="The LLM model to use (default: ollama/gemma3:1b).")
    parser.add_argument("--output", type=str, help="Path to save the LLM response.")
    parser.add_argument("--quality", type=int, default=150, help="Conversion quality (e.g., DPI for PDF, default: 150).")
    parser.add_argument("--no-service-check", action="store_true", help="Skip checking if Ollama service is running.")

    args = parser.parse_args()

    # Phase 1 integration: Service Check
    if not args.no_service_check and args.model.startswith("ollama"):
        manager = OllamaServiceManager()
        if not manager.is_running():
            print("Error: Ollama service is not running. Please start it using 'scripts/ollama_manager.sh start'.")
            sys.exit(1)

    print(f"[*] Target Model: {args.model}")
    print(f"[*] Prompt: {args.prompt}")
    if args.output:
        print(f"[*] Output File: {args.output}")
    print(f"[*] Quality: {args.quality}")

    # --- Phase 2 logic start ---
    from utils.parser import PromptParser
    from utils.converter import FileConverter
    from utils.llm_client import LLMClient

    # 1. Parse Prompt
    parser_tool = PromptParser()
    file_links = parser_tool.parse(args.prompt)
    
    # 2. Convert Files
    converter = FileConverter(quality=args.quality)
    images_b64 = []
    final_prompt = args.prompt
    
    for link in file_links:
        if link["exists"]:
            mime, data = converter.convert(link["abs_path"])
            if mime.startswith("image"):
                images_b64.append(data)
                # Remove the link from text to avoid confusion, or keep it as description
                final_prompt = final_prompt.replace(link["original_path"], f"[Image: {link['description']}]")
            elif mime == "text/plain":
                # Inject text content directly
                content_block = f"\n--- Start of {link['description']} ---\n{data}\n--- End of {link['description']} ---\n"
                final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", content_block)
            else:
                print(f"[!] Warning: File type {mime} not fully supported in this version. Sending as binary if possible.")
                images_b64.append(data)

    # 3. Call LLM
    print("\n[*] Sending request to LLM...")
    client = LLMClient(model=args.model)
    response = client.ask(final_prompt, media=images_b64 if images_b64 else None)

    # 4. Handle Output
    print("\n--- LLM Response ---")
    print(response)
    print("--------------------")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(response)
        print(f"[*] Response saved to {args.output}")

if __name__ == "__main__":
    main()
