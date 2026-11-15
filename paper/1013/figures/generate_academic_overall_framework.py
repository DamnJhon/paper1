#!/usr/bin/env python3
"""Generate a detailed, publication-style overall method diagram.

The figure is intentionally drawn as an editable vector schematic rather
than a slide-like infographic.  It mirrors the four technical blocks in the
paper and keeps the training/deployment information boundary explicit.
"""

from __future__ import annotations

from pathlib import Path

from generate_figures import (
    BLUE,
    DARK,
    GRAY,
    GREEN,
    GRID,
    LIGHT,
    MID,
    NAVY,
    ORANGE,
    PURPLE,
    TEAL,
    WHITE,
    SVG,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "overview"
OUT.mkdir(exist_ok=True)


PALE_BLUE = "#F4F7FB"
PALE_ORANGE = "#FCF7F1"
PALE_PURPLE = "#F7F5FA"
PALE_GREEN = "#F3F8F6"
PANEL_STROKE = "#AEBAC4"


def save(svg: SVG, name: str) -> Path:
    svg.parts.append("</svg>")
    path = OUT / name
    path.write_text("\n".join(svg.parts), encoding="utf-8")
    return path


def panel(svg: SVG, x: int, y: int, w: int, h: int, letter: str, title: str, accent: str) -> None:
    svg.rect(x, y, w, h, fill=WHITE, stroke=PANEL_STROKE, sw=1.6, rx=5)
    svg.text(x + 22, y + 40, f"({letter})", 26, fill=accent, weight=700)
    svg.text(x + 75, y + 40, title, 28, fill=DARK, weight=700)
    svg.line(x + 20, y + 58, x + w - 20, y + 58, stroke=GRID, sw=1.5)
    svg.line(x + 20, y + 58, x + 240, y + 58, stroke=accent, sw=3)


def node(
    svg: SVG,
    x: int,
    y: int,
    w: int,
    h: int,
    lines: list[str],
    *,
    stroke: str = NAVY,
    fill: str = WHITE,
    size: int = 20,
    weight: int = 550,
    rx: int = 3,
) -> None:
    svg.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.6, rx=rx)
    gap = size * 1.35
    total = (len(lines) - 1) * gap
    first_y = y + h / 2 - total / 2 + size * 0.36
    svg.multiline(x + w / 2, first_y, lines, size=size, fill=DARK, weight=weight, gap=1.35)


def arrow(svg: SVG, x1: int, y1: int, x2: int, y2: int, *, color: str = NAVY, sw: float = 2.2) -> None:
    arrow_id = "arrow-blue" if color == BLUE else "arrow-green" if color == GREEN else "arrow"
    svg.line(x1, y1, x2, y2, stroke=color, sw=sw, arrow=True, arrow_id=arrow_id)


def label(svg: SVG, x: int, y: int, text: str, *, size: int = 18, color: str = GRAY,
          weight: int = 500, anchor: str = "start") -> None:
    svg.text(x, y, text, size=size, fill=color, weight=weight, anchor=anchor)


