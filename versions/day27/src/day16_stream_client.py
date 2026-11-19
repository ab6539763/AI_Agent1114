"""
StarMind Day 16 - 步骤二：多角色对话协议、stream=True 流式打字机与参数对比实验
"""

import time
from dataclasses import dataclass
from typing import Dict, Generator, List

from src.day16_sampling_simulator import GenerationConfig, SCENE_PRESETS


VALID_ROLES = {"system", "user", "assistant"}


@dataclass
class StreamChunk:
    """模拟 OpenAI ChatCompletionChunk 增量结构。"""
    chunk_index: int
    delta_content: str
    finish_reason: str | None = None
    elapsed_ms: float = 0.0


@dataclass
class ExperimentResult:
    """单组参数对比实验汇总。"""
    profile_name: str
    temperature: float
    max_tokens: int
    output_text: str
    chunk_count: int
    ttft_ms: float
    total_ms: float
    finish_reason: str


class StarMindStreamClient:
    """
    星辰智脑离线/仿真流式对话客户端。
    完整遵循 system/user/assistant 协议与 stream=True 增量输出语义。
    """

    def validate_messages(self, messages: List[Dict[str, str]]) -> None:
        """校验对话消息列表是否符合标准角色协议。"""
        if not messages:
            raise ValueError("messages 不能为空")
        for idx, msg in enumerate(messages):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role not in VALID_ROLES:
                raise ValueError(f"第 {idx} 条消息角色非法: {role}，仅允许 {VALID_ROLES}")
            if not isinstance(content, str) or not content.strip():
                raise ValueError(f"第 {idx} 条消息 content 不能为空")
            if role == "system" and idx != 0:
                raise ValueError("安全规范：system 角色仅允许出现在消息列表首位（index=0）")

    def _synthesize_reply(self, messages: List[Dict[str, str]], config: GenerationConfig) -> str:
        """根据角色指令和温度参数生成确定性风格的模拟企业回复。"""
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            "",
        )
        if config.temperature <= 0.2:
            return f"【精准模式】针对「{last_user}」，建议按星辰数科 SOP-01 执行：1. 核对单号；2. 确认权限；3. 归档工单。"
        if config.temperature <= 0.6:
            return f"您好！关于「{last_user}」，星辰智脑为您梳理了清晰步骤：先核实基础信息，再提交审批流，预计 10 分钟内完成。"
        return f"哇，说到「{last_user}」这个话题太有意思啦！星辰智脑灵光一闪，为您准备了三套脑洞大开的创意方案供您挑选！"

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        config: GenerationConfig,
        chunk_size: int = 4,
        simulate_delay_ms: float = 0.0,
    ) -> Generator[StreamChunk, None, None]:
        """
        以生成器方式模拟 stream=True 流式输出：
        - 严格遵守 max_tokens（此处按字符分片近似）上限，超长时标记 finish_reason='length'
        - 正常结束时标记 finish_reason='stop'
        """
        self.validate_messages(messages)
        config.validate()

        full_text = self._synthesize_reply(messages, config)
        truncated = len(full_text) > config.max_tokens
        effective_text = full_text[: config.max_tokens]

        start = time.perf_counter()
        idx = 0
        for pos in range(0, len(effective_text), max(1, chunk_size)):
            if simulate_delay_ms > 0:
                time.sleep(simulate_delay_ms / 1000.0)
            piece = effective_text[pos : pos + max(1, chunk_size)]
            elapsed = round((time.perf_counter() - start) * 1000, 3)
            yield StreamChunk(chunk_index=idx, delta_content=piece, finish_reason=None, elapsed_ms=elapsed)
            idx += 1

        final_elapsed = round((time.perf_counter() - start) * 1000, 3)
        yield StreamChunk(
            chunk_index=idx,
            delta_content="",
            finish_reason="length" if truncated else "stop",
            elapsed_ms=final_elapsed,
        )

    def run_param_experiment(
        self,
        messages: List[Dict[str, str]],
        presets: Dict[str, GenerationConfig] | None = None,
    ) -> List[ExperimentResult]:
        """对同一组对话运行多组参数预设，产出结构化对比实验报告。"""
        active_presets = presets or SCENE_PRESETS
        results: List[ExperimentResult] = []
        for name, cfg in active_presets.items():
            pieces: List[str] = []
            ttft = 0.0
            total = 0.0
            finish = "stop"
            chunks = 0
            for chunk in self.stream_chat(messages, cfg, chunk_size=6, simulate_delay_ms=0.0):
                if chunks == 0:
                    ttft = chunk.elapsed_ms
                if chunk.delta_content:
                    pieces.append(chunk.delta_content)
                if chunk.finish_reason is not None:
                    finish = chunk.finish_reason
                total = chunk.elapsed_ms
                chunks += 1
            results.append(
                ExperimentResult(
                    profile_name=name,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                    output_text="".join(pieces),
                    chunk_count=chunks,
                    ttft_ms=ttft,
                    total_ms=total,
                    finish_reason=finish,
                )
            )
        return results


if __name__ == "__main__":
    client = StarMindStreamClient()
    msgs = [
        {"role": "system", "content": "你是杭州星辰数科企业 AI 助手。"},
        {"role": "user", "content": "新员工如何申请内网 VPN 权限？"},
    ]
    for exp in client.run_param_experiment(msgs):
        print(f"[{exp.profile_name:16s} | T={exp.temperature}] ({exp.finish_reason}) {exp.output_text}")

