# STARMIND-010 · Day 10 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 10 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 模块、包与异常处理 —— 搭建星辰智脑自定义异常体系、模块化包结构与 venv / requirements.txt 工程规范 |
| **GitLab 分支** | `feat/day10-modules-exceptions-venv` |
| **Commit 规范** | `feat(day10): 构建StarMind自定义异常层级、降级容错执行器与依赖清单校验工具` |
| **配套课件** | `courseware/day10/index.html` |
| **配套 Notebook** | `notebooks/day10/day10_practice.ipynb` |
| **迭代快照** | `versions/day10/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们用继承和多态搭出了多模型适配层，但目前还没处理调用超时、限流、密钥无效等生产异常。
- **启下（明日演进）**：明天（Day 11）咱们学习文件操作（txt/csv/json）与 os/pathlib/datetime/re 常用标准库，给星辰智脑打造批量文档读取与关键词统计工具。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑接入多模型后，生产环境频繁面临上游 429 限流、401 密钥失效、输入超长等故障，需要统一的自定义异常体系、优雅降级机制与标准化依赖隔离方案。

### 核心痛点
- 所有错误都抛出泛化的 `Exception`，调用方无法区分该重试、该切模型还是该立即报警。
- 裸 `except Exception: pass` 掩盖了真实故障根因。
- 团队成员全局 pip 装包互相打架，缺少 `venv` 与 `requirements.txt` 规范检查。

### 迭代目标
- 掌握 `import` 搜索路径、包结构（`__init__.py`）、`venv` 虚拟环境与 `requirements.txt` 管理。
- 熟练运用 `try / except / else / finally` 与 `raise ... from exc` 异常链保留原始堆栈。
- 设计 `StarMindError` 自定义异常层级并实现主备模型自动降级执行器。

### 验收标准
- [x] 自定义异常树包含 `StarMindError` 基类及 `AuthError`、`RateLimitError`、`ModelTimeoutError` 子类，携带 `error_code` 与 `retryable` 标记。
- [x] 容错执行器在主模型抛出 `RateLimitError` 时自动无缝切换至备用模型；遇到 `AuthError` 时立即向上抛出不盲目降级。
- [x] 依赖清单解析工具能校验 `requirements.txt` 是否锁定版本号，pytest 全绿。

### 非功能指标
- 严禁使用裸 `except:`，所有异常流转均有结构化日志记录。
- 完整保留异常上下文链，便于排查根因。

## 3. 架构设计与交付清单

在大厂微服务与 AI 网关架构中，异常不是「程序崩了」，而是「受控的业务控制流协议」：
1. **分层异常体系（day10_exceptions.py）**：所有业务异常继承自 `StarMindError`，并内置 `code`（如 `E429`、`E401`）和 `retryable: bool` 元数据。上游框架只需要检查 `exc.retryable`，就能决定走降级重试还是直接熔断告警。
2. **主备降级与依赖审计层（day10_resilient_runner.py）**：利用 `try / except / else / finally` 实现主模型调用、限流/超时自动切备用模型、审计收尾；附带 `audit_requirements_text` 帮团队在 CI 阶段拦截未锁版本的 `requirements.txt`。

### 当日交付代码文件
- `src/day10_exceptions.py`：步骤一：构建星辰智脑自定义异常体系
- `src/day10_resilient_runner.py`：步骤二：实现主备模型容错降级器与 requirements.txt 审计工具

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
异常捕获先子类 AuthError 再父类 StarMindError，结构非常严谨；`raise ... from` 保留根因链也很到位。

### Reviewer：阿杰 (QA 测试)（Approved）
4 组故障注入用例（正常、429 降级、504 降级、401 快速失败）全部通过。

