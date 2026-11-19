"""
STARMIND-007 模块一：第一周 Python 核心语法自动化周测判分引擎。
涵盖类型转换、切片、集合运算、JSON 参数与默认参数陷阱五大高频考点。
"""

from typing import Dict, List, Any

# 周测标准题库（题号、题干、标准答案、解析）
WEEK1_QUESTIONS: List[Dict[str, str]] = [
    {
        "id": "Q1",
        "topic": "布尔类型转换",
        "question": "表达式 bool('False') 的求值结果是 True 还是 False？",
        "answer": "True",
        "explanation": "非空字符串转 bool 永远为 True，只有空字符串 '' 为 False。",
    },
    {
        "id": "Q2",
        "topic": "空集合创建",
        "question": "在 Python 中创建一个空集合应该写 set() 还是 {}？",
        "answer": "set()",
        "explanation": "{} 创建的是空字典 dict，空集合必须写 set()。",
    },
    {
        "id": "Q3",
        "topic": "字符串切片",
        "question": "表达式 'StarMind'[0:4] 的结果是什么？",
        "answer": "Star",
        "explanation": "切片遵循左闭右开原则，取索引 0, 1, 2, 3 四个字符。",
    },
    {
        "id": "Q4",
        "topic": "JSON 中文输出",
        "question": "json.dumps 中防止中文被转义为 \\uXXXX 的关键参数名是什么？",
        "answer": "ensure_ascii",
        "explanation": "设置 ensure_ascii=False 即可保留可读中文字符。",
    },
    {
        "id": "Q5",
        "topic": "函数默认参数",
        "question": "需要列表型可选参数时，函数签名中默认值应写 None 还是 []？",
        "answer": "None",
        "explanation": "可变默认参数 [] 会在多次调用间共享导致数据串台，必须用 None 占位。",
    },
]


def grade_quiz(submissions: Dict[str, str]) -> Dict[str, Any]:
    """根据学员提交的答案字典自动判分并生成错题诊断报告。"""
    total = len(WEEK1_QUESTIONS)
    correct = 0
    wrong_details: List[Dict[str, str]] = []

    for q in WEEK1_QUESTIONS:
        qid = q["id"]
        user_ans = str(submissions.get(qid, "")).strip()
        if user_ans == q["answer"]:
            correct += 1
        else:
            wrong_details.append(
                {
                    "id": qid,
                    "topic": q["topic"],
                    "your_answer": user_ans or "(未作答)",
                    "expected": q["answer"],
                    "explanation": q["explanation"],
                }
            )

    score = int(round((correct / total) * 100)) if total else 0
    return {
        "total": total,
        "correct": correct,
        "score": score,
        "passed": score >= 80,
        "wrong_details": wrong_details,
    }


if __name__ == "__main__":
    perfect_answers = {"Q1": "True", "Q2": "set()", "Q3": "Star", "Q4": "ensure_ascii", "Q5": "None"}
    report = grade_quiz(perfect_answers)
    print(f"第一周周测成绩: {report['score']} 分 | 是否通过: {report['passed']}")

