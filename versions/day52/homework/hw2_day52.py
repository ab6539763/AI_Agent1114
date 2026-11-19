"""
Day 52 课后作业 2（企业实战）：企业实战：生成 LLaMA-Factory 的 dataset_info.json 注册表
工单：STARMIND-052
"""

import json


def build_dataset_info() -> dict:
    return {
        "starmind_cs_alpaca": {
            "file_name": "starmind_cs_train_alpaca.json",
            "columns": {
                "prompt": "instruction",
                "query": "input",
                "response": "output",
                "system": "system",
            },
        },
        "starmind_cs_sharegpt": {
            "file_name": "starmind_cs_train_sharegpt.json",
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "system": "system"},
            "tags": {
                "role_tag": "from",
                "content_tag": "value",
                "user_tag": "human",
                "assistant_tag": "gpt",
            },
        },
    }


print(json.dumps(build_dataset_info(), ensure_ascii=False, indent=2))

