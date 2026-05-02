# LazyConduit 🚀

LazyConduit 是一個用 Python 撰寫的資料轉換與 LLM 互動工具。它能自動解析你輸入的 Prompt，將其中引用的檔案（如圖片、文字檔、PDF 等）轉換為 LLM 可理解的格式，並直接串接 Ollama 或 Gemini 等 API 取得回應。

## ✨ 核心特色

- **自動檔案解析 (Auto-Injection)**：直接在 Prompt 中使用 `[描述](./路徑/檔案.ext)` 語法，程式會自動讀取並注入資料。
- **多模態支援 (Multimodal)**：支援將圖片 (PNG, JPG) 自動轉為 Base64 傳送給具備視覺能力的 LLM 模型（如 gemma4）。
- **服務自動化管理**：內建腳本可自動管理本地 Ollama 服務的啟動與停止。
- **純文字自動注入**：自動偵測 `.txt` 檔案並將內容直接展開於 Prompt 之中。
- **靈活的 CLI 界面**：支援自訂模型、輸出檔案、轉換品質等參數。

## 🛠️ 安裝與準備

1. **環境需求**：
   - Python 3.10+
   - 已安裝 [Ollama](https://ollama.ai/)

2. **安裝依賴套件**：
   ```bash
   pip install requests
   ```

3. **模型準備**：
   確保你已經下載了需要的模型，例如：
   ```bash
   ollama pull gemma4:latest
   ollama pull gemma3:1b
   ```

## 🚀 使用說明

### 1. 啟動服務
你可以使用內建腳本來管理 Ollama 服務：
```bash
bash scripts/ollama_manager.sh start
```

### 2. 執行轉換與分析
你可以直接在命令列輸入 Prompt，並引用檔案：

**文字總結範例：**
```bash
python3 LazyConduit.py "請幫我總結這份筆記： [我的筆記](./notes.txt)"
```

**圖片分析範例：**
```bash
python3 LazyConduit.py --model "ollama/gemma4" "分析這張圖片 [小雞](./assets/chicken.png)"
```

### 3. 進階參數
- `--model`: 指定使用的模型 (預設: `ollama/gemma3:1b`)
- `--output`: 將 LLM 的回應存檔 (例如: `--output result.txt`)
- `--quality`: 設定轉換品質 (例如 PDF 解析度)
- `--no-service-check`: 跳過 Ollama 服務檢查

## 📂 專案結構
- `LazyConduit.py`: 主程式進入點。
- `scripts/`: 包含服務管理腳本。
- `utils/`: 核心邏輯模組 (解析器、轉換器、LLM 客戶端)。
- `assets/`: 存放測試用的多媒體檔案。

## 📅 開發進度 (Roadmap)
- [x] Phase 1: Ollama 服務管理自動化
- [x] Phase 2: CLI 核心功能、Markdown 解析、文字/圖片注入
- [ ] Phase 2 (進行中): PDF/DOCX 進階轉換邏輯
- [ ] Phase 3: Tkinter GUI 界面開發

---
*LazyConduit - 讓資料與 LLM 之間的傳遞變得更懶、更直覺。*