def build() -> Path:
    s = SVG(2400, 1380)

    # Quiet figure-level labels; the formal title remains in the manuscript caption.
    label(s, 45, 25, "TRAINING", size=16, color=BLUE, weight=700)
    s.line(145, 20, 1610, 20, stroke=GRID, sw=1.2)
    label(s, 1660, 25, "DEPLOYMENT", size=16, color=GREEN, weight=700)
    s.line(1780, 20, 2355, 20, stroke=GRID, sw=1.2)

    # ------------------------------------------------------------------ (a)
    ax, ay, aw, ah = 35, 40, 720, 525
    panel(s, ax, ay, aw, ah, "a", "多方向、多距离参考族构建", BLUE)
    xs = [65, 235, 405, 575]
    widths = [135, 135, 135, 145]
    contents = [
        ["基础跳跃", "动作片段"],
        ["运动特征", "近邻检索"],
        ["旋转与", "幅度调整"],
        ["相位对齐与", "可行性筛选"],
    ]
    for x, w, lines in zip(xs, widths, contents):
        node(s, x, 135, w, 92, lines, stroke=BLUE, fill=PALE_BLUE, size=19)
    for x1, x2 in zip([200, 370, 540], [225, 395, 565]):
        arrow(s, x1, 181, x2, 181, color=BLUE)

    label(s, 65, 275, "运动特征", size=19, color=BLUE, weight=700)
    label(s, 175, 275, "x_i = [q_i, qdot_i, p_i^root, v_i^root, p_i^foot, c_i, phi_i]", size=20, color=DARK)
    label(s, 65, 318, "检索目标", size=19, color=BLUE, weight=700)
    label(s, 175, 318, "i* = arg min_i [ ||x − x_i||_W^2 + lambda_g ||g − g_i||_2^2 ]", size=20, color=DARK)
    label(s, 65, 361, "检查项", size=19, color=BLUE, weight=700)
    label(s, 175, 361, "关节限位 · 速度连续性 · 足端穿透 · 接触一致性", size=19, color=DARK)

    s.rect(65, 418, 655, 74, fill=PALE_BLUE, stroke=BLUE, sw=1.5, rx=3)
    label(s, 392, 451, "输出：增强参考轨迹集  {r_1:T}", size=22, color=BLUE, weight=700, anchor="middle")
    label(s, 392, 480, "仅用于 Teacher 训练，不作为部署输入", size=17, color=GRAY, anchor="middle")
    label(s, 392, 535, "离线数据准备", size=17, color=GRAY, weight=600, anchor="middle")

    # ------------------------------------------------------------------ (b)
    bx, by, bw, bh = 785, 40, 1580, 525
    panel(s, bx, by, bw, bh, "b", "参考轨迹条件 Teacher 与实际位移重标注", ORANGE)

    node(s, 815, 130, 250, 112, ["训练特权输入", "完整状态 s_t", "当前/未来参考 r_t"],
         stroke=ORANGE, fill=PALE_ORANGE, size=19)
    node(s, 1110, 145, 205, 82, ["Teacher  πE", "πE(a_t | s_t, r_t)"],
         stroke=ORANGE, fill=PALE_ORANGE, size=20, weight=650)
    node(s, 1360, 130, 260, 112, ["PhysX / Unitree G1", "29 DoF", "动力学交互"],
         stroke=NAVY, fill=LIGHT, size=19)
    arrow(s, 1065, 186, 1100, 186, color=ORANGE)
    arrow(s, 1315, 186, 1350, 186, color=ORANGE)
    label(s, 1335, 170, "a_t^E", size=17, color=ORANGE, weight=700, anchor="end")

    # Teacher feedback loop.
    s.path("M 1490 247 L 1490 300 L 1212 300 L 1212 237", stroke=TEAL, sw=2.0,
           arrow=True, arrow_id="arrow-green")
    label(s, 1350, 290, "状态 / 接触反馈", size=17, color=TEAL, weight=600, anchor="middle")

    # Geometric relabeling inset.
    s.rect(1665, 112, 360, 214, fill=WHITE, stroke=PANEL_STROKE, sw=1.3, rx=3)
    label(s, 1845, 142, "实际位移重标注", size=20, color=ORANGE, weight=700, anchor="middle")
    ox, oy = 1710, 282
    s.line(ox, oy, 1975, oy, stroke=MID, sw=1.5, arrow=True)
    s.line(ox, oy, ox, 165, stroke=MID, sw=1.5, arrow=True)
    s.line(ox, oy, 1928, 176, stroke=BLUE, sw=2.2, dash="7 5")
    s.line(ox, oy, 1900, 218, stroke=ORANGE, sw=3.0)
    s.circle(1928, 176, 6, fill=BLUE, stroke=WHITE, sw=1)
    s.circle(1900, 218, 7, fill=ORANGE, stroke=WHITE, sw=1)
    label(s, 1938, 180, "名义目标", size=15, color=BLUE)
    label(s, 1910, 223, "实际落点", size=15, color=ORANGE)
    label(s, 1845, 315, "g_i = Δp_i(actual, B0)", size=18, color=DARK, weight=650, anchor="middle")

    node(s, 2070, 130, 250, 176,
         ["专家数据集  D_E", "{o_t, g_i, z_t,", "a_t^E, s_{t+1}}", "BC / DAgger 标签"],
         stroke=ORANGE, fill=PALE_ORANGE, size=18)
    arrow(s, 1620, 186, 1655, 186, color=ORANGE)
    arrow(s, 2025, 218, 2060, 218, color=ORANGE)

    label(s, 815, 365, "Teacher 奖励", size=19, color=ORANGE, weight=700)
    label(s, 965, 365,
          "关节/根节点跟踪 + 足端接触 + 稳定性 − 能耗 − 动作变化 − 非期望接触",
          size=19, color=DARK)
    label(s, 815, 412, "核心作用", size=19, color=ORANGE, weight=700)
    label(s, 965, 412, "将运动学参考转换为满足机器人动力学和接触约束的专家行为", size=19, color=DARK)
    label(s, 815, 459, "重标注原则", size=19, color=ORANGE, weight=700)
    label(s, 965, 459, "Student 条件采用 Teacher 的真实起落位移，而非名义参考位移", size=19, color=DARK)
    s.rect(815, 492, 1505, 46, fill=PALE_ORANGE, stroke=GRID, sw=1.0, rx=2)
    label(s, 1567, 522, "训练阶段可见：参考相位 · 未来全身轨迹 · 仿真完整状态",
          size=18, color=GRAY, weight=600, anchor="middle")

    # Cross-stage data transfer to Student training.
    s.path("M 2195 308 L 2195 595 L 1370 595 L 1370 705", stroke=ORANGE, sw=2.2,
           arrow=True, arrow_id="arrow")
    label(s, 1780, 589, "实际位移标签 + Teacher 专家动作", size=17, color=ORANGE,
          weight=650, anchor="middle")

    # ------------------------------------------------------------------ (c)
    cx, cy, cw, ch = 35, 625, 1580, 710
    panel(s, cx, cy, cw, ch, "c", "Student：BC 初始化与 DAgger–PPO 联合优化", PURPLE)

    node(s, 70, 730, 260, 150,
         ["Student 输入：96维", "本体观测 o_t：93", "二维目标位移 g：2", "跳跃触发 z_t：1"],
         stroke=PURPLE, fill=PALE_PURPLE, size=18)
    node(s, 390, 755, 230, 100, ["Student  πS", "πS(a_t | o_t,g,z_t)", "29维关节目标"],
         stroke=TEAL, fill=PALE_GREEN, size=18, weight=650)
    node(s, 680, 755, 255, 100, ["G1 / PhysX", "Student 交互状态", "任务回报 R_s"],
         stroke=NAVY, fill=LIGHT, size=18)
    node(s, 1000, 720, 555, 170,
         ["DAgger：在 Student 访问状态上查询 Teacher", "Student 状态 (s_t,o_t) → 冻结 πE", "专家动作 a_t^E → 聚合样本 D_k", "缓解闭环状态分布偏移"],
         stroke=ORANGE, fill=PALE_ORANGE, size=18)
    arrow(s, 330, 805, 380, 805, color=NAVY)
    arrow(s, 620, 805, 670, 805, color=NAVY)
    arrow(s, 935, 805, 990, 805, color=NAVY)

    # Three training objectives.
    node(s, 70, 955, 430, 165,
         ["BC 初始化 / 动作模仿", "L_act = E[ ||mu_S − a^E||_2^2 ]", "使用实际位移重标注专家数据"],
         stroke=ORANGE, fill=WHITE, size=19)
    node(s, 540, 955, 430, 165,
         ["PPO：任务回报优化", "L_PPO = L_clip + c_v L_value − c_e H", "目标到达 · 安全落地 · 稳定恢复"],
         stroke=TEAL, fill=WHITE, size=19)
    node(s, 1010, 955, 545, 165,
         ["DAgger：聚合监督", "D_k ← D_{k−1} ∪ {o_t,g,z_t,a_t^E}", "针对 Student 自身访问状态持续补充标签"],
         stroke=ORANGE, fill=WHITE, size=19)
    arrow(s, 285, 945, 285, 925, color=ORANGE)
    s.path("M 808 862 L 808 945", stroke=TEAL, sw=2.0, arrow=True, arrow_id="arrow-green")
    s.path("M 1282 895 L 1282 945", stroke=ORANGE, sw=2.0, arrow=True, arrow_id="arrow")

    s.rect(70, 1170, 1485, 72, fill=PALE_PURPLE, stroke=PURPLE, sw=1.5, rx=3)
    label(s, 812, 1204,
          "联合目标：L_k = (1 − alpha_k) L_PPO + alpha_k L_act，   alpha_k = max(0.1, 1 − k/10000)",
          size=21, color=DARK, weight=650, anchor="middle")
    label(s, 812, 1232, "训练后冻结并部署最终 Student；Teacher 与参考数据不再参与在线执行",
          size=17, color=GRAY, anchor="middle")

    label(s, 70, 1293, "Student 奖励", size=18, color=TEAL, weight=700)
    label(s, 205, 1293,
          "目标位移 + 方向一致性 + 安全落地 + 稳定恢复 − 动作变化 − 关节代价 − 非期望接触",
          size=18, color=DARK)

    # ------------------------------------------------------------------ (d)
    dx, dy, dw, dh = 1645, 625, 720, 710
    panel(s, dx, dy, dw, dh, "d", "二维目标条件闭环部署", GREEN)
    node(s, 1680, 730, 200, 105, ["任务输入", "o_t, g, z_t", "93 + 2 + 1维"],
         stroke=GREEN, fill=PALE_GREEN, size=18)
    node(s, 1925, 745, 170, 78, ["πS*", "固定策略"],
         stroke=GREEN, fill=PALE_GREEN, size=20, weight=700)
    node(s, 2140, 730, 190, 105, ["G1 / PhysX", "29维动作", "50 Hz 控制"],
         stroke=GREEN, fill=PALE_GREEN, size=18)
    arrow(s, 1880, 783, 1915, 783, color=GREEN)
    arrow(s, 2095, 783, 2130, 783, color=GREEN)
    s.path("M 2235 845 L 2235 890 L 1780 890 L 1780 845", stroke=TEAL, sw=2.0,
           arrow=True, arrow_id="arrow-green")
    label(s, 2007, 882, "本体反馈  o_{t+1}", size=17, color=TEAL, weight=600, anchor="middle")

    label(s, 1680, 947, "目标几何（起跳坐标系 B0）", size=20, color=DARK, weight=700)
    gx, gy = 1745, 1160
    s.line(gx, gy, 2265, gy, stroke=MID, sw=1.5, arrow=True)
    s.line(gx, gy, gx, 980, stroke=MID, sw=1.5, arrow=True)
    s.line(gx, gy, 2175, 1000, stroke=BLUE, sw=3.2)
    s.line(gx, gy, 2125, 1055, stroke=ORANGE, sw=3.2)
    s.circle(2175, 1000, 8, fill=BLUE, stroke=WHITE, sw=1)
    s.circle(2125, 1055, 8, fill=ORANGE, stroke=WHITE, sw=1)
    label(s, 2188, 1005, "g：期望位移", size=17, color=BLUE, weight=650)
    label(s, 2138, 1060, "Δp：实际位移", size=17, color=ORANGE, weight=650)
    s.line(2125, 1055, 2175, 1000, stroke=GRAY, sw=1.4, dash="5 4")
    label(s, 2215, 1085, "e_p = ||Δp − g||_2", size=17, color=DARK, weight=650, anchor="end")
    label(s, 1755, 1192, "起跳点", size=16, color=GRAY)

    s.rect(1680, 1230, 650, 70, fill=PALE_GREEN, stroke=GREEN, sw=1.3, rx=3)
    label(s, 2005, 1258, "联合成功判据", size=18, color=GREEN, weight=700, anchor="middle")
    label(s, 2005, 1287, "有效起跳 · 目标到达 · 安全落地 · 稳定恢复", size=18,
          color=DARK, weight=600, anchor="middle")
    label(s, 2005, 1323, "无相位 · 无未来参考 · 无在线动作检索", size=17,
          color=GREEN, weight=700, anchor="middle")

    # A single dashed separator emphasizes the deployment information boundary.
    s.line(1630, 610, 1630, 1342, stroke=GREEN, sw=1.8, dash="8 7")
    return save(s, "fig01_overall_framework_academic.svg")


if __name__ == "__main__":
    print(build())
