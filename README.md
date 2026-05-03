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
   pip install requests pymupdf python-docx odfpy
   ```

3. **模型準備 / Pull Models**:
   ```bash
   ollama pull gemma4:latest
   ollama pull gemma4:e2b
   ollama pull gemma3:1b
   ```

---

## 🚀 使用說明 / Usage
## 🚀 使用方式 / Usage

### 1. 啟動服務 / Start Service
```bash
bash scripts/ollama_manager.sh start
```

### 2. 執行指令 / Run Commands

### 圖形界面模式 (GUI Mode)
如果你偏好使用視窗界面，可以使用以下指令啟動：
```bash
python3 LazyConduitGUI.py
```
**功能特色 / Features:**
- **三欄式佈局**：同時具備 Prompt 輸入、即時預覽 (Markdown 著色)、以及 LLM 回應區域。
- **自動儲存**：輸入內容會即時存檔至 `temp/input_tmp.md`，輸出結果存至 `temp/output_tmp.md`。
- **服務管理**：內建 Ollama 服務狀態切換按鈕，無需切換至終端機。
- **模型管理**：自動列出已安裝模型，並支援手動輸入下載。

---

### 終端機模式 (CLI Mode)
**文字總結範例 (Text Summary Example):**
```bash
python3 LazyConduit.py "請幫我總結這份筆記： [我的筆記](./assets/notes.txt)"
```

**圖片分析範例 (Image Analysis Example):**
```bash
python3 LazyConduit.py --model "ollama/gemma4" "分析這張圖片 [小雞](./assets/chicken.png)"
```

**PDF 分析範例 (PDF Analysis Example):**
```bash
python3 LazyConduit.py --model "ollama/gemma4" --pages "1" "請總結這份文件的第一頁內容： [文件](./assets/3 Body Problem.pdf)"
```

**PDF 多頁分析範例 (PDF Multi-Page Analysis Example):**
```bash
python3 LazyConduit.py --model "ollama/gemma4" --pages "1,2,3" "請總結這份文件的第一、二、三頁內容： [文件](./assets/3 Body Problem.pdf)"
```

**docx/odt 轉換範例 (Document Conversion Example):**
```bash
# 支援 .docx 與 .odt
python3 LazyConduit.py --model "ollama/gemma4" "請總結這份文件的內容： [文件](./assets/3 body problem.docx)"
```
---

## 📂 專案結構 / Project Structure
- `LazyConduit.py`: CLI 主程式 / CLI entry point.
- `LazyConduitGUI.py`: GUI 主程式 / GUI entry point.
- `scripts/`: 服務管理腳本 / Service management scripts.
- `utils/`: 核心模組 (解析器、轉換器、LLM 客戶端) / Core modules.
- `temp/`: GUI 暫存目錄 / GUI temporary files.

## 📅 開發進度 / Roadmap
- [x] Phase 1: Ollama 服務管理自動化 / Ollama service automation.
- [x] Phase 2: CLI 核心功能、Markdown 解析、文字/圖片注入 / CLI core, Markdown parsing, Text/Image injection.
- [x] Phase 3: GUI 界面開發 / GUI development.
- [ ] Phase 4: ROS2 rostopic 支援 / ROS2 rostopic support.

## 📄 授權條款 / License
本專案採用 [MIT License](LICENSE) 授權。
This project is licensed under the [MIT License](LICENSE).

---
*LazyConduit - 讓資料與 LLM 之間的傳遞變得更懶、更直覺。*
