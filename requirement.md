## LazyConduit Requirement

### 1. Overview
LazyConduit 是一個用 Python 寫的，可以在終端機直接執行的資料轉換工具, 主要是用轉換需要提供給 gemma 這種 LLM 所需的 prompt 資料，讓 gemma 更容易理解我們輸入的資料。 Gemma 可處理的資料包括 文字、圖片、聲音、影片等。

很不幸的, 像是 PDF 這種資料, 直接交給 LLM 是沒有辦法的, 所以我们需要先將 PDF 這種資料轉換為文字或者二進制圖片。 同樣的 圖片聲音影音轉為二進制檔案讓 LLM 使用也是必要的。

### 2. Features
- python3 為主要實現的程式
- Prompt 主要以 markdown 基礎語法支援, 像是引用檔案/圖片等. 位置可以採相對位置.
- 支援 pdf、docx、txt、png、jpg、jpeg、mp3、mp4 等格式的轉換。
- 支援將轉換後的資料輸出為單一文件。
- 可設定轉換的品質，例如 pdf 轉換為圖片時，可以設定圖片的解析度等。 audio 轉為 binary 時，可以設定 audio 的頻率等。
- 可設定輸出檔案的格式，例如 pdf 轉換為圖片時，可以設定圖片的格式為 png、jpg、jpeg 等。
- 提供單一或者多個檔案的交叉插入, 讓 Prompt 可以針對多個檔案的邏輯進行處理。
- 可以選擇 LLM 輸入的目標, 像是 ollama 的 gemma, 或者 google 的 gemini 等等。並且支援網路或者本機的 LLM。
- 建立一個 tk based 的界面, 提供編輯, 與基礎預覽界面.

TBD... 持續增加中

### 3. Example

**圖片分析**

```bash
python3 LazyConduit.py --model ollama/gemma:2b "分析以下圖片內有幾隻雞 [檔案描述](./folder/file1.pdf), 請回應我 「總共有 X 隻雞。」"
```

### 4. TODO
- [ ] ollama service start/stop script
- [ ] 一般的 Prompt 輸入界面
- [ ] 模型選擇界面切換
- [ ] TBD....

