# STARMIND-028 · Day 28 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 28 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 4 周：第4周：LangChain 核心架构与 RAG 文档预处理） |
| **需求标题** | 文档加载与分割(RAG第一步)：多格式解析器与中文递归分块调优 —— Garbage In, Garbage Out！攻克企业多格式文档清洗与中文语义无损切分 |
| **GitLab 分支** | `feat/day28-rag-loaders-chinese-splitter` |
| **Commit 规范** | `feat(day28): 实现多格式文档加载器与中文RecursiveCharacterTextSplitter分块实验` |
| **配套课件** | `courseware/day28/index.html` |
| **配套 Notebook** | `notebooks/day28/day28_practice.ipynb` |
| **迭代快照** | `versions/day28/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 27）我们搞定了多轮会话记忆与 SQLite 持久化，星辰智脑已经能记住员工上下文了。但现在它还是个「空壳子」——公司内网散落着几千份 Markdown 技术文档、HTML 公告、CSV 薪资/资产表、PDF 员工手册和 Word 制度文件，大模型压根没读过。
- **启下（明日演进）**：明天（Day 29）我们将把今天切好的高质量文本块（Chunks）向量化，深入 HNSW 近似最近邻检索原理，亲手搭建支持元数据过滤的本地持久化向量数据库！

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科知识库首批需要接入 5 类企业异构文档：研发 Markdown 规范、内网 HTML 公告、IT 资产/排班 CSV 表格、HR PDF 员工手册与法务 Word 合同模板。

### 核心痛点
- HTML 充满导航栏 `<script>`/`<style>` 噪音标签，直接入库严重污染检索结果。
- 直接按固定字数硬切会把中文句子和制度条款截断，导致语义支离破碎。
- 切片缺少来源文件名、章节标题、切片序号等元数据，后续无法向员工展示可信引用来源。

### 迭代目标
- 定义统一的 `Document(page_content, metadata)` 数据结构，与 LangChain `langchain_core.documents.Document` 对齐。
- 实现 Markdown、HTML、CSV、纯文本及结构化 PDF/Word 加载器，自动清洗噪音并提取丰富元数据。
- 实现中文增强版 `RecursiveCharacterTextSplitter`，并开展不同 `chunk_size` / `chunk_overlap` 参数组合的断句完整度与冗余率实验。

### 验收标准
- [x] HTML 加载器能彻底剥离 `<script>`/`<style>` 与 HTML 标签，仅保留干净正文；Markdown 加载器能提取 `#` 标题层级。
- [x] 中文递归分块器严格遵守 `len(chunk) <= chunk_size`（除非单个原子片段超长），且相邻分块正确保留 overlap 上下文。
- [x] 分块调优实验能输出量化对比表，所有 pytest 单元测试 100% 通过。

### 非功能指标
- 解析 100KB 中文文档并完成分块耗时 < 50ms。
- 零重型外部依赖（不强依赖 poppler/libreoffice 二进制），并在笔记中给出生产级 `pypdf`/`python-docx`/`unstructured` 接入对照。

## 3. 架构设计与交付清单

企业级文档入库流水线（Ingestion Pipeline）的第一阶段是 **Extract -> Clean -> Split -> Enrich**：
1. **Extract（多格式提取）**：不同格式走专用 Loader，统一归一化为 `List[Document]`。特别地，`.docx` 本质上是一个 ZIP 压缩包，里面 `word/document.xml` 存着所有段落 XML，用 Python 标准库 `zipfile + xml.etree.ElementTree` 甚至不需要装第三方库就能无损解析真实 Word 文件！
2. **Clean（噪音清洗）**：去除 HTML 的 `<script>`/`<style>`、压缩连续空白行、剔除页眉页脚（如「杭州星辰数科内部机密 第X页」），防止噪音拉低 Embedding 质量。
3. **Split（中文递归分块）**：`RecursiveCharacterTextSplitter` 的精髓在于「优先按大语义边界切，实在切不动再降级按小边界切」：先试双换行（段落），再试单换行，再试中文句号/感叹号/问号，最后才退化到逗号或字符硬切；合并相邻小段时精确控制 `chunk_size` 与 `chunk_overlap`。
4. **Enrich（元数据增强）**：为每个切片自动写入 `source`、`doc_type`、`section_title`、`chunk_index`、`total_chunks`、`start_index`，为明天向量库的 `where` 过滤和后天的引用溯源打好基础。

### 当日交付代码文件
- `src/day28_loaders.py`：步骤一：实现统一 Document 模型与多格式企业文档加载器
- `src/day28_text_splitter.py`：步骤二：实现中文 RecursiveCharacterTextSplitter 与分块参数调优实验

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
保留句末标点在上一块结尾这个细节非常到位！另外 `split_documents` 里不要忘记对 `chunk_overlap >= chunk_size` 做参数防御，否则合并循环可能死循环。

### Reviewer：林产品（Approved）
财务部导出的报销标准表是 CSV 格式，能不能保证检索时别丢了列名？

