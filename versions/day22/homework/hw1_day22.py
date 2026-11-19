"""
Day 22 课后作业 1（基础巩固）：为聊天前端新增暗黑模式（Dark Theme）CSS 主题变量块
工单：STARMIND-022
"""

def append_dark_theme(css_text: str) -> str:
    """为企业聊天前端追加暗黑模式 CSS 变量定义。"""
    dark_block = """
[data-theme="dark"] {
  --bg-page: #0b1120;
  --bg-panel: #111827;
  --text-main: #f1f5f9;
  --border: #1f2937;
}
"""
    return css_text.rstrip() + "\n" + dark_block


if __name__ == "__main__":
    from src.day22_frontend_builder import STYLES_CSS
    updated = append_dark_theme(STYLES_CSS)
    print("包含暗黑模式:", '[data-theme="dark"]' in updated)

