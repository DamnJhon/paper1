#!/usr/bin/env python3
"""Generate a detailed method flowchart and a graphical abstract.

The two figures summarize ``../20261013-110211.md``.  They deliberately
separate training-only information from the deployable policy interface and
label all manuscript performance numbers as synthetic demonstration data.
"""

from __future__ import annotations

import base64
from pathlib import Path

from generate_figures import (
    BLUE,
    CYAN,
    DARK,
    GRAY,
    GREEN,
    GRID,
    LIGHT,
    MID,
    MINT,
    NAVY,
    ORANGE,
    ORANGE_BG,
    PURPLE,
    PURPLE_BG,
    RED,
    RED_BG,
    SKY,
    TEAL,
    WHITE,
    SVG,
    chip,
    esc,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "overview"
OUT.mkdir(exist_ok=True)


def save(svg: SVG, name: str) -> None:
    svg.parts.append("</svg>")
    (OUT / name).write_text("\n".join(svg.parts), encoding="utf-8")


def png_data_uri(path: Path) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def panel_title(svg: SVG, x: float, y: float, number: str, title: str, color: str) -> None:
    svg.circle(x, y, 24, fill=color, stroke=color, sw=0)
    svg.text(x, y + 8, number, 22, fill=WHITE, weight=700, anchor="middle")
    svg.text(x + 38, y + 8, title, 27, fill=color, weight=700)


def box(svg: SVG, x, y, w, h, title, lines, fill, stroke, title_size=23, body_size=19):
    svg.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2.5, rx=18)
    svg.text(x + w / 2, y + 38, title, title_size, fill=stroke, weight=700, anchor="middle")
    if lines:
        svg.multiline(x + w / 2, y + 72, lines, body_size, fill=DARK, weight=450, gap=1.42)


