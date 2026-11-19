# STARMIND-005 · Day 05 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 05 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 1 周：第 1 周：Python 核心语法与数据结构基石） |
| **需求标题** | 核心数据结构（下）——字典与 JSON 重点日 —— 吃透嵌套 dict 与 JSON 序列化，解析星辰智脑模拟大模型 API 完整响应 |
| **GitLab 分支** | `feat/day05-dict-json-api-parser` |
| **Commit 规范** | `feat(day05): 实现嵌套字典安全提取器与大模型JSON响应解析落盘工具` |
| **配套课件** | `courseware/day05/index.html` |
| **配套 Notebook** | `notebooks/day05/day05_practice.ipynb` |
| **迭代快照** | `versions/day05/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们用 list、tuple、set 搞定了待办管理器和知识库标签去重，掌握了序列与集合容器。
- **启下（明日演进）**：明天（Day 6）咱们学习函数封装（默认参数、*args/**kwargs、lambda、递归），把前面五天散落的脚本重构成高内聚的函数式架构。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑即将对接 DeepSeek 与通义千问 API，研发团队需要先构建健壮的 JSON 响应解析与审计落盘层，防止上游字段缺失导致服务崩溃。

### 核心痛点
- 直接用 `resp['choices'][0]['message']['content']` 硬取值，一旦接口限流或返回异常结构立刻触发 KeyError/IndexError。
- 默认 `json.dumps()` 会把中文转义成 `\uXXXX`，运维看日志极度痛苦。
- 缺少统计单次请求 prompt_tokens、completion_tokens 与费用的结构化汇总。

### 迭代目标
- 熟练掌握 dict 增删改查、`.get()`、`.items()`、字典推导式与多层嵌套解析。
- 精通 `json.loads`、`json.dumps`、`json.load`、`json.dump` 四大方法及 `ensure_ascii=False`。
- 实现对模拟大模型 API JSON 响应的安全提取、费用计算与本地文件持久化。

### 验收标准
- [x] 能从标准 OpenAI 兼容 JSON 响应中准确提取回复文本、模型名、结束原因与 Token 用量。
- [x] 面对缺失字段或非法 JSON 字符串时返回兜底错误结构而不抛出未捕获异常。
- [x] 能将解析后的审计记录以可读中文 JSON 写入文件并无损读回，pytest 全绿。

### 非功能指标
- 所有文件读写显式指定 `encoding='utf-8'`。
- 单测使用临时目录 `tmp_path` 验证文件读写，不污染源码仓库。

## 3. 架构设计与交付清单

企业级 AI 网关的响应处理层必须具备「防御性反序列化」能力：
1. **通用安全路径提取器**（day05_dict_utils.py）：封装 `safe_get_path(data, path, default)`，支持按点号和下标（如 `'choices.0.message.content'`）安全穿透多层嵌套 dict/list，任何一层缺失都优雅返回默认值。
2. **LLM JSON 协议解析与持久化层**（day05_json_api_parser.py）：将字符串反序列化（`json.loads`）、核心业务字段抽取、Token 费用归档以及本地审计落盘（`json.dump` / `json.load`）封装为独立函数，确保上游接口轻微变动时业务主流程不崩溃。

### 当日交付代码文件
- `src/day05_dict_utils.py`：步骤一：编写嵌套字典安全路径提取与配置合并工具
- `src/day05_json_api_parser.py`：步骤二：实现大模型 API JSON 响应解析器与本地审计落盘

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
`safe_get_path` 写得很克制清晰，处理上游 `error` 字段和 `JSONDecodeError` 也到位。单测用 `tmp_path` 不污染仓库点赞。

### Reviewer：阿杰 (QA 测试)（Approved）
已确认落盘后的 JSON 文件直接可读中文（无 \u 转义），异常 JSON 也不会抛崩溃。

