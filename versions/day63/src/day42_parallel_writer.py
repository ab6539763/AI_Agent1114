"""Day 42 - 步骤二：Subgraph 子图 + Fan-out/Fan-in 并行写作 Agent 实战。"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ChapterDraft:
    index: int
    title: str
    content: str
    passed_qa: bool
    revisions: int


class ChapterWriterSubgraph:
    """
    独立可复用的单章写作 Subgraph：
    节点流转：draft_section -> qa_check -> (不合格则 revise_section -> qa_check) -> END
    """

    def __init__(self, simulated_io_sec: float = 0.05) -> None:
        self.simulated_io_sec = simulated_io_sec

    def invoke(self, section_spec: Dict[str, Any]) -> ChapterDraft:
        idx = section_spec["index"]
        title = section_spec["title"]
        topic = section_spec["topic"]

        # 节点 1：起草初稿（模拟外部 LLM 调用耗时）
        time.sleep(self.simulated_io_sec)
        body = f"针对《{topic}》的「{title}」，星辰数科采用模块化微服务与高可用状态机架构，保障核心链路 99.95% 可用性。"
        revisions = 0

        # 节点 2：质检循环（检查是否包含必要企业落地要素）
        while "量化指标" not in body and revisions < 2:
            revisions += 1
            body += " 量化指标：端到端 P95 延迟低于 1.5 秒，自动化单测覆盖率不低于 85%。"

        return ChapterDraft(
            index=idx,
            title=title,
            content=body,
            passed_qa=("量化指标" in body),
            revisions=revisions,
        )


class ParallelProposalWriterAgent:
    """
    主图编排：
    outline_node -> fan_out_chapters (并行调用 ChapterWriterSubgraph) -> fan_in_polish_node
    """

    def __init__(self, max_workers: int = 4, simulated_io_sec: float = 0.05) -> None:
        self.max_workers = max_workers
        self.chapter_subgraph = ChapterWriterSubgraph(simulated_io_sec=simulated_io_sec)

    def _outline_node(self, topic: str) -> List[Dict[str, Any]]:
        return [
            {"index": 1, "title": "一、项目背景与痛点分析", "topic": topic},
            {"index": 2, "title": "二、核心系统架构与技术选型", "topic": topic},
            {"index": 3, "title": "三、安全合规与交付验收计划", "topic": topic},
        ]

    def _fan_out_write_chapters(self, outline: List[Dict[str, Any]]) -> List[ChapterDraft]:
        """Fan-out 并行执行所有章节子图，并在 Fan-in 时按原始 index 恢复严格顺序。"""
        results: List[ChapterDraft] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(self.chapter_subgraph.invoke, sec) for sec in outline]
            for fut in as_completed(futures):
                results.append(fut.result())
        # 关键：按原始大纲序号排序，防止并行乱序
        results.sort(key=lambda ch: ch.index)
        return results

    def _polish_node(self, topic: str, chapters: List[ChapterDraft]) -> str:
        sections_md = [f"# {topic} —— 技术落地方案\n"]
        for ch in chapters:
            sections_md.append(f"## {ch.title}\n{ch.content}\n")
        sections_md.append("---\n*本文档由星辰智脑并行写作 Agent 自动生成并通过质检子图校验。*")
        return "\n".join(sections_md)

    def run(self, topic: str) -> Dict[str, Any]:
        t0 = time.perf_counter()
        outline = self._outline_node(topic)
        chapters = self._fan_out_write_chapters(outline)
        final_doc = self._polish_node(topic, chapters)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "topic": topic,
            "chapter_count": len(chapters),
            "all_passed_qa": all(c.passed_qa for c in chapters),
            "ordered_titles": [c.title for c in chapters],
            "elapsed_ms": elapsed_ms,
            "document": final_doc,
        }


if __name__ == "__main__":
    writer = ParallelProposalWriterAgent(max_workers=3, simulated_io_sec=0.05)
    out = writer.run("星辰数科智能客服升级项目")
    print(f"并行生成 {out['chapter_count']} 章耗时: {out['elapsed_ms']} ms | 全部质检通过: {out['all_passed_qa']}")
    print(out["document"])

