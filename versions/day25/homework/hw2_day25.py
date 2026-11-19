"""
Day 25 课后作业 2（企业实战）：作业二：实现可版本化管理的 PromptRegistry 模板仓库
工单：STARMIND-025
"""

"""Day 25 作业二参考答案：企业级 Prompt 版本化注册中心"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_prompt_template import ChatPromptTemplate


class PromptRegistry:
    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, ChatPromptTemplate]] = {}
        self._latest: Dict[str, str] = {}

    def register(self, name: str, version: str, template: ChatPromptTemplate) -> None:
        self._store.setdefault(name, {})[version] = template
        self._latest[name] = version

    def get(self, name: str, version: Optional[str] = None) -> ChatPromptTemplate:
        if name not in self._store:
            raise KeyError(f"未找到提示词模板: {name}")
        target_ver = version or self._latest[name]
        if target_ver not in self._store[name]:
            raise KeyError(f"模板 {name} 不存在版本: {target_ver}")
        return self._store[name][target_ver]

    def list_versions(self, name: str) -> List[str]:
        return list(self._store.get(name, {}).keys())


if __name__ == "__main__":
    reg = PromptRegistry()
    reg.register("hr_qa", "v1", ChatPromptTemplate.from_messages([("system", "你是HR助手"), ("human", "{q}")]))
    reg.register("hr_qa", "v2", ChatPromptTemplate.from_messages([("system", "你是星辰数科资深HRBP，回答需附制度编号"), ("human", "{q}")]))

    assert reg.list_versions("hr_qa") == ["v1", "v2"]
    latest_msgs = reg.get("hr_qa").format_messages(q="年假怎么休？")
    print("最新版本 System Prompt:", latest_msgs[0].content)
    assert "制度编号" in latest_msgs[0].content

