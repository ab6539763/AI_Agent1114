"""
原生高清 SVG 工程图表渲染器（零外部依赖，离线 100% 清晰渲染）。
支持四种企业级研发图表：
1. flowchart    - 业务与代码执行流程图（横向/蛇形流转）
2. architecture - 分层系统架构设计图（带色块分层与调用箭头）
3. sequence     - 模块/服务间交互时序图（生命线与同步/异步消息）
4. schematic    - 核心原理解析示意图（数据变换与内存/向量结构）
"""

from html import escape
from typing import Dict, List


PALETTE = [
    ("#eff6ff", "#2563eb", "#1e3a8a"),  # 蓝
    ("#ecfdf5", "#059669", "#065f46"),  # 绿
    ("#fffbeb", "#d97706", "#92400e"),  # 琥珀
    ("#f5f3ff", "#7c3aed", "#4c1d95"),  # 紫
    ("#fef2f2", "#dc2626", "#991b1b"),  # 红
    ("#f0f9ff", "#0284c7", "#075985"),  # 天蓝
    ("#fdf2f8", "#db2777", "#831843"),  # 粉
]


def _pick_colors(idx: int, custom: str = ""):
    mapping = {
        "blue": PALETTE[0],
        "green": PALETTE[1],
        "amber": PALETTE[2],
        "purple": PALETTE[3],
        "red": PALETTE[4],
        "cyan": PALETTE[5],
        "pink": PALETTE[6],
    }
    if custom and custom in mapping:
        return mapping[custom]
    return PALETTE[idx % len(PALETTE)]


def render_diagram_svg(spec: Dict) -> str:
    kind = spec.get("kind", "flowchart")
    nodes: List[Dict[str, str]] = spec.get("nodes", [])
    edges: List[Dict[str, str]] = spec.get("edges", [])
    if not nodes:
        return ""

    if kind == "sequence":
        return _render_sequence(nodes, edges, spec.get("title", ""))
    elif kind == "architecture":
        return _render_architecture(nodes, edges, spec.get("title", ""))
    elif kind == "schematic":
        return _render_schematic(nodes, edges, spec.get("title", ""))
    return _render_flowchart(nodes, edges, spec.get("title", ""))


