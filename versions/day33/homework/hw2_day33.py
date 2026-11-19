"""
Day 33 课后作业 2（企业实战）：作业二：实现 Sentence-Window（句子窗口扩展）检索器
工单：STARMIND-033
"""

"""Day 33 作业二参考答案：Sentence-Window 句子窗口扩展检索器"""
import re
from typing import Dict, List


class SentenceWindowRetriever:
    def __init__(self, window: int = 1) -> None:
        self.window = window
        self.doc_sentences: Dict[str, List[str]] = {}

    def index_document(self, doc_id: str, text: str) -> None:
        sents = [s.strip() for s in re.split(r"(?<=[。！？])", text) if s.strip()]
        self.doc_sentences[doc_id] = sents

    def search_with_window(self, keyword: str) -> List[str]:
        outputs: List[str] = []
        for doc_id, sents in self.doc_sentences.items():
            for idx, s in enumerate(sents):
                if keyword in s:
                    left = max(0, idx - self.window)
                    right = min(len(sents), idx + self.window + 1)
                    outputs.append("".join(sents[left:right]))
        return outputs


if __name__ == "__main__":
    sw = SentenceWindowRetriever(window=1)
    sw.index_document(
        "D1",
        "网关默认超时时间为15秒。遇到ERR-5042需优先排查显存水位。若持续超5分钟请立即开启熔断。",
    )
    res = sw.search_with_window("ERR-5042")
    print("窗口扩展结果:", res[0])
    assert "15秒" in res[0] and "熔断" in res[0]

