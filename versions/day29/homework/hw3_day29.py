"""
Day 29 课后作业 3（架构进阶）：作业三：实现多租户命名空间隔离管理器（TenantVectorRegistry）
工单：STARMIND-029
"""

"""Day 29 作业三参考答案：防路径穿越的多租户物理隔离向量库管理器"""
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_vector_store import StarMindVectorStore


class TenantVectorRegistry:
    TENANT_RE = re.compile(r"^[a-zA-Z0-9_-]{2,32}$")

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self._cache: Dict[str, StarMindVectorStore] = {}

    def get_store(self, tenant_id: str) -> StarMindVectorStore:
        if not self.TENANT_RE.match(tenant_id):
            raise ValueError(f"非法 tenant_id: {tenant_id}")
        if tenant_id not in self._cache:
            tenant_dir = self.base_dir / tenant_id
            self._cache[tenant_id] = StarMindVectorStore(
                collection_name=f"kb_{tenant_id}",
                persist_directory=tenant_dir,
            )
        return self._cache[tenant_id]


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        reg = TenantVectorRegistry(tmpdir)
        reg.get_store("acme_corp").add_documents([Document("ACME机密报价单")])
        assert reg.get_store("beta_corp").count() == 0
        print("多租户物理隔离校验通过！")

