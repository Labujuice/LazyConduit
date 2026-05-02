# LazyConduit 🚀

LazyConduit 是一個用 Python 撰寫的資料轉換與 LLM 互動工具。它能自動解析你輸入的 Prompt，將其中引用的檔案轉換為 LLM 可理解的格式，並直接串接 LLM API 取得回應。

LazyConduit is a Python-based data conversion and LLM interaction tool. It automatically parses file references in your prompts, converts them into LLM-compatible formats, and directly communicates with LLM APIs to retrieve responses.

---

## ✨ 核心特色 / Key Features

### 中文 (Traditional Chinese)
- **自動檔案解析**：直接在 Prompt 中使用 `[描述](./路徑/檔案.ext)` 語法，程式會自動讀取並注入資料。
- **多模態支援**：支援將圖片 (PNG, JPG) 自動轉為 Base64 傳送給具備視覺能力的 LLM 模型（如 gemma4）。
- **服務自動管理**：內建腳本可自動管理本地 Ollama 服務的啟動與停止。
- **純文字自動注入**：自動偵測 `.txt` 檔案並將內容直接展開於 Prompt 之中。
- **靈活的 CLI 界面**：支援自訂模型、輸出檔案、轉換品質等參數。

### English
- **Auto-File Parsing**: Use `[desc](path)` syntax directly in prompts to automatically load and inject file data.
- **Multimodal Support**: Automatically converts images (PNG, JPG) to Base64 for multimodal LLMs (e.g., gemma4).
- **Service Management**: Built-in scripts to manage local Ollama service start/stop.
- **Text Auto-Injection**: Detects `.txt` files and expands their content directly into the prompt.
- **Flexible CLI**: Customizable models, output paths, conversion quality, and more.

---

## 🛠️ 安裝與準備 / Installation & Setup

1. **環境需求 / Requirements**:
   - Python 3.10+
   - [Ollama](https://ollama.ai/)

2. **安裝依賴套件 / Install Dependencies**:
   ```bash
   pip install requests
   ```

3. **模型準備 / Pull Models**:
   ```bash
   ollama pull gemma4:latest
   ollama pull gemma3:1b
   ```

---

## 🚀 使用說明 / Usage

### 1. 啟動服務 / Start Service
```bash
bash scripts/ollama_manager.sh start
```

### 2. 執行指令 / Run Commands

**文字總結範例 (Text Summary Example):**
```bash
python3 LazyConduit.py "請幫我總結這份筆記： [我的筆記](./notes.txt)"
```

**圖片分析範例 (Image Analysis Example):**
```bash
python3 LazyConduit.py --model "ollama/gemma4" "分析這張圖片 [小雞](./assets/chicken.png)"
```

---

## 📂 專案結構 / Project Structure
- `LazyConduit.py`: 主程式進入點 / Main entry point.
- `scripts/`: 服務管理腳本 / Service management scripts.
- `utils/`: 核心模組 (解析器、轉換器、LLM 客戶端) / Core modules.
- `assets/`: 測試用媒體檔案 / Test media files.

## 📅 開發進度 / Roadmap
- [x] Phase 1: Ollama 服務管理自動化 / Ollama service automation.
- [x] Phase 2: CLI 核心功能、Markdown 解析、文字/圖片注入 / CLI core, Markdown parsing, Text/Image injection.
- [ ] Phase 2 (In Progress): PDF/DOCX 進階轉換 / Advanced PDF/DOCX conversion.
- [ ] Phase 3: GUI 界面開發 / GUI development.

## 📄 授權條款 / License
本專案採用 [MIT License](LICENSE) 授權。
This project is licensed under the [MIT License](LICENSE).

---
*LazyConduit - 讓資料與 LLM 之間的傳遞變得更懶、更直覺。*
