# LazyConduit 🚀

LazyConduit 是一個用 Python 撰寫的資料轉換、LLM 互動與 **ROS2 機器人整合** 工具。它能自動解析 Prompt 中的檔案引用，轉換為 LLM 可理解格式，並透過標準 GUI 或 ROS2 Topic 進行跨平台通訊。

LazyConduit is a Python-based tool for data conversion, LLM interaction, and **ROS2 robotics integration**. It automatically parses file references in prompts, converts them into LLM-compatible formats, and supports communication via standard GUI or ROS2 Topics.

---

## ✨ 核心特色 / Key Features

### 中文 (Traditional Chinese)
- **🤖 ROS2 深度整合**：提供 `LazyConduitNode`，支援透過 Topic 遠端觸發 LLM 任務，並具備 JSON 序號追蹤與耗時監控。
- **📝 自動檔案解析**：直接在 Prompt 中使用 `[描述](./路徑/檔案.ext)` 語法，程式會自動讀取並注入資料。
- **👁️ 多模態支援**：透過 `cv_bridge` 整合，支援 `sensor_msgs/Image` 直接進行視覺分析。
- **🔌 靈活的雙介面**：具備文件工作流專用的 GUI 與 ROS2 偵錯專用的 Debug Console。
- **🐳 Docker 一鍵部署**：內建完整 ROS2 環境，支援與宿主機 Ollama 服務無縫串接。

### English
- **🤖 ROS2 Deep Integration**: Provides `LazyConduitNode` supporting remote LLM tasks via Topics, featuring JSON sequence tracking and duration monitoring.
- **📝 Auto-File Parsing**: Use `[desc](path)` syntax directly in prompts to automatically load and inject file data.
- **👁️ Multimodal Support**: Integrated with `cv_bridge` to support vision analysis directly via `sensor_msgs/Image`.
- **🔌 Flexible Dual Interface**: Includes a Document Workflow GUI and a dedicated ROS2 Debug Console.
- **🐳 Docker One-Key Deployment**: Built-in ROS2 environment with seamless connection to host-side Ollama services.

---

## 🐳 Docker 快速啟動 / Docker Quick Start

我們提供完整的環境，確保 ROS2 與所有依賴套件開箱即用：
We provide a full environment to ensure ROS2 and all dependencies work out of the box:

```bash
# 啟動環境 (自動處理網路與掛載) / Start environment (Auto networking & mounting)
bash docker_run.sh
```

---

## 🚀 使用說明 / Usage

### 🎮 ROS2 偵錯模式 / ROS2 Debug Mode
執行專用的偵錯控制台進行節點測試：
Run the dedicated debug console for node testing:
```bash
python3 LazyConduitGUI_ROS2.py
```
- **Launch Node**: 啟動背景節點並監控 `/lazy_conduit/output`。 / Starts the background node and monitors output.
- **Monitor**: 自動解析 JSON 回傳，顯示耗時與序號。 / Auto-parses JSON response to show duration and index.

### 📄 文件工作流模式 / Document Workflow Mode
執行標準 GUI 進行筆記與文件整理：
Run the standard GUI for note-taking and document organization:
```bash
python3 LazyConduitGUI.py
```

---

## 📡 ROS2 Topic 協定 / Communication Protocol

### 📥 訂閱 / Subscriptions
- `/lazy_conduit/text_input` (`std_msgs/String`)
- `/lazy_conduit/vision_input` (`sensor_msgs/Image`)
- `/lazy_conduit/vision_prompt` (`std_msgs/String`)

### 📤 發布 / Publications
- `/lazy_conduit/output` (`std_msgs/String`):
  回傳 JSON 格式結果，方便外部程式串接解析。
  Returns JSON formatted results for easy integration.
  ```json
  {
    "index": 1,
    "duration": 3.42,
    "model": "ollama/gemma3:1b",
    "content": "..."
  }
  ```

---

## 📅 開發進度 / Roadmap
- [x] Phase 1: Ollama 服務管理自動化 / Ollama service automation.
- [x] Phase 2: CLI 核心、Markdown 解析 / CLI core, Markdown parsing.
- [x] Phase 3: GUI 介面開發 / GUI development.
- [x] Phase 4: ROS2 深度整合 / ROS2 integration.

## 📄 授權條款 / License
本專案採用 [MIT License](LICENSE) 授權。
This project is licensed under the [MIT License](LICENSE).
