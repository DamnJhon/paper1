"""Draw the paper's methodological contributions in their data-flow order."""

import argparse
from base64 import b64encode

from generate_method_flow import BLUE, INK, MUTED, OUT, RULE, RUST, SVG, edge, formula
from generate_method_flow import node as draw_node, note as draw_note, section as draw_section


ENGLISH = {
    "(a) 以实际起落位移重标注专家轨迹": "(a) Expert relabeling with realized jump displacement",
    "(b) 在 Student 访问状态上联合蒸馏与优化": "(b) Joint distillation and optimization on student-visited states",
    "参考轨迹增强": "Augment references",
    "Teacher 跟踪": "Teacher tracking",
    "完整参考与仿真状态": "Full reference and sim state",
    "G1 仿真采样": "G1 rollouts",
    "冻结 Teacher 后采集轨迹": "Frozen teacher",
    "Unitree G1 跳跃姿态示意": "Illustrative Unitree G1 jump poses",
    "起跳": "Takeoff",
    "实际落点": "Actual landing",
    "名义落点": "Nominal target",
    "重标注专家数据": "Relabeled data",
    "按起跳局部坐标系中的实际基座位移标注专家动作":
        "Label expert actions with realized base displacement in the takeoff frame.",
    "地面标记表示基座水平投影": "Markers show the robot base projected onto the ground.",
    "BC 初始化": "BC initialization",
    "拟合专家动作": "Fit expert actions",
    "当前 Student": "Current student",
    "G1／PhysX 交互": "G1 / PhysX interaction",
    "采样 Student 执行轨迹": "Collect student rollouts",
    "Student 用自身策略采样，再由专家动作与任务回报共同更新":
        "The student collects its own rollouts and learns from expert actions and task rewards.",
    "DAgger 专家监督": "DAgger supervision",
    "在访问状态上查询冻结 Teacher": "Query teacher on visited states",
    "PPO 任务优化": "PPO task optimization",
    "目标到达、落地与恢复回报": "Goal, landing, recovery rewards",
    "联合更新 Student": "Joint student update",
    "参数更新": "Update policy",
    "(c) 以二维目标位移指挥跳跃（G1 仿真）": "(c) Jump control with a 2D displacement command (G1 simulation)",
    "二维目标命令与本体反馈": "2D goal command and proprioception",
    "方向与距离由目标向量给定 · 输入共 96 维":
        "The goal specifies direction and distance · 96 input dimensions",
    "固定 Student": "Frozen student",
    "G1／PhysX": "G1 / PhysX",
    "50 Hz 控制": "50 Hz control",
    "导出策略": "Export policy",
    "29 维关节位置目标": "29 joint position targets",
    "评价维度   目标误差 · 落地安全 · 稳定恢复 · 未见目标泛化":
        "Evaluation · Target error · Landing safety · Stable recovery · Generalization to unseen goals",
}


def pose(svg, name, x, y, width, height):
    pixels = (OUT / "g1_poses" / f"{name}.png").read_bytes()
    svg.image(x, y, width, height, "data:image/png;base64," + b64encode(pixels).decode("ascii"))


