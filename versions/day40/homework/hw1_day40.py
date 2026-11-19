"""
Day 40 课后作业 1（基础巩固）：为文件工具增加扩展名白名单与大小限制
工单：STARMIND-040
"""

"""Day 40 作业 1 参考答案：扩展名白名单与文件大小护栏。"""

from pathlib import Path
import tempfile

ALLOWED_EXTS = {".md", ".txt", ".json"}
MAX_CHARS = 10_000


def safe_export_doc(base_dir: Path, filename: str, content: str) -> str:
    """受控导出文档：限定扩展名、大小与目录边界。"""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        return f"拒绝写入：不支持的文件类型 '{ext}'，仅允许 {sorted(ALLOWED_EXTS)}"
    if len(content) > MAX_CHARS:
        return f"拒绝写入：内容长度 {len(content)} 超过上限 {MAX_CHARS}"
    target = (base_dir / filename).resolve()
    if not target.is_relative_to(base_dir.resolve()):
        return "拒绝写入：检测到路径穿越风险"
    target.write_text(content, encoding="utf-8")
    return f"导出成功：{target.name}"


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        assert "拒绝写入" in safe_export_doc(p, "hack.sh", "rm -rf /")
        assert "导出成功" in safe_export_doc(p, "report.md", "# OK")
        print("作业 1 验证通过")

