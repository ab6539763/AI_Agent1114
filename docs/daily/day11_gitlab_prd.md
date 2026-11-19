# STARMIND-011 · Day 11 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 11 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 文件操作与常用标准库 —— 精通 pathlib/csv/json/datetime/re，打造星辰知识库批量文档扫描与关键词统计引擎 |
| **GitLab 分支** | `feat/day11-files-stdlib-kb-scanner` |
| **Commit 规范** | `feat(day11): 实现基于pathlib/re/csv/datetime的批量文档读取与关键词统计导出工具` |
| **配套课件** | `courseware/day11/index.html` |
| **配套 Notebook** | `notebooks/day11/day11_practice.ipynb` |
| **迭代快照** | `versions/day11/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们搭好了 StarMind 自定义异常体系和主备容错调度器，工程骨架已经立起来了。
- **启下（明日演进）**：明天（Day 12）激动人心的时刻到了——咱们学习 HTTP 协议与 API 调用，亲手对接 DeepSeek / 通义千问协议写出第一版命令行 AI 问答小程序！

## 2. 业务需求说明 (PRD)

### 业务背景
在搭建 RAG 知识库前，运营与算法团队需要对存量散落的本地 Markdown/TXT 文档进行批量内容扫描、敏感信息抽检与高频业务词统计，并生成可供 Excel 打开的 CSV 统计表。

### 核心痛点
- 人工逐个打开几十份文档统计关键词效率极低且易漏。
- Windows 与 Linux 路径分隔符不一致（`\` vs `/`），硬编码路径跨平台必挂。
- 缺少使用正则表达式批量抽取文档中隐藏的手机号、邮箱与工单编号的能力。

### 迭代目标
- 掌握 `with open(..., encoding='utf-8')`、`pathlib.Path` 跨平台目录遍历与文件读写。
- 熟练使用 `csv.DictWriter/DictReader`、`datetime` 时间戳格式化与 `re` 正则表达式。
- 交付批量文档扫描、关键词频次统计、实体抽取与 CSV/JSON 双格式报表导出工具。

### 验收标准
- [x] 能递归扫描指定目录下所有 `.txt` / `.md` 文件并正确统计字符数与指定关键词命中次数。
- [x] 能用正则准确提取文档中出现的邮箱地址与 `STARMIND-xxx` 工单号。
- [x] 能将统计结果无乱码导出为 CSV 与 JSON 报告，并在隔离 `tmp_path` 下通过 pytest。

### 非功能指标
- 全流程使用 `pathlib.Path` 保证 Windows/macOS/Linux 跨平台一致。
- CSV 写出使用 `newline=''` 防止 Windows 出现多余空行。

## 3. 架构设计与交付清单

本模块是后续第三阶段 RAG「文档加载器（Document Loader）」的直接前身，采用清晰的两段式流水线：
1. **正则实体抽取与文本分析器（day11_regex_extractor.py）**：预编译（`re.compile`）常用业务正则表达式（邮箱、工单号、中国大陆手机号），提供高性能的单文档统计与实体提取纯函数。
2. **批量目录扫描与报表导出器（day11_doc_scanner.py）**：基于 `pathlib.Path.rglob('*')` 递归发现目标扩展名文件，逐个调用分析器收集指标，打上 `datetime` 生成时间，分别写入 `.csv`（含 `newline=''`）和 `.json` 报表。

### 当日交付代码文件
- `src/day11_regex_extractor.py`：步骤一：编写预编译正则实体抽取与关键词频次分析器
- `src/day11_doc_scanner.py`：步骤二：实现批量文档递归扫描器与 CSV / JSON 双格式报表导出

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
全线采用 `pathlib` + `utf-8-sig` + `newline=''`，还贴心过滤掉了 `.bin` 二进制杂文件，可以直接复用进后面的 RAG 导入器。

### Reviewer：林产品 (PM)（Approved）
导出的 CSV 用 Excel 双击直接打开中文完美显示，工单号和邮箱也全抓出来了！

