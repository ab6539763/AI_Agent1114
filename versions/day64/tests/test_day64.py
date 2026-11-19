import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 64 单元测试：容器化部署合规审计与异步健康巡检门禁"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day64_release_bundle import ReleaseBundle, audit_release_bundle, generate_release_bundle
from src.day64_ops_preflight import run_preflight_checks


def test_release_bundle_passes_audit():
    bundle = generate_release_bundle("1.0.0")
    res = audit_release_bundle(bundle)
    assert res["passed"] is True
    assert res["issues"] == []


def test_release_bundle_catches_insecure_configs():
    bad = ReleaseBundle(
        version="latest",
        dockerfile="FROM python:3.11\nUSER root\n",
        compose_yml="image: starmind-api:latest\n",
        nginx_conf="location / { proxy_pass http://app; }\n",
        runbook_md="# 简陋文档\n",
    )
    res = audit_release_bundle(bad)
    assert res["passed"] is False
    assert len(res["issues"]) >= 5


def test_preflight_go_live_and_hold():
    async def ok():
        return True

    async def down():
        return False

    r_ok = asyncio.run(run_preflight_checks({"api": ok, "db": ok}))
    assert r_ok.decision == "GO_LIVE" and r_ok.failed_services == []

    r_bad = asyncio.run(run_preflight_checks({"api": ok, "llm": down}))
    assert r_bad.decision == "HOLD" and r_bad.failed_services == ["llm"]

