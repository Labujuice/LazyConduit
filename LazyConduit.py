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
    parser.add_argument("--quality", type=int, default=100, help="Conversion quality (e.g., DPI for PDF, default: 100).")
    parser.add_argument("--pages", type=str, help="PDF pages to process (e.g., '1-3', '1,3,5', or 'all'. Default: all).")
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
            mime, data = converter.convert(link["abs_path"], pages=args.pages)
            
            # Handle list of images (e.g. multi-page PDF or single image in a list)
            if isinstance(data, list) and not isinstance(data, str):
                images_b64.extend(data)
                if mime == "application/pdf":
                    print(f"[*] 成功轉換 PDF: {link['description']} (共 {len(data)} 頁)")
                    final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"[參照附件圖片：{link['description']} 的 PDF 內容]")
                else:
                    print(f"[*] 成功讀取圖片: {link['description']}")
                    final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"[參照附件圖片：{link['description']}]")
            
            # Handle text content or Error messages
            elif isinstance(data, str):
                if data.startswith("Error"):
                    print(f"[!] {data}")
                    final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", f"[錯誤: {data}]")
                else:
                    # Inject text content directly
                    print(f"[*] 成功讀取文字檔案: {link['description']}")
                    content_block = f"\n--- {link['description']} 內容開始 ---\n{data}\n--- {link['description']} 內容結束 ---\n"
                    final_prompt = final_prompt.replace(f"[{link['description']}]({link['original_path']})", content_block)
            
            else:
                print(f"[!] Warning: 未知格式 {mime}")

    # Add a global hint if images are present
    if images_b64:
        final_prompt = "請根據我提供的文字與附件圖片內容進行分析回覆：\n" + final_prompt

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
