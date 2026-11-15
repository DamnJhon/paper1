"""Generate the compact paper figure using the original drawing primitives."""

from generate_method_flow import BLUE, MUTED, OUT, RULE, RUST, SVG, edge, formula, node, note, section


def draw():
    s = SVG(1600, 840)
    for name, color in (("flow", BLUE), ("supervision", RUST), ("feedback", MUTED)):
        s.raw(f'<defs><marker id="{name}" markerWidth="7" markerHeight="7" refX="7" '
              f'refY="3.5" orient="auto" markerUnits="userSpaceOnUse">'
              f'<path d="M0 0 L7 3.5 L0 7 Z" fill="{color}"/></marker></defs>')

    section(s, 35, "(a) 参考构建与专家数据采集")
    node(s, 30, 65, 302, 88, "离线参考增强")
    note(s, 181, 125, "近邻检索、变换与可行性筛选", 17)
    node(s, 418, 65, 243, 88, "Teacher 参考跟踪", BLUE, "#f3f7f9")
    formula(s, 540, 126, r"\pi_E(a_t\mid s_t,r_t)")
    node(s, 752, 65, 255, 88, "G1／PhysX")
    note(s, 880, 125, "冻结 Teacher 后采集轨迹", 17)
    node(s, 1114, 65, 456, 88, "实际位移重标注", RUST, "#faf6f3")
    formula(s, 1342, 126, r"g_i=\Delta p_i^{\mathrm{actual}}")
    for start, end in ((332, 418), (661, 752), (1007, 1114)):
        edge(s, f"M {start} 109 H {end}")
    formula(s, 375, 98, r"r_t", 17, BLUE)
    formula(s, 706, 98, r"a_t^E", 17, BLUE)
    edge(s, "M 880 153 V 180 H 540 V 153", MUTED, True)
    note(s, 710, 173, "状态反馈", 15)
    s.line(30, 203, 1570, 203, stroke=RULE, sw=1)

    section(s, 236, "(b) Student 初始化与联合训练")
    node(s, 1230, 274, 340, 82, "BC 初始化", RUST, "#faf6f3")
    note(s, 1400, 332, "拟合专家动作", 17)
    edge(s, "M 1400 153 V 274", RUST)
    note(s, 1349, 230, "重标注专家数据", 16, RUST, "end")
    formula(s, 1368, 230, r"D_E", 17, RUST)

    node(s, 885, 274, 262, 82, "当前 Student", BLUE, "#f3f7f9")
    formula(s, 1016, 333, r"\pi_S(a_t\mid o_t,g,z_t)")
    node(s, 500, 274, 276, 82, "G1／PhysX 交互")
    note(s, 638, 332, "执行当前策略并采样", 17)
    edge(s, "M 1230 315 H 1147", RUST)
    edge(s, "M 885 315 H 776")
    formula(s, 830, 303, r"a_t", 17, BLUE)
    edge(s, "M 638 274 V 253 H 1016 V 274", MUTED, True)
    formula(s, 822, 246, r"o_{t+1}", 16, MUTED)

    node(s, 416, 407, 276, 73, "PPO 任务优化")
    note(s, 554, 461, "交互样本与任务回报", 16)
    node(s, 742, 407, 324, 73, "DAgger 聚合监督", RUST, "#faf6f3")
    note(s, 904, 461, "在访问状态上查询冻结的 Teacher", 16)
    edge(s, "M 554 356 V 407")
    edge(s, "M 731 356 V 382 H 904 V 407", RUST)
    edge(s, "M 554 480 V 526")
    edge(s, "M 904 480 V 526", RUST)

    node(s, 500, 526, 566, 82, "联合损失与参数更新", BLUE, "#f3f7f9")
    formula(s, 783, 585,
            r"L_k=(1-\alpha_k)L_{\mathrm{PPO}}+\alpha_k L_{\mathrm{act}}", 21)
    edge(s, "M 1066 567 H 1178 V 379 H 1106 V 356")
    note(s, 1192, 475, "更新策略", 16, BLUE, "start")
    s.line(30, 637, 1570, 637, stroke=RULE, sw=1, dash="5 4")

    section(s, 670, "(c) 目标条件闭环执行（G1 仿真）")
    node(s, 30, 706, 478, 87, "部署输入（96 维）")
    formula(s, 269, 768, r"(o_t,g,z_t),\quad g=(\Delta x^*,\Delta y^*)", 20)
    node(s, 662, 706, 242, 87, "固定 Student", BLUE, "#f3f7f9")
    formula(s, 783, 768, r"\pi_S^*(a_t\mid o_t,g,z_t)", 20)
    node(s, 1190, 706, 380, 87, "G1／PhysX")
    note(s, 1380, 768, "50 Hz 闭环控制", 17)
    edge(s, "M 783 608 V 706")
    note(s, 797, 678, "导出策略", 16, BLUE, "start")
    edge(s, "M 508 749 H 662")
    edge(s, "M 904 749 H 1190")
    note(s, 1047, 738, "29 维关节位置目标", 16, BLUE)
    edge(s, "M 1380 793 V 822 H 269 V 793", MUTED, True)
    formula(s, 820, 814, r"o_{t+1}", 17, MUTED)

    s.parts.append("</svg>")
    path = OUT / "fig01_method_flow_compact.svg"
    path.write_text("\n".join(s.parts), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    draw()