def _render_flowchart(nodes: List[Dict], edges: List[Dict], title: str) -> str:
    # 每行最多放 3 个节点，自动蛇形折行
    cols = min(3, len(nodes))
    rows = (len(nodes) + cols - 1) // cols
    box_w, box_h = 220, 74
    gap_x, gap_y = 66, 62
    pad_x, pad_y = 36, 48
    width = pad_x * 2 + cols * box_w + max(0, cols - 1) * gap_x
    height = pad_y * 2 + rows * box_h + max(0, rows - 1) * gap_y + 16

    coords = {}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'style="max-width:100%;height:auto;font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">',
        '<defs><marker id="arrow-flow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#475569"/></marker></defs>',
        f'<rect width="{width}" height="{height}" rx="10" fill="#fafcff"/>',
        f'<text x="{width/2}" y="26" text-anchor="middle" font-size="14" font-weight="700" fill="#1e293b">{escape(title)}</text>',
    ]

    for i, node in enumerate(nodes):
        r = i // cols
        c = i % cols
        # 蛇形排列，偶数行从左到右，奇数行从右到左
        if r % 2 == 1:
            c = cols - 1 - c
        x = pad_x + c * (box_w + gap_x)
        y = pad_y + r * (box_h + gap_y)
        coords[node["id"]] = (x, y, box_w, box_h)

        bg, stroke, text_c = _pick_colors(i, node.get("color", ""))
        label = escape(node.get("label", node["id"]))
        sub = escape(node.get("sub", ""))
        parts.append(
            f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="10" '
            f'fill="{bg}" stroke="{stroke}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{x + box_w/2}" y="{y + 30}" text-anchor="middle" '
            f'font-size="13.5" font-weight="700" fill="{text_c}">{label}</text>'
        )
        if sub:
            parts.append(
                f'<text x="{x + box_w/2}" y="{y + 52}" text-anchor="middle" '
                f'font-size="11.5" fill="#475569">{sub}</text>'
            )

    for edge in edges:
        src = coords.get(edge.get("from", ""))
        dst = coords.get(edge.get("to", ""))
        if not src or not dst:
            continue
        sx, sy, sw, sh = src
        dx, dy, dw, dh = dst
        if abs(sy - dy) < 5:
            # 同一行
            if sx < dx:
                x1, y1, x2, y2 = sx + sw, sy + sh / 2, dx - 3, dy + dh / 2
            else:
                x1, y1, x2, y2 = sx, sy + sh / 2, dx + dw + 3, dy + dh / 2
        else:
            # 跨行
            x1, y1, x2, y2 = sx + sw / 2, sy + sh, dx + dw / 2, dy - 3
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#475569" '
            f'stroke-width="2" marker-end="url(#arrow-flow)"/>'
        )
        elabel = escape(edge.get("label", ""))
        if elabel:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 7
            parts.append(
                f'<rect x="{mx - len(elabel)*6 - 6}" y="{my - 12}" width="{len(elabel)*12 + 12}" height="18" rx="4" fill="#ffffff" opacity="0.92"/>'
            )
            parts.append(
                f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="11" fill="#334155">{elabel}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def _render_architecture(nodes: List[Dict], edges: List[Dict], title: str) -> str:
    # 纵向分层架构图，每层放 1~2 个模块
    width = 860
    layer_h = 88
    pad_y = 48
    n = len(nodes)
    rows = []
    # 按每行 2 个（奇数最后一个居中）排布
    i = 0
    while i < n:
        if i == 0 or (i == n - 1 and (n - i) == 1):
            rows.append([nodes[i]])
            i += 1
        else:
            rows.append(nodes[i : i + 2])
            i += 2

    height = pad_y + len(rows) * (layer_h + 32) + 24
    coords = {}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'style="max-width:100%;height:auto;font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">',
        '<defs><marker id="arrow-arch" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#1d4ed8"/></marker></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="#f8fafc"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="14.5" font-weight="700" fill="#0f172a">{escape(title)}</text>',
    ]

    idx_counter = 0
    for r_idx, row in enumerate(rows):
        y = pad_y + r_idx * (layer_h + 32)
        # 层背景带
        parts.append(
            f'<rect x="24" y="{y - 8}" width="{width - 48}" height="{layer_h + 16}" rx="10" '
            f'fill="#ffffff" stroke="#e2e8f0" stroke-dasharray="5,4"/>'
        )
        if len(row) == 1:
            box_w = 540
            x = (width - box_w) / 2
            node = row[0]
            bg, stroke, text_c = _pick_colors(idx_counter, node.get("color", ""))
            idx_counter += 1
            coords[node["id"]] = (x, y + 6, box_w, layer_h - 12)
            parts.append(
                f'<rect x="{x}" y="{y + 6}" width="{box_w}" height="{layer_h - 12}" rx="9" '
                f'fill="{bg}" stroke="{stroke}" stroke-width="2"/>'
            )
            parts.append(
                f'<text x="{x + box_w/2}" y="{y + 36}" text-anchor="middle" font-size="14" font-weight="700" fill="{text_c}">{escape(node.get("label",""))}</text>'
            )
            parts.append(
                f'<text x="{x + box_w/2}" y="{y + 60}" text-anchor="middle" font-size="12" fill="#475569">{escape(node.get("sub",""))}</text>'
            )
        else:
            box_w = 350
            xs = [56, width - 56 - box_w]
            for c_idx, node in enumerate(row):
                x = xs[c_idx]
                bg, stroke, text_c = _pick_colors(idx_counter, node.get("color", ""))
                idx_counter += 1
                coords[node["id"]] = (x, y + 6, box_w, layer_h - 12)
                parts.append(
                    f'<rect x="{x}" y="{y + 6}" width="{box_w}" height="{layer_h - 12}" rx="9" '
                    f'fill="{bg}" stroke="{stroke}" stroke-width="2"/>'
                )
                parts.append(
                    f'<text x="{x + box_w/2}" y="{y + 36}" text-anchor="middle" font-size="13.5" font-weight="700" fill="{text_c}">{escape(node.get("label",""))}</text>'
                )
                parts.append(
                    f'<text x="{x + box_w/2}" y="{y + 60}" text-anchor="middle" font-size="11.5" fill="#475569">{escape(node.get("sub",""))}</text>'
                )

    for edge in edges:
        src = coords.get(edge.get("from", ""))
        dst = coords.get(edge.get("to", ""))
        if not src or not dst:
            continue
        sx, sy, sw, sh = src
        dx, dy, dw, dh = dst
        if abs(sy - dy) < 10:
            x1, y1 = (sx + sw, sy + sh / 2) if sx < dx else (sx, sy + sh / 2)
            x2, y2 = (dx - 3, dy + dh / 2) if sx < dx else (dx + dw + 3, dy + dh / 2)
        else:
            x1, y1 = sx + sw / 2, sy + sh
            x2, y2 = dx + dw / 2, dy - 3
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1d4ed8" stroke-width="2" marker-end="url(#arrow-arch)"/>'
        )
        elabel = escape(edge.get("label", ""))
        if elabel:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 4
            parts.append(
                f'<text x="{mx}" y="{my}" text-anchor="middle" font-size="11" font-weight="600" fill="#1e40af">{elabel}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def _render_schematic(nodes: List[Dict], edges: List[Dict], title: str) -> str:
    # 原理示意图：水平管道 + 数据流卡片
    box_w, box_h = 185, 86
    gap = 46
    pad_x = 30
    cols = min(4, len(nodes))
    rows = (len(nodes) + cols - 1) // cols
    width = pad_x * 2 + cols * box_w + max(0, cols - 1) * gap
    height = 56 + rows * (box_h + 54) + 20
    coords = {}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'style="max-width:100%;height:auto;font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">',
        '<defs><marker id="arrow-sch" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#0f766e"/></marker></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="#f7fdfa"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="14" font-weight="700" fill="#134e4a">{escape(title)}</text>',
    ]
    for i, node in enumerate(nodes):
        r, c = i // cols, i % cols
        x = pad_x + c * (box_w + gap)
        y = 52 + r * (box_h + 54)
        coords[node["id"]] = (x, y, box_w, box_h)
        bg, stroke, text_c = _pick_colors(i, node.get("color", ""))
        parts.append(
            f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="12" fill="{bg}" stroke="{stroke}" stroke-width="2"/>'
        )
        parts.append(
            f'<circle cx="{x + 18}" cy="{y + 18}" r="10" fill="{stroke}"/>'
            f'<text x="{x + 18}" y="{y + 22}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{i+1}</text>'
        )
        parts.append(
            f'<text x="{x + box_w/2 + 6}" y="{y + 38}" text-anchor="middle" font-size="13" font-weight="700" fill="{text_c}">{escape(node.get("label",""))}</text>'
        )
        parts.append(
            f'<text x="{x + box_w/2}" y="{y + 64}" text-anchor="middle" font-size="11" fill="#475569">{escape(node.get("sub",""))}</text>'
        )
    for edge in edges:
        src = coords.get(edge.get("from", ""))
        dst = coords.get(edge.get("to", ""))
        if not src or not dst:
            continue
        sx, sy, sw, sh = src
        dx, dy, dw, dh = dst
        if abs(sy - dy) < 10:
            x1, y1, x2, y2 = sx + sw, sy + sh / 2, dx - 3, dy + dh / 2
        else:
            x1, y1, x2, y2 = sx + sw / 2, sy + sh, dx + dw / 2, dy - 3
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#0f766e" stroke-width="2" stroke-dasharray="4,2" marker-end="url(#arrow-sch)"/>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def _render_sequence(nodes: List[Dict], edges: List[Dict], title: str) -> str:
    n = len(nodes)
    col_w = 185
    width = max(720, n * col_w + 60)
    height = 110 + max(3, len(edges)) * 54 + 40
    xs = {}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'style="max-width:100%;height:auto;font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">',
        '<defs><marker id="arrow-seq" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#334155"/></marker></defs>',
        f'<rect width="{width}" height="{height}" rx="12" fill="#fafafc"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="14" font-weight="700" fill="#1e293b">{escape(title)}</text>',
    ]
    step_x = (width - 80) / max(1, n)
    for i, node in enumerate(nodes):
        cx = 40 + step_x * i + step_x / 2
        xs[node["id"]] = cx
        bg, stroke, text_c = _pick_colors(i, node.get("color", ""))
        parts.append(
            f'<rect x="{cx - 72}" y="44" width="144" height="44" rx="8" fill="{bg}" stroke="{stroke}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{cx}" y="70" text-anchor="middle" font-size="12.5" font-weight="700" fill="{text_c}">{escape(node.get("label",""))}</text>'
        )
        parts.append(
            f'<line x1="{cx}" y1="88" x2="{cx}" y2="{height - 22}" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="5,5"/>'
        )
    for idx, edge in enumerate(edges):
        x1 = xs.get(edge.get("from", ""))
        x2 = xs.get(edge.get("to", ""))
        if x1 is None or x2 is None:
            continue
        y = 122 + idx * 52
        parts.append(
            f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#334155" stroke-width="2" marker-end="url(#arrow-seq)"/>'
        )
        elabel = escape(edge.get("label", ""))
        parts.append(
            f'<text x="{(x1+x2)/2}" y="{y - 8}" text-anchor="middle" font-size="11.5" fill="#0f172a">{idx+1}. {elabel}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)
