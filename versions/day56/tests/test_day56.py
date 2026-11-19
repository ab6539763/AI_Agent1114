import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 56 单元测试：部署资产审计与运维健康巡检"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day56_deploy_generator import (
    DeploySpec,
    audit_deploy_assets,
    render_multistage_dockerfile,
    render_sse_nginx_conf,
)
from src.day56_ops_inspector import HostMetrics, ServiceProbe, run_ops_inspection


def test_generated_deploy_assets_pass_security_audit():
    spec = DeploySpec()
    issues = audit_deploy_assets(render_multistage_dockerfile(spec), render_sse_nginx_conf(spec))
    assert issues == []


def test_audit_catches_root_user_and_missing_sse_buffering_off():
    bad_df = "FROM python:3.11\nUSER root\nCMD ['python']"
    bad_ngx = "location /api/ { proxy_pass http://api:8000; }"
    issues = audit_deploy_assets(bad_df, bad_ngx)
    assert len(issues) >= 4


def test_ops_inspection_green_yellow_red():
    ok_host = HostMetrics(30.0, 50.0, 40.0)
    r_green = run_ops_inspection([ServiceProbe("api", True, True, 20.0)], ok_host)
    assert r_green.overall_status == "GREEN" and r_green.exit_code == 0

    r_yellow = run_ops_inspection(
        [ServiceProbe("api", True, True, 20.0), ServiceProbe("redis", False, False, 0.0, "timeout")],
        ok_host,
    )
    assert r_yellow.overall_status == "YELLOW" and r_yellow.exit_code == 1

    r_red = run_ops_inspection([ServiceProbe("api", True, False, 0.0, "502")], ok_host)
    assert r_red.overall_status == "RED" and r_red.exit_code == 2

