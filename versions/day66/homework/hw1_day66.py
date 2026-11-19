"""
Day 66 课后作业 1（基础巩固）：基础巩固：计算简历与目标岗位 JD 的关键词匹配度
工单：STARMIND-066
"""

def calc_jd_match(resume_text: str, jd_keywords: list[str]) -> dict:
    low = resume_text.lower()
    hit = [k for k in jd_keywords if k.lower() in low]
    miss = [k for k in jd_keywords if k.lower() not in low]
    return {"match_rate": round(len(hit) / max(1, len(jd_keywords)), 4), "missing": miss}


res = calc_jd_match("主导 RAG、FastAPI、SSE 与 Docker 落地", ["RAG", "FastAPI", "vLLM", "Docker"])
assert res["match_rate"] == 0.75 and res["missing"] == ["vLLM"]
print("JD 匹配度体检通过:", res)

