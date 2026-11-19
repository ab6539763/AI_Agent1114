# STARMIND-038 · Day 38 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 38 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 6 周：第6周：阶段项目二——企业级知识库问答系统实战与答辩） |
| **需求标题** | 项目二答辩与代码评审：架构讲稿、Code Review评分、压测瓶颈定位与重构实战 —— 第三阶段收官验收：用压测数据说话，攻克并发锁竞争与重复计算瓶颈，把 QPS 拉升 3 倍以上 |
| **GitLab 分支** | `perf/day38-project2-review-benchmark-refactor` |
| **Commit 规范** | `perf(day38): 完成项目二答辩压测工具、LRU语义缓存+倒排剪枝重构优化与Code Review评分器` |
| **配套课件** | `courseware/day38/index.html` |
| **配套 Notebook** | `notebooks/day38/day38_practice.ipynb` |
| **迭代快照** | `versions/day38/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 37）我们完成了 StarMind-KB v2.0 全部功能开发与联调，产品经理林姐体验完直呼丝滑。但今天是阶段项目二正式技术答辩与上线前评审日——架构委员会不仅要看功能演示，更要审查你的**代码质量评分**和**高并发压测 P95/QPS 数据**！
- **启下（明日演进）**：恭喜你圆满通关第三阶段（企业级 RAG 全栈开发）！明天（Day 39）我们将正式开启**第四阶段：AI Agent、工具调用与 LangGraph 状态机**，让星辰智脑从「会查资料的问答助手」进化为「能自主规划、调工具干活的智能体」！

## 2. 业务需求说明 (PRD)

### 业务背景
StarMind-KB v2.0 即将全员发布，需通过技术委员会的 10 分钟架构答辩、GitLab Code Review 量化评审及上线前高并发压力测试（模拟早高峰百人同时查询高频制度问题）。

### 核心痛点
- 初版检索引擎每次查询全量扫描所有切片且无查询缓存，文档规模扩大后 P95 延迟飙升。
- 高并发场景下粗粒度互斥锁导致吞吐量（QPS）被锁死在单核水平。
- 答辩汇报容易沦为「流水账念代码」，缺少面向架构师的量化指标与工程取舍说明。

### 迭代目标
- 构建 `CodeReviewScorer`：从架构分层、检索质量、安全可靠、测试覆盖、性能表现 5 个维度自动计算加权总分、评级（S/A/B/C）与准予上线决策。
- 对照实现 `NaiveSlowKBService`（复现全表扫描+无缓存+粗锁三大瓶颈）与 `OptimizedFastKBService`（倒排索引剪枝 + TTL LRU 缓存 + 无锁读路径重构）。
- 构建并发压测引擎 `run_benchmark`，自动输出优化前后 QPS / P50 / P95 / P99 / 缓存命中率 / 加速比，并生成 10 分钟答辩核心数据简报。

### 验收标准
- [x] `OptimizedFastKBService` 与 `NaiveSlowKBService` 对同一批查询的 Top-1 命中文档 100% 一致（重构绝不改变业务正确性）。
- [x] 多线程并发压测下，`OptimizedFastKBService` 的 QPS 显著高于 `NaiveSlowKBService`（加速比 >= 2.0x），且高频查询触发 LRU 缓存命中。
- [x] `CodeReviewScorer` 能准确识别低分项并阻断不达标 MR 上线。
- [x] 所有 pytest 自动化测试 100% 本地离线通过。

### 非功能指标
- LRU 缓存必须支持 `max_size` 容量淘汰与 `ttl_seconds` 过期失效，并在文档更新时支持一键 `invalidate()` 防止脏读。

## 3. 架构设计与交付清单

后端性能优化的铁律是「**先 Profile 找瓶颈，再重构，最后用压测证明收益且保证结果等价**」：
1. **瓶颈一：全表扫描 -> 倒排索引剪枝（Inverted Index Posting List）**：初版每次查 BM25 都要把全库 $N$ 个切片遍历一遍，复杂度 $O(N \cdot |Q|)$；重构后在入库阶段预建 `term -> {chunk_id: tf}` 倒排表，查询时只遍历包含至少一个查询词的候选切片集合，在大规模知识库中直接剪掉 90% 无关切片！
2. **瓶颈二：重复计算 -> TTL LRU 查询缓存**：企业知识库查询呈现极强的二八定律（20% 高频制度问题占 80% 流量）。引入基于 `OrderedDict` 的线程安全 TTL LRU 缓存，命中缓存直接 $O(1)$ 返回，耗时从毫秒级降至微秒级，同时在文档发生 Upsert/Delete 时立即清空失效缓存保证一致性。
3. **瓶颈三：全局大锁 -> 无锁读路径（Lock-Free Read）**：初版把整个检索过程包在 `threading.Lock()` 里，4 核机器跑出了单核 QPS；重构后将只读倒排索引与预计算文档长度设为不可变快照，仅在读写 LRU 缓存的极短微秒临界区加锁，彻底释放多核并发吞吐！

### 当日交付代码文件
- `src/day38_code_review_and_perf.py`：步骤一：实现 GitLab Code Review 评分器与重构前后双版本检索引擎
- `src/day38_load_test_runner.py`：步骤二：实现多线程并发压测引擎与答辩量化对比报告（day38_load_test_runner.py）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
重构前先写等价性断言 `slow_hits[0][0] == fast_hits[0][0]` 再压测，这才是资深架构师的职业素养！安全维度设置 <70 一票否决也非常符合企业合规要求。

### Reviewer：阿杰（Approved）
P95/P99 分位数和缓存命中率一目了然，这套压测脚本后面第四阶段测 Agent 并发也能直接复用。

