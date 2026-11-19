# STARMIND-055 · Day 55 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 55 / 70 |
| **所属阶段** | 第 5 阶段：第五阶段：模型微调与部署（第 8 周：模型微调、本地推理部署与安全合规） |
| **需求标题** | 本地推理部署（Ollama / vLLM）与高并发压测 —— OpenAI 兼容推理网关、PagedAttention 原理与 TTFT/TPS 异步压测基准工具 |
| **GitLab 分支** | `feat/day55-ollama-vllm-benchmark` |
| **Commit 规范** | `feat(day55): 实现OpenAI兼容推理客户端与TTFT/吞吐量并发压测工具` |
| **配套课件** | `courseware/day55/index.html` |
| **配套 Notebook** | `notebooks/day55/day55_practice.ipynb` |
| **迭代快照** | `versions/day55/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们完成了微调模型的双轨门禁验收、LoRA 无损合并和 AWQ/GGUF 量化方案生成。
- **启下（明日演进）**：明天（Day 56）我们把整个星辰智脑后端 + 推理服务 + 前端用 Docker 多阶段构建、Docker Compose 和 Nginx 反向代理打包上线。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑需要将私有化部署的 Qwen2.5-7B-AWQ 接入企业统一网关，并对不同并发水位（1/5/20 并发）下的响应速度进行量化压测，确保满足产品 SLA（首字延迟 P95 < 1.5s，单卡吞吐 >= 40 tokens/s）。

### 核心痛点
- 开发用 Ollama、生产用 vLLM，如果业务代码硬编码了各自的私有 API，切换成本极高。
- 缺乏统一的并发压测脚本，上线前不知道单张 4090 到底能抗住多少同时在线提问的员工。

### 迭代目标
- 构建遵循 OpenAI `/v1/chat/completions` 规范的统一推理客户端与本地可控延迟流式模拟后端。
- 构建高并发异步压测基准工具（Benchmark Runner），精确采集 TTFT（首字延迟）、TPOT（单 Token 生成耗时）、总耗时 P50/P95 与系统吞吐量（tokens/s）。
- 提供 PagedAttention KV Cache 显存块利用率模拟器，直观对比传统连续分配与分页分配的显存节省。

### 验收标准
- [x] 压测工具支持自定义并发数与请求数，正确计算 TTFT、TPOT、吞吐量与成功率，输出结构化压测报告。
- [x] PagedAttention 模拟器证明在变长请求混合场景下，分页管理将显存碎片浪费从 >80% 降至 <5%。
- [x] 纯本地异步测试 100% 稳定通过，无需外网和 GPU。

### 非功能指标
- 全链路异步 `asyncio` 实现，压测工具自身不成为性能瓶颈。

## 3. 架构设计与交付清单

企业级大模型推理层最关键的架构原则是 **协议解耦（OpenAI API Compatible）**。无论是云端 DeepSeek/通义千问、本地 Ollama（端口 11434）还是生产 vLLM（端口 8000），业务层统一只认 `POST /v1/chat/completions` + `Authorization: Bearer <key>`，通过修改配置中心的 `LLM_BASE_URL` 即可秒级无痛切换。

理解 vLLM 为什么能把吞吐量提升 10~20 倍，核心看两个机制：
1. **PagedAttention（分页注意力）**：传统推理引擎会按 `max_model_len`（如 4096）为每个请求预先分配一块连续 KV Cache 显存，即便用户只生成了 200 个 token，剩下 3896 个位置也白白浪费（内部碎片率高达 60%+）。vLLM 将 KV Cache 切分成固定大小（如 16 tokens/block）的物理块按需分配，通过逻辑块到物理块的页表映射实现非连续存储，并将相同 System Prompt 的前缀块共享（Prefix Caching），碎片率压低到 4% 以下。
2. **Continuous Batching（连续批处理）**：传统静态批处理必须等同一批里最长那条回复吐完才释放整个 Batch，短请求干等；连续批处理在每个迭代步（Iteration）动态插入新请求、剔除已完成请求，GPU 算力始终满载。

衡量推理性能的四大黄金指标：
- **TTFT (Time To First Token)**：用户发出请求到看见第一个字的等待时间，直接决定交互体感（反映 Prefill 阶段压力）。
- **TPOT (Time Per Output Token)**：吐出第一个字之后，平均每个字的生成间隔（反映 Decode 阶段带宽，建议 < 50ms 即 > 20 tokens/s）。
- **E2E Latency**：整条回复完成的总耗时。
- **Throughput (tokens/s)**：系统整体每秒产出的总 Token 数，决定单卡能服务多少并发员工。

### 当日交付代码文件
- `src/day55_paged_attention_sim.py`：步骤一：实现 PagedAttention KV Cache 显存利用率模拟器
- `src/day55_inference_benchmark.py`：步骤二：实现高并发异步推理压测基准工具（TTFT / TPOT / TPS）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
`run_benchmark` 把 `stream_fn` 抽象成可注入的异步生成器非常干净，既方便单测秒过，又方便压真实 vLLM SSE 接口。

### Reviewer：阿杰（Approved）
看懂 PagedAttention 的模拟器后豁然开朗，86% 的显存碎片省下来全给了并发用户，怪不得生产都推 vLLM！

