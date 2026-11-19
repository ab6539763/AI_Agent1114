"""
Day 56 - 模块二：生产环境运维健康巡检与分级告警脚本
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ServiceProbe:
    """单个依赖服务的探针采集结果"""
    name: str
    is_critical: bool
    healthy: bool
    latency_ms: float
    detail: str = ""


@dataclass
class HostMetrics:
    """宿主机资源水位"""
    cpu_percent: float
    mem_percent: float
    disk_percent: float


@dataclass
class InspectionReport:
    """运维巡检总报告"""
    overall_status: str     # "GREEN" | "YELLOW" | "RED"
    exit_code: int          # 0=健康, 1=警告降级, 2=严重故障
    alerts: List[str] = field(default_factory=list)
    summary: Dict[str, object] = field(default_factory=dict)


def run_ops_inspection(
    probes: List[ServiceProbe],
    host: HostMetrics,
    max_latency_ms: float = 500.0,
) -> InspectionReport:
    """评估所有微服务探针与主机水位，输出红黄绿分级状态与退出码"""
    alerts: List[str] = []
    has_red = False
    has_yellow = False

    for p in probes:
        if not p.healthy:
            if p.is_critical:
                has_red = True
                alerts.append(f"[CRITICAL] 核心服务 {p.name} 不可达: {p.detail}")
            else:
                has_yellow = True
                alerts.append(f"[WARN] 非核心服务 {p.name} 异常，已进入降级模式: {p.detail}")
        elif p.latency_ms > max_latency_ms:
            has_yellow = True
            alerts.append(f"[WARN] 服务 {p.name} 探针延迟偏高 ({p.latency_ms:.1f}ms > {max_latency_ms}ms)")

    if host.disk_percent >= 90.0 or host.mem_percent >= 92.0:
        has_red = True
        alerts.append(f"[CRITICAL] 宿主机资源危急: MEM={host.mem_percent}%, DISK={host.disk_percent}%")
    elif host.disk_percent >= 80.0 or host.mem_percent >= 82.0 or host.cpu_percent >= 85.0:
        has_yellow = True
        alerts.append(
            f"[WARN] 宿主机负载偏高: CPU={host.cpu_percent}%, MEM={host.mem_percent}%, DISK={host.disk_percent}%"
        )

    if has_red:
        status, code = "RED", 2
    elif has_yellow:
        status, code = "YELLOW", 1
    else:
        status, code = "GREEN", 0

    return InspectionReport(
        overall_status=status,
        exit_code=code,
        alerts=alerts,
        summary={
            "total_services": len(probes),
            "healthy_services": sum(1 for p in probes if p.healthy),
            "host": {"cpu": host.cpu_percent, "mem": host.mem_percent, "disk": host.disk_percent},
        },
    )


if __name__ == "__main__":
    probes = [
        ServiceProbe("starmind-api", True, True, 18.5, "ok"),
        ServiceProbe("vllm-gateway", True, True, 45.2, "ok"),
        ServiceProbe("redis-cache", False, True, 3.1, "ok"),
    ]
    rep = run_ops_inspection(probes, HostMetrics(cpu_percent=35.0, mem_percent=58.0, disk_percent=42.0))
    print(f"巡检状态: {rep.overall_status} (exit_code={rep.exit_code}), 告警数={len(rep.alerts)}")

