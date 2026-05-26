# 📊 财务报告 RAG 智能问答系统

基于 **MinerU** 文档解析、**DashScope** 嵌入模型与 LLM、**ChromaDB** 向量数据库构建的财务报告智能问答系统。系统能够自动解析 PDF 格式的财务报告，对内容进行智能分块与向量化存储，并通过检索增强生成（RAG）技术，精准回答用户提出的财务相关问题。

---

## ✨ 主要特性

- **PDF 智能解析**：集成 MinerU 工具，高质量提取文本、表格及结构信息。
- **语义分块策略**：根据标题层级和内容类型（文本/表格）进行自适应分块，支持表格跨块拆分。
- **向量化存储**：使用 DashScope 嵌入模型生成向量，存储于 ChromaDB 持久化数据库中。
- **RAG 问答**：基于检索到的相关文档片段，调用通义千问模型生成专业、准确的回答。
- **增量更新**：支持清除旧数据，重建向量索引。

---

## 🛠️ 环境要求

- Python 3.9+
- 依赖包：见 `requirements.txt`

### 主要依赖库

```text
torch
chromadb
langchain-community
dashscope
mineru[core]
python-dotenv
doclayout-yolo
```

> **注意**：MinerU 需要额外安装其核心依赖，请参考 [MinerU 官方文档](https://github.com/opendatalab/MinerU)。

---

## 📦 安装与配置

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/financial-rag.git
cd financial-rag
```

### 2. 安装依赖

建议使用虚拟环境：

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. 配置 API 密钥

创建 `.env` 文件（或设置系统环境变量）：

```ini
DASHSCOPE_API_KEY=your-dashscope-api-key
EMBEDDING_MODEL=text-embedding-v2   # 可选，默认 text-embedding-v2
```

> 获取 DashScope API 密钥：[阿里云灵积控制台](https://dashscope.console.aliyun.com/)

### 4. 准备 PDF 文件

在项目根目录下创建 `my_pdfs/` 文件夹，放入待分析的财务报告 PDF 文件。

---

## 🚀 使用方法

### 完整工作流示例

```python
from financial_assistant import MinerURAGSystem, RAGQASystem

# 1. 初始化 RAG 系统
rag = MinerURAGSystem(persist_directory="./chroma_db")

# 2. 解析 PDF 文档（自动处理 my_pdfs/ 下的所有 PDF）
processed_files = rag.process_documents(pdf_directory="my_pdfs")

# 3. 分块并准备向量化数据
docs, metas, ids = rag.chunk_and_embed(content_files=processed_files)

# 4. 构建向量数据库
rag.build_vector_store(docs, metas, ids)

# 5. 创建问答系统
qa = RAGQASystem(mineru_rag_system=rag)

# 6. 提问
answer, results = qa.ask_question("2019年度归属于上市公司股东的净利润？")
print(answer)
```

### 直接运行脚本

项目已内置主调用流程，只需将 PDF 放入 `my_pdfs/` 文件夹，然后执行：

```bash
python financial_assistant.py
```

脚本会：
- 自动解析 `my_pdfs/` 下的所有 PDF（若已存在解析结果 JSON，则跳过解析阶段）
- 分块、建库
- 回答预设问题（可修改脚本末尾的 `question` 变量）

---

## 📂 文件结构说明

```
.
├── financial_assistant.py    # 主程序，包含 RAG 系统与问答类
├── my_pdfs/                  # 存放待解析的 PDF 文件
├── processed/                # MinerU 解析输出目录（自动生成）
├── chroma_db/                # ChromaDB 持久化存储目录
├── .env                      # 环境变量（API 密钥等）
└── requirements.txt          # Python 依赖列表
```

---

## 🔧 关键模块说明

### `MinerURAGSystem`

- `process_documents(pdf_directory, output_dir)`: 调用 MinerU 解析 PDF，生成 `*_content_list.json` 文件。
- `chunk_and_embed(content_files, chunk_size=512, overlap=50)`: 读取 JSON 内容，执行智能分块，返回文本块、元数据和 ID。
- `build_vector_store(documents, metadatas, ids)`: 清空原有集合，计算嵌入向量并存入 ChromaDB。
- `query_documents(query_text, n_results=5)`: 检索与问题最相似的文档块。

### `RAGQASystem`

- `generate_answer(question, context)`: 基于检索到的上下文构造 Prompt，调用 DashScope 生成模型回答。
- `ask_question(question)`: 完整问答流程（检索 → 生成）。

---

## 📝 自定义配置

- **分块大小**：修改 `chunk_and_embed` 中的 `chunk_size` 参数（默认 512 字符）。
- **检索数量**：修改 `query_documents` 中的 `n_results` 参数（默认 5）。
- **LLM 模型**：在 `_call_llm` 中修改 `model` 参数，可选 `qwen-turbo`, `qwen-plus`, `qwen-max`。
- **嵌入模型**：通过环境变量 `EMBEDDING_MODEL` 更换（支持 DashScope 系列）。

---

## ⚠️ 注意事项

- 首次运行会自动创建 `processed/` 和 `chroma_db/` 目录。
- 解析 PDF 需要一定的计算资源，大型文档可能耗时较长。
- 若 PDF 中包含复杂表格或图表，MinerU 的提取效果可能受文档质量影响。
- 建议使用 2019 年或之后的财务报告以获得最佳结构解析效果。

---

## 📄 许可证

本项目仅供学习研究使用。使用的第三方工具（MinerU、DashScope、ChromaDB）请遵循其各自许可协议。

---

## 🤝 贡献与反馈

欢迎提交 Issue 或 Pull Request 改进系统功能。

---

**Happy Analyzing! 📈**