def draw(english=False):
    s = SVG(1600, 870)

    def translated(label):
        return ENGLISH[label] if english else label

    def note(svg, x, y, label, *args):
        draw_note(svg, x, y, translated(label), *args)

    def node(svg, x, y, w, h, label, *args):
        draw_node(svg, x, y, w, h, translated(label), *args)

    def section(svg, y, label):
        draw_section(svg, y, translated(label))

    for name, color in (("flow", BLUE), ("supervision", RUST), ("feedback", MUTED)):
        s.raw(f'<defs><marker id="{name}" markerWidth="7" markerHeight="7" refX="7" '
              f'refY="3.5" orient="auto" markerUnits="userSpaceOnUse">'
              f'<path d="M0 0 L7 3.5 L0 7 Z" fill="{color}"/></marker></defs>')

    section(s, 40, "(a) 以实际起落位移重标注专家轨迹")
    s.text(731, 40, translated("(b) 在 Student 访问状态上联合蒸馏与优化"), 22, fill=INK, weight=650)
    s.line(711, 64, 711, 570, stroke=RULE, sw=1)

    note(s, 104, 96, "参考轨迹增强", 16 if english else 18, INK)
    note(s, 318, 96, "Teacher 跟踪", 18, INK)
    note(s, 318, 121, "完整参考与仿真状态", 15)
    note(s, 545, 96, "G1 仿真采样", 18, INK)
    edge(s, "M 192 90 H 239" if english else "M 169 90 H 241")
    edge(s, "M 400 90 H 482" if english else "M 391 90 H 468")
    formula(s, 205, 79, r"r_t", 16, BLUE)
    formula(s, 430, 79, r"a_t^E", 16, BLUE)
    note(s, 545, 121, "冻结 Teacher 后采集轨迹", 15)

    # Project the base positions onto an unscaled ground line.
    note(s, 45, 163, "Unitree G1 跳跃姿态示意", 17, INK, "start")
    pose(s, "takeoff", 77, 227, 82, 176)
    pose(s, "flight", 195, 174, 89, 151)
    pose(s, "landing", 305, 251, 83, 152)
    s.line(46, 403, 467, 403, stroke=RULE, sw=1.4)
    s.circle(126, 403, 4.5, fill=INK, stroke=INK, sw=0)
    s.circle(355, 403, 5.5, fill=RUST, stroke=RUST, sw=0)
    s.circle(455, 403, 5.5, fill="#ffffff", stroke=MUTED, sw=1.6)
    note(s, 126, 429, "起跳", 16)
    note(s, 343, 429, "实际落点", 16, RUST, "end")
    note(s, 433 if english else 451, 429, "名义落点", 15 if english else 16, MUTED)
    s.line(126, 445, 126, 468, stroke=RULE, sw=1)
    s.line(126, 460, 355, 460, stroke=RUST, sw=1.4)
    edge(s, "M 355 409 V 460 H 493 V 308 H 514", RUST)
    formula(s, 239, 485, r"g_i\leftarrow\Delta p_i^{\mathrm{actual}}", 18, RUST)
    node(s, 514, 270, 176, 76, "重标注专家数据", RUST, "#faf6f3")
    formula(s, 602, 328, "D_E", 20, RUST)
    note(s, 45, 524, "按起跳局部坐标系中的实际基座位移标注专家动作", 17, INK, "start")
    note(s, 45, 550, "地面标记表示基座水平投影", 15, MUTED, "start")

    # Teacher labels and task returns train the same policy.
    node(s, 733, 270, 164, 76, "BC 初始化", RUST, "#faf6f3")
    note(s, 815, 327, "拟合专家动作", 16)
    node(s, 956, 270, 238, 76, "当前 Student", BLUE, "#f3f7f9")
    formula(s, 1075, 327, r"\pi_S(a_t\mid o_t,g,z_t)", 19)
    node(s, 1286, 270, 279, 76, "G1／PhysX 交互")
    note(s, 1425, 327, "采样 Student 执行轨迹", 16)
    edge(s, "M 690 308 H 733", RUST)
    edge(s, "M 897 308 H 956", RUST)
    edge(s, "M 1194 308 H 1286")
    formula(s, 1240, 297, "a_t", 16, BLUE)
    edge(s, "M 1425 270 V 229 H 1075 V 270", MUTED, True)
    formula(s, 1250, 218, "o_{t+1}", 17, MUTED)
    note(s, 1075, 154, "Student 用自身策略采样，再由专家动作与任务回报共同更新", 17, INK)

    node(s, 1005, 388, 280, 72, "DAgger 专家监督", RUST, "#faf6f3")
    note(s, 1145, 441, "在访问状态上查询冻结 Teacher", 15)
    node(s, 1310, 388, 255, 72, "PPO 任务优化", BLUE, "#f3f7f9")
    note(s, 1437, 441, "目标到达、落地与恢复回报", 15)
    edge(s, "M 1332 346 V 368 H 1145 V 388", RUST)
    edge(s, "M 1474 346 V 388")

    node(s, 1005, 510, 560, 75, "联合更新 Student", BLUE, "#f3f7f9")
    formula(s, 1285, 567,
            r"L_k=(1-\alpha_k)L_{\mathrm{PPO}}+\alpha_k L_{\mathrm{act}}", 20)
    edge(s, "M 1145 460 V 510", RUST)
    edge(s, "M 1437 460 V 510")
    edge(s, "M 1005 547 H 928 V 365 H 1026 V 346")
    note(s, 914, 457, "参数更新", 15, BLUE, "end")
    s.line(30, 616, 1570, 616, stroke=RULE, sw=1.15, dash="5 4")

    section(s, 650, "(c) 以二维目标位移指挥跳跃（G1 仿真）")
    node(s, 30, 685, 500, 92, "二维目标命令与本体反馈", BLUE, "#f3f7f9")
    formula(s, 280, 740, r"g=(\Delta x^*,\Delta y^*),\quad (o_t,g,z_t)", 19)
    note(s, 280, 764, "方向与距离由目标向量给定 · 输入共 96 维", 15)
    node(s, 697, 685, 254, 92, "固定 Student", BLUE, "#f3f7f9")
    formula(s, 824, 748, r"\pi_S^*(a_t\mid o_t,g,z_t)", 20)
    node(s, 1197, 685, 368, 92, "G1／PhysX")
    note(s, 1381, 747, "50 Hz 控制", 17)
    edge(s, "M 1285 585 V 636 H 824 V 685")
    note(s, 1060, 658, "导出策略", 16, BLUE)
    edge(s, "M 530 731 H 697")
    edge(s, "M 951 731 H 1197")
    note(s, 1074, 720, "29 维关节位置目标", 16, BLUE)
    edge(s, "M 1381 777 V 814 H 280 V 777", MUTED, True)
    formula(s, 824, 806, "o_{t+1}", 17, MUTED)
    note(s, 30, 850, "评价维度   目标误差 · 落地安全 · 稳定恢复 · 未见目标泛化", 16, MUTED, "start")

    s.parts.append("</svg>")
    suffix = "_en" if english else ""
    path = OUT / f"fig01_method_flow_unitree_g1{suffix}.svg"
    path.write_text("\n".join(s.parts), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english", action="store_true")
    draw(english=parser.parse_args().english)
