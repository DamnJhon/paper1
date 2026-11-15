"""Draw the method figure. Run with Python and Matplotlib installed."""

from pathlib import Path

from matplotlib.path import Path as MathPath
from matplotlib.textpath import TextPath

from generate_figures import SVG, esc


INK = "#202a34"
MUTED = "#515e69"
BLUE = "#295d79"
RUST = "#944b32"
RULE = "#a9b4bd"
OUT = Path(__file__).resolve().parent / "overview"


def formula(svg, x, y, tex, size=19, color=INK, centered=True):
    """Use vector glyph outlines so math renders consistently in SVG and PDF."""
    glyphs = TextPath((0, 0), f"${tex}$", size=size, usetex=False)
    box = glyphs.get_extents()
    offset = x - (box.x0 + box.width / 2 if centered else box.x0)
    codes = {
        MathPath.MOVETO: "M", MathPath.LINETO: "L", MathPath.CURVE3: "Q",
        MathPath.CURVE4: "C", MathPath.CLOSEPOLY: "Z",
    }
    segments = []
    for points, code in glyphs.iter_segments(simplify=False):
        coordinates = " ".join(
            f"{offset + px:.2f},{y - py:.2f}"
            for px, py in zip(points[::2], points[1::2])
        ) if code != MathPath.CLOSEPOLY else ""
        segments.append(f"{codes[code]}{coordinates}")
    svg.raw(f'<g aria-label="{esc(tex)}"><title>{esc(tex)}</title>'
            f'<path fill="{color}" d="{" ".join(segments)}"/></g>')


def note(svg, x, y, text, size=17, color=MUTED, anchor="middle"):
    svg.text(x, y, text, size, fill=color, anchor=anchor)


def node(svg, x, y, w, h, title, color=INK, fill="#ffffff"):
    svg.rect(x, y, w, h, fill=fill, stroke=color, sw=1.25, rx=0)
    svg.text(x + w / 2, y + 26, title, 19, fill=color, weight=600, anchor="middle")


def edge(svg, path, color=BLUE, dashed=False):
    marker = {BLUE: "flow", RUST: "supervision", MUTED: "feedback"}[color]
    svg.path(path, stroke=color, sw=1.65, dash="5 4" if dashed else None,
             arrow=True, arrow_id=marker)


def section(svg, y, title):
    svg.text(30, y, title, 22, fill=INK, weight=650)


