"""
StarMind Day 17 - 步骤二：Prompt 输出质量自动评测器
按 JSON 合法性 (40分) + 必填字段完整性 (40分) + 格式洁净度与长度合规 (20分) 量化打分。
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.day17_prompt_library import StarMindPromptLibrary


@dataclass
class EvalScore:
    """单条 Prompt 响应评测明细。"""
    scene_id: str
    strategy: str
    total_score: float
    json_valid: bool
    missing_keys: List[str]
    clean_json_only: bool
    within_length: bool
    feedback: str


class PromptEvaluator:
    """星辰智脑 Prompt 自动化质量门禁评测器。"""

    def __init__(self, library: StarMindPromptLibrary | None = None) -> None:
        self.library = library or StarMindPromptLibrary()

    @staticmethod
    def _extract_json_block(raw_output: str) -> Tuple[Dict[str, object] | None, bool]:
        """
        尝试解析输出为 JSON：
        返回 (解析后的字典或None, 是否为无多余废话的纯净JSON)。
        """
        stripped = raw_output.strip()
        try:
            obj = json.loads(stripped)
            if isinstance(obj, dict):
                return obj, True
        except json.JSONDecodeError:
            pass

        # 容错：尝试从 ```json ... ``` 或首尾大括号中提取
        match = re.search(r"\{[\s\S]*\}", stripped)
        if match:
            try:
                obj = json.loads(match.group(0))
                if isinstance(obj, dict):
                    return obj, False
            except json.JSONDecodeError:
                return None, False
        return None, False

    def evaluate_output(self, scene_id: str, strategy: str, raw_output: str) -> EvalScore:
        """对单条模型输出进行 100 分制量化评分。"""
        spec = self.library.get_spec(scene_id)
        parsed, is_clean = self._extract_json_block(raw_output)

        score = 0.0
        missing: List[str] = list(spec.required_json_keys)
        json_valid = parsed is not None
        within_len = len(raw_output) <= spec.max_reply_chars
        reasons: List[str] = []

        if json_valid and parsed is not None:
            score += 40.0
            missing = [k for k in spec.required_json_keys if k not in parsed]
            covered_ratio = (len(spec.required_json_keys) - len(missing)) / len(spec.required_json_keys)
            score += round(40.0 * covered_ratio, 2)
            if missing:
                reasons.append(f"缺少必填字段: {missing}")
        else:
            reasons.append("输出不是合法 JSON 对象")

        if is_clean:
            score += 10.0
        else:
            reasons.append("包含 Markdown 围栏或额外寒暄废话")

        if within_len:
            score += 10.0
        else:
            reasons.append(f"长度 {len(raw_output)} 超出上限 {spec.max_reply_chars}")

        feedback = "✅ 完美通过企业质量门禁" if not reasons else "；".join(reasons)
        return EvalScore(
            scene_id=scene_id,
            strategy=strategy,
            total_score=round(score, 2),
            json_valid=json_valid,
            missing_keys=missing,
            clean_json_only=is_clean,
            within_length=within_len,
            feedback=feedback,
        )

    def compare_strategies(
        self, samples: List[Tuple[str, str, str]]
    ) -> Dict[str, float]:
        """
        批量评测不同策略的平均分。
        samples 每项为 (scene_id, strategy_name, raw_model_output)。
        """
        bucket: Dict[str, List[float]] = {}
        for scene_id, strategy, raw in samples:
            res = self.evaluate_output(scene_id, strategy, raw)
            bucket.setdefault(strategy, []).append(res.total_score)
        return {
            strat: round(sum(scores) / len(scores), 2)
            for strat, scores in bucket.items()
        }


if __name__ == "__main__":
    evaluator = PromptEvaluator()
    demo_samples = [
        ("ticket_triage", "zero_shot", "好的，我觉得这是一个很紧急的数据库问题，建议马上重启！"),
        ("ticket_triage", "one_shot", '```json\n{"module": "db", "priority": "P0"}\n```'),
        ("ticket_triage", "few_shot", '{"module": "db", "priority": "P0", "first_action": "排查连接池耗尽原因"}'),
    ]
    for sc, st, out in demo_samples:
        r = evaluator.evaluate_output(sc, st, out)
        print(f"[{st:10s}] 得分: {r.total_score:5.1f} | {r.feedback}")
    print("策略平均分对比:", evaluator.compare_strategies(demo_samples))