def flowchart() -> None:
    s = SVG(1800, 1050, "二维目标位移跳跃策略：训练、蒸馏与部署流程")
    s.text(900, 91, "完整参考只服务于训练；部署接口仅保留本体观测、目标位移和触发信号", 22,
           fill=GRAY, anchor="middle")

    # Swimlane backgrounds.
    lanes = [
        (45, 130, 420, 745, "A 参考族构建", SKY, BLUE),
        (490, 130, 515, 745, "B Teacher 与目标重标注", ORANGE_BG, ORANGE),
        (1030, 130, 725, 745, "C Student：DAgger-PPO 闭环", MINT, TEAL),
    ]
    for x, y, w, h, label, fill, stroke in lanes:
        s.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2.5, rx=24, opacity=0.36)
        chip(s, x + 20, y + 18, label, fill, stroke, min(w - 40, 330))

    # Lane A: reference construction.
    box(s, 85, 220, 340, 105, "跳跃动作数据库", ["姿态 · 速度 · 根节点", "足端接触 · 动作相位"], WHITE, BLUE)
    s.line(255, 328, 255, 365, stroke=BLUE, sw=4, arrow=True, arrow_id="arrow-blue")
    box(s, 85, 375, 340, 150, "运动特征近邻检索", ["姿态/速度相似性", "接触阶段一致性", "目标位移一致性"], WHITE, BLUE)
    s.line(255, 528, 255, 565, stroke=BLUE, sw=4, arrow=True, arrow_id="arrow-blue")
    box(s, 85, 575, 340, 170, "时空增强与筛选", ["平面旋转 · 幅度调整", "相位对齐 · 轨迹平滑", "限位/穿透/接触检查"], WHITE, BLUE)
    s.line(255, 748, 255, 785, stroke=BLUE, sw=4, arrow=True, arrow_id="arrow-blue")
    box(s, 85, 795, 340, 60, "多方向、多距离参考族", [], SKY, BLUE, title_size=22)

    # Lane B: teacher and relabeling.
    box(s, 535, 220, 425, 125, "参考轨迹条件 Teacher", ["输入：完整状态 sₜ", "相位 + 短时未来参考 rₜ"], WHITE, ORANGE)
    s.line(747, 348, 747, 385, stroke=ORANGE, sw=4, arrow=True)
    box(s, 535, 395, 425, 125, "动力学可执行轨迹", ["吸收接触与动力学约束", "输出专家动作 aₜᴱ"], WHITE, ORANGE)
    s.line(747, 523, 747, 560, stroke=PURPLE, sw=4, arrow=True)
    box(s, 535, 570, 425, 140, "实际起落位移重标注", ["Δp = p_land − p_takeoff", "用 Teacher 实际位移生成 g", "减少名义参考与执行偏差"], WHITE, PURPLE)
    s.line(747, 713, 747, 750, stroke=PURPLE, sw=4, arrow=True)
    box(s, 535, 760, 425, 95, "初始蒸馏数据集 Dᴱ", ["(oₜ, g, zₜ, aₜᴱ, sₜ₊₁)"], PURPLE_BG, PURPLE)

    # Cross-lane reference connection.
    s.path("M 425 825 C 470 825 480 282 525 282", stroke=BLUE, sw=4, arrow=True, arrow_id="arrow-blue")
    s.text(478, 525, "增强参考", 18, fill=BLUE, weight=700, anchor="middle")

    # Lane C: initial BC and DAgger-PPO loop.
    box(s, 1070, 220, 285, 110, "行为克隆初始化", ["L_act：模仿 Teacher", "获得可起跳初始策略"], WHITE, TEAL)
    box(s, 1435, 220, 280, 110, "Student 在线执行", ["按 π_S 访问自身状态", "暴露落地与恢复偏差"], WHITE, TEAL)
    s.line(1358, 275, 1423, 275, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    s.path("M 960 808 C 1015 808 1020 275 1058 275", stroke=PURPLE, sw=4, arrow=True)
    s.text(1020, 542, "初始数据", 18, fill=PURPLE, weight=700, anchor="middle")

    box(s, 1435, 390, 280, 120, "DAgger 专家查询", ["在 Student 访问状态上", "由冻结 Teacher 标注动作"], WHITE, ORANGE)
    s.line(1575, 333, 1575, 378, stroke=ORANGE, sw=4, arrow=True)
    box(s, 1070, 390, 285, 120, "任务回报", ["目标到达 · 方向一致", "安全落地 · 稳定恢复", "动作平滑"], WHITE, GREEN)

    box(s, 1190, 580, 405, 130, "聚合数据 + DAgger-PPO 联合更新", ["Lₖ = (1−αₖ)L_PPO + αₖL_act", "αₖ 递减，保留最低模仿权重"], WHITE, TEAL, title_size=22)
    s.path("M 1575 513 C 1575 550 1545 565 1525 575", stroke=ORANGE, sw=4, arrow=True)
    s.path("M 1212 513 C 1212 545 1240 562 1260 575", stroke=GREEN, sw=4, arrow=True, arrow_id="arrow-green")
    box(s, 1190, 770, 405, 75, "更新后的目标条件 Student", [], MINT, GREEN, title_size=23)
    s.line(1392, 713, 1392, 758, stroke=GREEN, sw=4, arrow=True, arrow_id="arrow-green")
    s.path("M 1598 808 C 1730 808 1730 165 1575 165 C 1470 165 1460 196 1460 208",
           stroke=TEAL, sw=3.5, dash="10 7", arrow=True, arrow_id="arrow-green")
    s.text(1692, 520, "下一轮 rollout", 18, fill=TEAL, weight=700,
           anchor="middle")

    # Deployment strip.
    s.rect(45, 905, 1710, 105, fill="#F7FBF9", stroke=GREEN, sw=2.5, rx=22)
    s.text(75, 945, "部署", 25, fill=GREEN, weight=700)
    chip(s, 170, 927, "本体观测 oₜ", WHITE, TEAL, 190)
    chip(s, 380, 927, "目标位移 g=(Δx*,Δy*)", WHITE, TEAL, 285)
    chip(s, 685, 927, "触发信号 zₜ", WHITE, TEAL, 180)
    s.line(880, 958, 1030, 958, stroke=GREEN, sw=4, arrow=True, arrow_id="arrow-green")
    box(s, 1045, 920, 260, 75, "Student 策略网络", [], MINT, GREEN, title_size=23)
    s.line(1315, 958, 1410, 958, stroke=GREEN, sw=4, arrow=True, arrow_id="arrow-green")
    chip(s, 1425, 927, "29 维关节位置动作", WHITE, GREEN, 260)
    s.text(900, 1033, "部署时不输入：动作相位、未来关节序列、完整根节点轨迹或在线动作检索",
           19, fill=RED, weight=650, anchor="middle")

    save(s, "method_training_flow.svg")


def graphical_abstract() -> None:
    s = SVG(1800, 1050, "面向二维目标位移命令的人形机器人跳跃策略学习")
    s.text(900, 90, "用完整参考教会机器人跳跃，再将能力蒸馏为低维目标条件反馈策略", 23,
           fill=GRAY, anchor="middle")

    # Three-part narrative.
    s.rect(45, 130, 390, 430, fill="#F8FAFD", stroke=BLUE, sw=2.5, rx=24)
    panel_title(s, 88, 178, "1", "任务接口", BLUE)
    s.text(240, 226, "起跳坐标系中的二维目标位移", 21, fill=NAVY, weight=650, anchor="middle")
    ox, oy = 210, 430
    s.line(ox, oy, ox + 145, oy, stroke=GRAY, sw=2.5, arrow=True)
    s.line(ox, oy, ox, oy - 145, stroke=GRAY, sw=2.5, arrow=True)
    s.text(365, oy + 8, "Δx*", 20, fill=GRAY, weight=650)
    s.text(ox - 10, oy - 155, "Δy*", 20, fill=GRAY, weight=650, anchor="end")
    s.line(ox, oy, ox + 110, oy - 95, stroke=ORANGE, sw=6, arrow=True)
    s.circle(ox, oy, 10, fill=BLUE, stroke=WHITE, sw=2)
    s.circle(ox + 110, oy - 95, 11, fill=ORANGE, stroke=WHITE, sw=2)
    s.text(294, 318, "g=(Δx*,Δy*)", 22, fill=ORANGE, weight=700, anchor="middle")
    s.text(240, 505, "只规定期望起落位置关系", 20, fill=DARK, weight=600, anchor="middle")
    s.text(240, 535, "不规定中间姿态与动作时序", 18, fill=GRAY, anchor="middle")

    s.rect(465, 130, 845, 430, fill="#FCFBFE", stroke=PURPLE, sw=2.5, rx=24)
    panel_title(s, 508, 178, "2", "训练阶段：完整参考 → 可部署能力", PURPLE)
    stages = [
        (500, "参考族", ["近邻检索", "旋转/幅度/筛选"], BLUE, SKY),
        (700, "Teacher", ["完整状态", "未来参考"], ORANGE, ORANGE_BG),
        (900, "位移重标注", ["Teacher 实际 Δp", "生成目标 g"], PURPLE, PURPLE_BG),
        (1100, "Student", ["DAgger + PPO", "模仿 + 任务回报"], TEAL, MINT),
    ]
    for x, title, lines, stroke, fill in stages:
        box(s, x, 250, 170, 180, title, lines, fill, stroke, title_size=21, body_size=17)
    for x1, x2, color, arrow_id in [(670, 700, NAVY, "arrow"), (870, 900, NAVY, "arrow"),
                                      (1070, 1100, NAVY, "arrow")]:
        s.line(x1 + 3, 340, x2 - 9, 340, stroke=color, sw=4, arrow=True, arrow_id=arrow_id)
    s.rect(515, 465, 750, 60, fill=WHITE, stroke=MID, sw=1.5, rx=14, dash="8 6")
    s.text(890, 503, "训练信息更强：完整参考、相位和仿真特权状态仅在此区域出现", 19,
           fill=GRAY, weight=600, anchor="middle")

    s.rect(1340, 130, 415, 430, fill="#F7FBF9", stroke=GREEN, sw=2.5, rx=24)
    panel_title(s, 1383, 178, "3", "部署阶段", GREEN)
    chip(s, 1385, 230, "本体观测 oₜ", WHITE, TEAL, 150)
    chip(s, 1548, 230, "目标 g + 触发 zₜ", WHITE, TEAL, 170)
    s.line(1460, 282, 1510, 325, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    s.line(1630, 282, 1580, 325, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    box(s, 1435, 335, 225, 105, "Student", ["目标条件反馈策略"], MINT, GREEN, title_size=25, body_size=19)
    s.line(1547, 443, 1547, 475, stroke=GREEN, sw=4, arrow=True, arrow_id="arrow-green")
    chip(s, 1420, 485, "29 维关节位置动作", WHITE, GREEN, 255)
    s.text(1547, 545, "无需未来参考或在线动作检索", 18, fill=RED, weight=650, anchor="middle")

    # Generated jump sequence reused as a visual anchor.
    s.rect(45, 595, 1710, 265, fill=WHITE, stroke=GRID, sw=2, rx=22)
    s.raw('<clipPath id="jumpclip"><rect x="60" y="610" width="1680" height="235" rx="16"/></clipPath>')
    href = png_data_uri(HERE / "fig05_jump_sequence_raw.png")
    s.raw(
        f'<image x="60" y="610" width="1680" height="235" xlink:href="{esc(href)}" '
        'preserveAspectRatio="xMidYMid slice" clip-path="url(#jumpclip)"/>'
    )
    s.rect(62, 615, 350, 45, fill=WHITE, stroke=WHITE, sw=0, rx=12, opacity=0.88)
    s.text(82, 646, "目标条件跳跃：准备 → 起跳 → 腾空 → 落地 → 恢复", 20, fill=NAVY, weight=700)
    s.rect(1365, 795, 355, 42, fill=WHITE, stroke=WHITE, sw=0, rx=12, opacity=0.88)
    s.text(1700, 823, "AI 生成动作示意，非仿真结果", 17, fill=GRAY, anchor="end")

    # Bottom: success definition and headline manuscript numbers.
    s.text(55, 905, "联合成功判据", 22, fill=NAVY, weight=700)
    criteria = [
        (225, "有效起跳", BLUE, SKY),
        (390, "目标到达", ORANGE, ORANGE_BG),
        (555, "安全落地", PURPLE, PURPLE_BG),
        (720, "稳定恢复", GREEN, MINT),
    ]
    for i, (x, label, color, fill) in enumerate(criteria):
        chip(s, x, 880, label, fill, color, 140)
        if i < len(criteria) - 1:
            s.text(x + 151, 909, "×", 24, fill=MID, weight=700, anchor="middle")

    stats = [
        (940, "91.3%", "已见目标成功率", GREEN),
        (1160, "0.061 m", "平均目标误差", BLUE),
        (1380, "82.9%", "组合留出成功率", PURPLE),
        (1600, "79.8%", "联合随机化成功率", ORANGE),
    ]
    for x, value, label, color in stats:
        s.text(x, 905, value, 27, fill=color, weight=750, anchor="middle")
        s.text(x, 935, label, 17, fill=GRAY, anchor="middle")
    s.text(900, 990, "注：以上性能数字来自论文中的合成演示数据，不得作为真实实验结果用于投稿或答辩",
           18, fill=RED, weight=650, anchor="middle")
    s.text(900, 1022, "核心贡献：把完整参考从“部署依赖”转化为“训练资源”", 23,
           fill=NAVY, weight=700, anchor="middle")

    save(s, "graphical_abstract.svg")


def main() -> None:
    flowchart()
    graphical_abstract()
    print(f"Generated overview figures in {OUT}")


if __name__ == "__main__":
    main()