def draw():
    s = SVG(1600, 1020)
    for name, color in (("flow", BLUE), ("supervision", RUST), ("feedback", MUTED)):
        s.raw(f'<defs><marker id="{name}" markerWidth="7" markerHeight="7" refX="7" '
              f'refY="3.5" orient="auto" markerUnits="userSpaceOnUse">'
              f'<path d="M0 0 L7 3.5 L0 7 Z" fill="{color}"/></marker></defs>')

    section(s, 37, "(a) 参考轨迹构建与专家数据采集")
    node(s, 30, 83, 302, 103, "离线参考增强")
    note(s, 181, 137, "基础跳跃片段 → 特征近邻检索")
    note(s, 181, 163, "旋转与幅度调整 → 可行性筛选")
    node(s, 410, 83, 236, 103, "Teacher 策略", BLUE, "#f3f7f9")
    formula(s, 528, 141, r"\pi_E(a_t\mid s_t,r_t)")
    note(s, 528, 166, "完整状态与当前／短时未来参考", 15)
    node(s, 725, 83, 192, 103, "G1／PhysX")
    note(s, 821, 138, "参考跟踪与接触仿真")
    note(s, 821, 163, "冻结 Teacher 后采集轨迹", 15)
    node(s, 996, 83, 228, 103, "实际位移重标注", RUST, "#faf6f3")
    formula(s, 1110, 139, r"g_i=\Delta p_i^{\mathrm{actual}}")
    note(s, 1110, 165, "在起跳坐标系中测量基座位移", 15)
    node(s, 1295, 83, 275, 103, "成功轨迹的专家数据", RUST, "#faf6f3")
    formula(s, 1432, 145, r"D_E=\{(o_t,g_i,z_t,a_t^E,s_{t+1})\}", 18)
    for start, end in ((332, 410), (646, 725), (917, 996), (1224, 1295)):
        edge(s, f"M {start} 134 H {end}")
    formula(s, 370, 119, r"r_t", 18, BLUE)
    formula(s, 685, 119, r"a_t^E", 18, BLUE)
    edge(s, "M 821 186 V 222 H 528 V 186", MUTED, True)
    note(s, 683, 215, "状态与接触反馈", 15)
    note(s, 32, 225, "参考族覆盖多方向、多距离", 16, MUTED, "start")
    s.line(30, 247, 1570, 247, stroke=RULE, sw=1)

    section(s, 276, "(b) Student 初始化与联合训练")
    node(s, 30, 346, 270, 98, "训练输入")
    formula(s, 165, 402, r"(o_t,g,z_t)", 20)
    note(s, 165, 427, "本体相关观测、目标、触发")
    node(s, 405, 346, 225, 98, "当前 Student", BLUE, "#f3f7f9")
    formula(s, 518, 410, r"\pi_S(a_t\mid o_t,g,z_t)")
    node(s, 748, 346, 270, 98, "G1／PhysX 交互")
    note(s, 883, 402, "采集 Student 访问状态")
    note(s, 883, 427, "计算目标、落地与恢复回报")
    node(s, 1295, 322, 275, 98, "BC 初始化", RUST, "#faf6f3")
    note(s, 1432, 373, "用重标注轨迹拟合专家动作")
    formula(s, 1432, 400,
            r"L_{\mathrm{act}}=\mathbb{E}_{D_E}\,[\|\mu_S(o_t,g,z_t)-a_t^E\|_2^2]", 16)
    edge(s, "M 1432 186 V 322", RUST)
    note(s, 1418, 275, "实际位移标签与专家动作", 15, RUST, "end")
    edge(s, "M 1295 361 H 1134 V 292 H 518 V 346", RUST)
    note(s, 921, 283, "初始化策略参数", 15, RUST)
    edge(s, "M 300 395 H 405")
    edge(s, "M 630 395 H 748")
    formula(s, 689, 382, r"a_t", 18, BLUE)
    s.path("M 878 346 V 321 H 524", stroke=MUTED, sw=1.65, dash="5 4")
    edge(s, "M 512 321 H 165 V 346", MUTED, True)
    formula(s, 299, 313, r"o_{t+1}", 16, MUTED)

    node(s, 560, 499, 335, 86, "PPO 任务优化")
    formula(s, 728, 558, r"L_{\mathrm{PPO}}=L_{\mathrm{clip}}+c_vL_{\mathrm{value}}-c_eH(\pi_S)", 17)
    node(s, 970, 499, 420, 86, "DAgger 聚合监督", RUST, "#faf6f3")
    note(s, 1180, 548, "在访问状态上查询冻结的 Teacher", 16)
    note(s, 1180, 571, "聚合新标注样本以计算模仿损失", 16)
    edge(s, "M 804 444 V 476 H 728 V 499")
    edge(s, "M 960 444 V 476 H 1180 V 499", RUST, True)
    note(s, 741, 469, "交互样本与回报", 15, BLUE)
    note(s, 1094, 468, "访问状态与对应参考", 15, RUST)

    node(s, 405, 635, 737, 95, "联合损失与参数更新", BLUE, "#f3f7f9")
    formula(s, 773, 701, r"L_k=(1-\alpha_k)L_{\mathrm{PPO}}+\alpha_k L_{\mathrm{act}},"
            r"\quad\alpha_k=\max\left(0.1,\,1-\frac{k}{10000}\right)", 20)
    edge(s, "M 728 585 V 635")
    edge(s, "M 1180 585 V 609 H 998 V 635", RUST)
    formula(s, 1060, 601, r"L_{\mathrm{act}}", 16, RUST)
    edge(s, "M 405 683 H 375 V 472 H 465 V 444", BLUE)
    note(s, 358, 606, "更新策略", 15, BLUE, "end")
    s.line(30, 760, 1570, 760, stroke=RULE, sw=1, dash="5 4")

    section(s, 797, "(c) 目标条件闭环执行（G1 仿真）")
    node(s, 30, 840, 325, 108, "任务命令")
    formula(s, 192, 897, r"g=(\Delta x^*,\Delta y^*),\quad z_t", 20)
    note(s, 192, 929, "触发时锁存起跳局部坐标系下的目标", 15)
    node(s, 422, 840, 252, 108, "部署输入")
    formula(s, 548, 897, r"(o_t,g,z_t)", 20)
    formula(s, 548, 930, r"93+2+1=96", 17)
    node(s, 780, 840, 236, 108, "固定 Student 策略", BLUE, "#f3f7f9")
    formula(s, 898, 910, r"\pi_S^*(a_t\mid o_t,g,z_t)", 20)
    node(s, 1230, 840, 340, 108, "G1／PhysX")
    note(s, 1400, 899, "29 自由度仿真模型 · 50 Hz 控制")
    note(s, 1400, 927, "起跳 → 腾空 → 落地 → 恢复", 16)
    edge(s, "M 1142 683 H 1175 V 810 H 898 V 840")
    note(s, 1040, 801, "导出训练后的策略", 15, BLUE)
    for start, end in ((355, 422), (674, 780), (1016, 1230)):
        edge(s, f"M {start} 894 H {end}")
    formula(s, 1123, 861, r"a_t", 18, BLUE)
    note(s, 1123, 882, "29 维关节位置目标", 15, BLUE)
    edge(s, "M 1400 948 V 995 H 548 V 948", MUTED, True)
    note(s, 925, 985, "本体观测反馈", 16)
    formula(s, 1010, 985, r"o_{t+1}", 17, MUTED)
    note(s, 32, 985, "执行时仅使用图示输入", 16, MUTED, "start")

    s.parts.append("</svg>")
    path = OUT / "fig01_method_flow.svg"
    path.write_text("\n".join(s.parts), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    draw()
