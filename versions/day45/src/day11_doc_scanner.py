"""
STARMIND-011 模块二：知识库批量文档扫描与 CSV/JSON 双报表导出器。
演示 pathlib.Path 递归扫描、datetime 时区时间戳、csv.DictWriter(utf-8-sig) 与 json.dump。
"""

import csv
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

from day11_regex_extractor import analyze_document_text

SUPPORTED_SUFFIXES: Tuple[str, ...] = (".txt", ".md")


def scan_directory(root_dir: Path, keywords: List[str]) -> Dict[str, Any]:
    """递归扫描目录下所有 .txt / .md 文件，生成完整统计报告。"""
    if not root_dir.exists() or not root_dir.is_dir():
        raise FileNotFoundError(f"扫描目录不存在: {root_dir}")

    doc_reports: List[Dict[str, Any]] = []
    global_keyword_totals: Dict[str, int] = {kw: 0 for kw in keywords}

    # 使用 pathlib.rglob 递归遍历并按相对路径排序，确保结果稳定
    matched_files = sorted(
        p for p in root_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )

    for file_path in matched_files:
        text = file_path.read_text(encoding="utf-8")
        rel_name = file_path.relative_to(root_dir).as_posix()
        report = analyze_document_text(rel_name, text, keywords)
        doc_reports.append(report)
        for kw, cnt in report["keyword_counts"].items():
            global_keyword_totals[kw] = global_keyword_totals.get(kw, 0) + cnt

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scanned_dir": root_dir.as_posix(),
        "total_files": len(doc_reports),
        "global_keyword_totals": global_keyword_totals,
        "documents": doc_reports,
    }


def export_reports(summary: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    """将扫描结果同时导出为 JSON 完整报告与 CSV 运营明细表。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "kb_scan_report.json"
    csv_path = output_dir / "kb_scan_summary.csv"

    # 1. 导出 JSON
    with json_path.open("w", encoding="utf-8") as jf:
        json.dump(summary, jf, ensure_ascii=False, indent=2)

    # 2. 导出 CSV（utf-8-sig 确保 Excel 打开中文不乱码，newline='' 防多余空行）
    fieldnames = ["file_name", "char_count", "line_count", "total_keyword_hits", "tickets", "emails"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for doc in summary["documents"]:
            writer.writerow(
                {
                    "file_name": doc["file_name"],
                    "char_count": doc["char_count"],
                    "line_count": doc["line_count"],
                    "total_keyword_hits": doc["total_keyword_hits"],
                    "tickets": ";".join(doc["tickets"]),
                    "emails": ";".join(doc["emails"]),
                }
            )

    return {"json": json_path, "csv": csv_path}


if __name__ == "__main__":
    # 使用临时目录自包含演示，运行完自动清理不留垃圾文件
    with tempfile.TemporaryDirectory() as tmp:
        kb_dir = Path(tmp) / "kb"
        (kb_dir / "tech").mkdir(parents=True)
        (kb_dir / "readme.md").write_text("星辰智脑 Python RAG 指南，联系人 chen@starmind.cn", encoding="utf-8")
        (kb_dir / "tech" / "api.txt").write_text("工单 STARMIND-011：Python 与 FastAPI 接口规范", encoding="utf-8")

        summary = scan_directory(kb_dir, ["Python", "RAG", "FastAPI"])
        paths = export_reports(summary, Path(tmp) / "out")
        print(f"扫描完成: {summary['total_files']} 份文档 | 全局词频: {summary['global_keyword_totals']}")
        print("CSV 预览:\n" + paths["csv"].read_text(encoding="utf-8-sig").strip())

