"""
StarMind Day 22 - 步骤二：企业前端静态资产自动校验器
校验 HTML 标签闭合平衡、必需交互元素 ID、CSS 主题变量以及 JS 防 XSS 与 API 端点契约。
"""

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Set


VOID_ELEMENTS = {"meta", "link", "br", "hr", "img", "input"}


class _HTMLStructureParser(HTMLParser):
    """基于标准库 HTMLParser 检查标签闭合栈与收集全部元素 ID。"""

    def __init__(self) -> None:
        super().__init__()
        self.stack: List[str] = []
        self.ids: Set[str] = set()
        self.errors: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        for k, v in attrs:
            if k == "id" and v:
                self.ids.add(v)
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_ELEMENTS:
            return
        if not self.stack:
            self.errors.append(f"多余的闭合标签 </{tag}>")
            return
        last = self.stack.pop()
        if last != tag:
            self.errors.append(f"标签嵌套不匹配：期望 </{last}>，实际遇到 </{tag}>")


@dataclass
class ValidationReport:
    passed: bool
    found_ids: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)


def validate_frontend_bundle(
    asset_dir: Path,
    required_ids: Set[str] | None = None,
    expected_api_endpoint: str = "/api/v1/chat/stream",
) -> ValidationReport:
    """对生成的静态前端目录执行端到端工程质量与安全校验。"""
    req_ids = required_ids or {"chat-log", "chat-form", "chat-input", "send-btn", "status-badge"}
    errors: List[str] = []

    html_path = asset_dir / "index.html"
    css_path = asset_dir / "styles.css"
    js_path = asset_dir / "chat_app.js"

    for p in (html_path, css_path, js_path):
        if not p.exists():
            errors.append(f"缺失静态资产文件: {p.name}")
    if errors:
        return ValidationReport(passed=False, errors=errors)

    # 1. HTML 结构与 DOM ID 校验
    html_text = html_path.read_text(encoding="utf-8")
    parser = _HTMLStructureParser()
    parser.feed(html_text)
    errors.extend(parser.errors)
    if parser.stack:
        errors.append(f"存在未闭合的 HTML 标签: {parser.stack}")
    missing_ids = req_ids - parser.ids
    if missing_ids:
        errors.append(f"HTML 缺少必需交互元素 ID: {sorted(missing_ids)}")

    # 2. CSS 主题变量规范校验
    css_text = css_path.read_text(encoding="utf-8")
    if ":root" not in css_text or "--accent" not in css_text:
        errors.append("CSS 未定义 :root 主题变量（至少应包含 --accent）")

    # 3. JS fetch 契约与 XSS 安全审计
    js_text = js_path.read_text(encoding="utf-8")
    if "fetch(" not in js_text:
        errors.append("JS 中未检测到 fetch() 异步通信调用")
    if expected_api_endpoint not in js_text:
        errors.append(f"JS 未对接约定的后端接口端点: {expected_api_endpoint}")
    if re.search(r"\.innerHTML\s*=", js_text):
        errors.append("安全告警：检测到不安全的 .innerHTML 赋值，请改用 .textContent 防范 XSS")

    return ValidationReport(passed=len(errors) == 0, found_ids=parser.ids, errors=errors)


if __name__ == "__main__":
    from tempfile import TemporaryDirectory
    from src.day22_frontend_builder import build_frontend_assets

    with TemporaryDirectory() as tmp:
        build_frontend_assets(Path(tmp))
        rep = validate_frontend_bundle(Path(tmp))
        print("前端资产校验结果:", rep)

