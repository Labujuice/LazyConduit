## LazyConduit Requirement

### 1. Overview
LazyConduit 是一個用 Python 撰寫的資料轉換與 LLM 互動工具。其核心目標是讓使用者能透過簡易的 Markdown 語法 (Prompt) 快速引用各種多媒體檔案 (PDF, 圖片, 音訊, 影片等)，並自動將其轉換為 LLM (如 Ollama/Gemma, Gemini) 可理解的格式（通常為 Binary/Base64 或文字），最後直接呼叫 LLM 取得結果。

### 2. Development Roadmap
開發將分為三個主要階段：
1. **Infrastructure**: 建立 Ollama 服務的自動啟動/停止管理腳本。
2. **CLI Core**: 實作核心 Python 程式，支援解析 Prompt 中的檔案連結、執行資料轉換、呼叫 LLM API，並能將輸出結果儲存至檔案。
3. **GUI Wrapper**: 建立基於 Tkinter 的圖形界面，提供編輯器與預覽功能，並作為 CLI 的操作外殼 (Wrapper)。

### 3. Key Features
- **自動檔案解析 (Auto-Parser)**：
    - 在 Prompt 中使用 Markdown 語法引用檔案：`[檔案描述](相對/絕對路徑)`。
    - 系統自動偵測檔案類型並決定轉換邏輯（例如：PDF 轉圖片、DOCX 轉文字）。
- **支援格式**：
    - 文件：PDF, DOCX, TXT
    - 圖片：PNG, JPG, JPEG
    - 影音：MP3, MP4
- **LLM 整合**：
    - 支援 **Ollama (本地)** 與 **Gemini (雲端)** API。
    - 自動將轉換後的資料與文字 Prompt 封裝，發送給指定的模型。
    - 直接在終端機印出結果，並支援 `--output` 參數儲存至檔案。
- **轉換品質控制**：
    - 內建各類型檔案的預設轉換品質（如 PDF 解析度、音訊頻率）。
    - 支援透過 CLI Arguments (Option Input) 進行即時調整（例如：`--quality 300`）。
- **多檔案交叉插入**：支援在單一 Prompt 中引用多個不同格式的檔案，讓模型進行綜合邏輯處理。

### 4. CLI Usage Example
```bash
# 範例：分析 PDF 內容並將結果存檔
python3 LazyConduit.py \
  --model ollama/gemma3:1b \
  --output result.txt \
  --quality 300 \
  "分析以下圖片內有幾隻雞 [圖片描述](./assets/chicken.pdf)，請回應：總共有 X 隻雞。"
```

### 5. TODO List
- [x] **Phase 1: Service Management**
    - [x] 撰寫 Ollama service start/stop 控制腳本
- [ ] **Phase 2: CLI Core Development**
    - [x] 檔案類型偵測模組 (File Type Detector)
    - [x] 各格式轉換器 (PDF to Image, DOCX to Text, etc.)
    - [x] Prompt 語法解析器 (Markdown Link Parser)
    - [x] LLM API 呼叫整合 (Ollama/Gemini)
    - [ ] CLI 參數處理 (argparse) 與輸出儲存功能
- [ ] **Phase 3: GUI Development**
    - [ ] Tkinter 基礎界面架構
    - [ ] Prompt 編輯區與檔案預覽區
    - [ ] 模型選擇與參數設定界面
    - [ ] GUI 呼叫 CLI 邏輯實作
- [ ] **Phase 4: ros2 rostopic support**
    - [ ] 制定 ros2 rostopic 的資料格式與傳輸協定
    - [ ] 實作 ros2 rostopic 的訊息封裝與解封裝
    - [ ] 實作 parser 結束後串接 LazyConduit 的 LLM API 呼叫
    - [ ] 實作 LazyConduit 的 LLM API 呼叫結果輸出，再封裝成 ros2 rostopic 傳送
    

