#!/usr/bin/env python3
"""Generate editable SVG figures for the 1013 paper draft.

All numerical plots use the synthetic data declared in the manuscript.
The script only depends on the Python standard library.
"""

from __future__ import annotations

import html
import base64
import math
import random
from pathlib import Path


OUT = Path(__file__).resolve().parent

NAVY = "#183B56"
BLUE = "#2F6BFF"
SKY = "#EAF1FF"
CYAN = "#27A7B8"
TEAL = "#178C7B"
GREEN = "#2FA36B"
MINT = "#E8F6F1"
ORANGE = "#F28E2B"
ORANGE_BG = "#FFF1E2"
RED = "#D9544D"
RED_BG = "#FDECEB"
PURPLE = "#8064C6"
PURPLE_BG = "#F0ECFA"
GRAY = "#607080"
MID = "#A9B4BF"
LIGHT = "#F5F7FA"
GRID = "#DDE3EA"
DARK = "#18232D"
WHITE = "#FFFFFF"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


class SVG:
    def __init__(self, width: int = 1600, height: int = 900, title: str = ""):
        self.width = width
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            "<defs>",
            '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">'
            f'<path d="M0,0 L12,6 L0,12 z" fill="{NAVY}"/></marker>',
            '<marker id="arrow-blue" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">'
            f'<path d="M0,0 L12,6 L0,12 z" fill="{BLUE}"/></marker>',
            '<marker id="arrow-green" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">'
            f'<path d="M0,0 L12,6 L0,12 z" fill="{GREEN}"/></marker>',
            '<linearGradient id="bluegrad" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{SKY}"/><stop offset="1" stop-color="#D9E8FF"/></linearGradient>',
            '<linearGradient id="heat" x1="0" y1="1" x2="0" y2="0">'
            '<stop offset="0" stop-color="#EDF2F7"/><stop offset="0.35" stop-color="#A9D7D0"/>'
            '<stop offset="0.7" stop-color="#42A88F"/><stop offset="1" stop-color="#136C64"/></linearGradient>',
            "</defs>",
            f'<rect width="{width}" height="{height}" fill="white"/>',
        ]
        if title:
            self.text(width / 2, 54, title, 34, weight=700, anchor="middle", fill=NAVY)

    def raw(self, value: str) -> None:
        self.parts.append(value)

    def rect(self, x, y, w, h, fill=WHITE, stroke=NAVY, sw=2, rx=16, dash=None, opacity=1.0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'
        )

    def line(self, x1, y1, x2, y2, stroke=NAVY, sw=3, dash=None, arrow=False, arrow_id="arrow"):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker = f' marker-end="url(#{arrow_id})"' if arrow else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round"{dash_attr}{marker}/>'
        )

    def path(self, d, fill="none", stroke=NAVY, sw=3, dash=None, arrow=False, arrow_id="arrow", opacity=1.0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker = f' marker-end="url(#{arrow_id})"' if arrow else ""
        self.parts.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{dash_attr}{marker}/>'
        )

    def circle(self, cx, cy, r, fill=WHITE, stroke=NAVY, sw=2, opacity=1.0):
        self.parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def ellipse(self, cx, cy, rx, ry, fill="none", stroke=NAVY, sw=2, dash=None, opacity=1.0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'
        )

    def polygon(self, points, fill=NAVY, stroke=NAVY, sw=1, opacity=1.0):
        pts = " ".join(f"{x},{y}" for x, y in points)
        self.parts.append(
            f'<polygon points="{pts}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def text(self, x, y, value, size=26, fill=DARK, weight=400, anchor="start", family="Noto Sans CJK SC, sans-serif", italic=False):
        style = "italic" if italic else "normal"
        self.parts.append(
            f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" font-style="{style}" text-anchor="{anchor}">{esc(value)}</text>'
        )

    def multiline(self, x, y, lines, size=24, fill=DARK, weight=400, anchor="middle", gap=1.35):
        self.parts.append(
            f'<text x="{x}" y="{y}" fill="{fill}" font-family="Noto Sans CJK SC, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">'
        )
        for i, value in enumerate(lines):
            dy = 0 if i == 0 else size * gap
            self.parts.append(f'<tspan x="{x}" dy="{dy}">{esc(value)}</tspan>')
        self.parts.append("</text>")

    def image(self, x, y, w, h, href, preserve="xMidYMid meet"):
        self.parts.append(
            f'<image x="{x}" y="{y}" width="{w}" height="{h}" xlink:href="{esc(href)}" '
            f'preserveAspectRatio="{preserve}"/>'
        )

    def save(self, name: str):
        self.parts.append("</svg>")
        (OUT / name).write_text("\n".join(self.parts), encoding="utf-8")


def chip(svg, x, y, text, fill, color=NAVY, w=None):
    w = w or max(100, 22 * len(text) + 30)
    svg.rect(x, y, w, 42, fill=fill, stroke=fill, sw=0, rx=21)
    svg.text(x + w / 2, y + 29, text, 19, fill=color, weight=600, anchor="middle")


def footer(svg, text="虚构仿真数据，仅用于论文写作演示"):
    svg.text(svg.width - 30, svg.height - 22, text, 17, fill=GRAY, anchor="end")


def axes(svg, x, y, w, h, xmin, xmax, ymin, ymax, xlabel, ylabel, x_ticks, y_ticks):
    svg.line(x, y + h, x + w, y + h, stroke=DARK, sw=2)
    svg.line(x, y, x, y + h, stroke=DARK, sw=2)
    for value in x_ticks:
        px = x + (value - xmin) / (xmax - xmin) * w
        svg.line(px, y, px, y + h, stroke=GRID, sw=1)
        svg.line(px, y + h, px, y + h + 8, stroke=DARK, sw=2)
        svg.text(px, y + h + 34, f"{value:g}", 18, fill=GRAY, anchor="middle")
    for value in y_ticks:
        py = y + h - (value - ymin) / (ymax - ymin) * h
        svg.line(x, py, x + w, py, stroke=GRID, sw=1)
        svg.line(x - 8, py, x, py, stroke=DARK, sw=2)
        svg.text(x - 16, py + 6, f"{value:g}", 18, fill=GRAY, anchor="end")
    svg.text(x + w / 2, y + h + 70, xlabel, 23, weight=600, anchor="middle")
    label_x, label_y = x - 72, y + h / 2
    svg.raw(
        f'<text x="{label_x}" y="{label_y}" transform="rotate(-90 {label_x} {label_y})" '
        f'fill="{DARK}" font-family="Noto Sans CJK SC, sans-serif" font-size="23" '
        f'font-weight="600" text-anchor="middle">{esc(ylabel)}</text>'
    )
    return (
        lambda vx: x + (vx - xmin) / (xmax - xmin) * w,
        lambda vy: y + h - (vy - ymin) / (ymax - ymin) * h,
    )


def fig01_framework():
    s = SVG(title="训练阶段利用完整参考，部署阶段仅保留二维目标位移命令")
    chip(s, 70, 88, "阶段 I 参考构建", SKY, BLUE, 250)
    chip(s, 395, 88, "阶段 II Teacher", ORANGE_BG, ORANGE, 230)
    chip(s, 720, 88, "阶段 III 重标注", PURPLE_BG, PURPLE, 245)
    chip(s, 1055, 88, "阶段 IV Student", MINT, TEAL, 240)
    chip(s, 1350, 88, "部署", "#EAF5F0", GREEN, 150)

    boxes = [
        (55, 180, 255, 150, SKY, BLUE, ["跳跃动作数据库", "姿态 · 速度 · 接触"]),
        (360, 180, 270, 150, ORANGE_BG, ORANGE, ["参考轨迹条件 Teacher", "完整状态 + 未来参考"]),
        (690, 180, 270, 150, PURPLE_BG, PURPLE, ["实际起落位移标注", "g = (Δx*, Δy*)"]),
        (1020, 180, 270, 150, MINT, TEAL, ["DAgger-PPO Student", "模仿 + 任务回报"]),
        (1340, 180, 210, 150, "#EAF5F0", GREEN, ["低层策略", "29维关节动作"]),
    ]
    for x, y, w, h, fill, stroke, lines in boxes:
        s.rect(x, y, w, h, fill=fill, stroke=stroke, sw=3, rx=22)
        s.multiline(x + w / 2, y + 55, lines, 23 if w > 220 else 21, weight=650, gap=1.5)
    for x1, x2 in [(310, 360), (630, 690), (960, 1020), (1290, 1340)]:
        s.line(x1 + 8, 255, x2 - 12, 255, stroke=NAVY, sw=4, arrow=True)

    s.rect(55, 380, 905, 380, fill="#FBFCFE", stroke=MID, sw=2, rx=22, dash="10 8")
    s.text(85, 425, "仅训练阶段使用", 25, fill=GRAY, weight=700)
    s.rect(85, 465, 250, 220, fill=WHITE, stroke=BLUE, sw=2, rx=18)
    s.text(210, 510, "离线数据增强", 25, weight=700, anchor="middle", fill=BLUE)
    for i, txt in enumerate(["近邻检索", "方向旋转", "幅度筛选", "可行性检查"]):
        chip(s, 125, 535 + i * 38, txt, SKY, BLUE, 170)
    s.rect(375, 465, 250, 220, fill=WHITE, stroke=ORANGE, sw=2, rx=18)
    s.text(500, 510, "Teacher监督", 25, weight=700, anchor="middle", fill=ORANGE)
    s.multiline(500, 555, ["动作相位", "短时未来姿态", "参考足端与接触", "仿真完整状态"], 21, gap=1.55)
    s.rect(665, 465, 250, 220, fill=WHITE, stroke=PURPLE, sw=2, rx=18)
    s.text(790, 510, "轨迹重标注", 25, weight=700, anchor="middle", fill=PURPLE)
    s.multiline(790, 560, ["名义参考位移", "↓", "Teacher实际位移", "形成目标条件数据"], 21, gap=1.45)

    s.rect(1015, 380, 535, 380, fill="#F7FBF9", stroke=GREEN, sw=3, rx=22)
    s.text(1050, 425, "部署阶段保留", 25, fill=GREEN, weight=700)
    s.rect(1055, 475, 195, 110, fill=WHITE, stroke=TEAL, sw=2, rx=18)
    s.multiline(1152, 518, ["本体观测", "oₜ"], 24, weight=650, gap=1.35)
    s.rect(1055, 620, 195, 110, fill=WHITE, stroke=TEAL, sw=2, rx=18)
    s.multiline(1152, 663, ["目标命令", "g = (Δx*, Δy*)"], 22, weight=650, gap=1.35)
    s.rect(1320, 525, 185, 130, fill=MINT, stroke=GREEN, sw=3, rx=22)
    s.multiline(1412, 572, ["Student", "策略网络"], 25, weight=700, gap=1.35)
    s.line(1250, 530, 1300, 570, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    s.line(1250, 675, 1300, 610, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    s.text(800, 830, "核心：参考轨迹是训练资源，而不是部署时必须持续提供的控制命令", 27, fill=NAVY, weight=700, anchor="middle")
    s.save("fig01_overall_framework.svg")


def fig02_target_command():
    s = SVG(title="二维目标位移命令及坐标定义")
    # Left: coordinate geometry
    s.rect(45, 100, 960, 720, fill="#FCFDFE", stroke=GRID, sw=2, rx=22)
    ox, oy = 350, 620
    s.line(ox, oy, ox + 430, oy, stroke=GRAY, sw=3, arrow=True)
    s.line(ox, oy, ox, oy - 390, stroke=GRAY, sw=3, arrow=True)
    s.text(800, oy + 10, "世界坐标 Xᴡ", 22, fill=GRAY)
    s.text(ox - 15, 205, "世界坐标 Yᴡ", 22, fill=GRAY, anchor="end")
    # Frozen local axes rotated slightly
    angle = -18 * math.pi / 180
    ux = (math.cos(angle), math.sin(angle))
    uy = (-math.sin(angle), math.cos(angle))
    s.line(ox, oy, ox + 230 * ux[0], oy - 230 * ux[1], stroke=BLUE, sw=5, arrow=True, arrow_id="arrow-blue")
    s.line(ox, oy, ox + 200 * uy[0], oy - 200 * uy[1], stroke=BLUE, sw=5, arrow=True, arrow_id="arrow-blue")
    s.text(ox + 250 * ux[0], oy - 250 * ux[1], "xᴮ⁰（前）", 23, fill=BLUE, weight=700)
    s.text(ox + 210 * uy[0], oy - 210 * uy[1], "yᴮ⁰（左）", 23, fill=BLUE, weight=700)
    s.circle(ox, oy, 14, fill=BLUE, stroke=WHITE, sw=3)
    s.text(ox, oy + 42, "起跳位置 p_takeoff", 22, weight=700, anchor="middle")

    gx, gy = 760, 350
    lx, ly = 720, 385
    s.circle(gx, gy, 16, fill=ORANGE, stroke=WHITE, sw=3)
    s.text(gx + 14, gy - 25, "期望目标 p_target", 22, fill=ORANGE, weight=700, anchor="middle")
    s.circle(lx, ly, 14, fill=GREEN, stroke=WHITE, sw=3)
    s.text(lx + 30, ly + 45, "实际落点 p_land", 22, fill=GREEN, weight=700, anchor="middle")
    s.line(ox + 12, oy - 12, gx - 18, gy + 12, stroke=ORANGE, sw=6, arrow=True)
    s.text(575, 440, "目标命令 g", 25, fill=ORANGE, weight=700, anchor="middle")
    s.line(ox + 12, oy - 4, lx - 16, ly + 12, stroke=GREEN, sw=5, arrow=True, arrow_id="arrow-green")
    s.text(560, 520, "实际位移 Δp", 24, fill=GREEN, weight=700, anchor="middle")
    s.line(lx, ly, gx, gy, stroke=RED, sw=3, dash="8 6", arrow=True)
    s.text(770, 408, "误差 eₚ", 22, fill=RED, weight=700)
    s.path(f"M {ox} {oy} A 120 120 0 0 0 {ox + 110} {oy - 50}", stroke=BLUE, sw=2, dash="6 5")
    s.text(425, 575, "起跳时锁定航向", 20, fill=BLUE)

    # Right definition card
    s.rect(1040, 100, 515, 720, fill=WHITE, stroke=NAVY, sw=2, rx=22)
    s.text(1297, 155, "命令语义", 28, fill=NAVY, weight=700, anchor="middle")
    s.rect(1090, 195, 415, 108, fill=SKY, stroke=BLUE, sw=2, rx=16)
    s.text(1297, 242, "g = (Δx*, Δy*)", 31, fill=BLUE, weight=700, anchor="middle")
    s.text(1297, 278, "前后位移 + 左右位移", 21, fill=GRAY, anchor="middle")
    items = [
        ("坐标系", "起跳瞬间锁定的机体航向坐标系"),
        ("更新时间", "触发起跳时锁存，恢复完成后释放"),
        ("表达内容", "期望起落位置关系"),
        ("不包含", "动作相位、未来姿态、足端轨迹"),
        ("评价量", "eₚ = ‖Δp − g‖₂"),
    ]
    for i, (key, value) in enumerate(items):
        yy = 350 + i * 82
        s.text(1095, yy, key, 22, fill=TEAL, weight=700)
        s.text(1215, yy, value, 20, fill=DARK)
        if i < len(items) - 1:
            s.line(1090, yy + 25, 1505, yy + 25, stroke=GRID, sw=1)
    s.rect(1090, 730, 415, 55, fill=ORANGE_BG, stroke=ORANGE_BG, sw=0, rx=12)
    s.text(1297, 765, "“紧凑”仅指相对完整参考轨迹减少过程信息", 18, fill=ORANGE, weight=650, anchor="middle")
    s.save("fig02_target_displacement_command.svg")


def fig03_augmentation():
    s = SVG(title="基于运动特征近邻检索的参考数据增强")
    stages = [
        (55, "原始动作片段", SKY, BLUE),
        (365, "运动特征检索", PURPLE_BG, PURPLE),
        (675, "几何与时序变换", ORANGE_BG, ORANGE),
        (985, "可行性筛选", RED_BG, RED),
        (1295, "参考目标覆盖", MINT, TEAL),
    ]
    for x, title, fill, stroke in stages:
        s.rect(x, 150, 250, 520, fill=fill, stroke=stroke, sw=3, rx=22)
        s.text(x + 125, 200, title, 25, fill=stroke, weight=700, anchor="middle")
    for x in [305, 615, 925, 1235]:
        s.line(x + 5, 410, x + 45, 410, stroke=NAVY, sw=4, arrow=True)

    # Stage 1 motion thumbnails
    for i, yy in enumerate([265, 385, 505]):
        s.line(95, yy + 62, 265, yy + 62, stroke=MID, sw=2)
        cx = 175 + i * 8
        s.circle(cx, yy, 18, fill=WHITE, stroke=NAVY, sw=3)
        s.line(cx, yy + 18, cx - 5, yy + 68, sw=5)
        s.line(cx - 5, yy + 42, cx - 42 + i * 8, yy + 62, sw=5)
        s.line(cx - 5, yy + 42, cx + 38, yy + 45 - i * 5, sw=5)
        s.line(cx - 5, yy + 68, cx - 32, yy + 106 - i * 10, sw=5)
        s.line(cx - 5, yy + 68, cx + 30, yy + 102 - i * 8, sw=5)
    s.text(180, 635, "12条重定向跳跃", 20, fill=GRAY, anchor="middle")

    # Feature vector
    feats = [("q, q̇", BLUE), ("根节点", PURPLE), ("足端", TEAL), ("接触", ORANGE), ("相位", RED)]
    for i, (t, c) in enumerate(feats):
        y = 265 + i * 68
        s.rect(405, y, 170, 46, fill=WHITE, stroke=c, sw=2, rx=12)
        s.text(490, y + 31, t, 21, fill=c, weight=650, anchor="middle")
    s.text(490, 625, "加权距离 + 目标一致性", 18, fill=GRAY, anchor="middle")

    # Transform
    transform_items = [("平面旋转", "↻"), ("幅度分组", "↔"), ("相位对齐", "≋"), ("轨迹平滑", "∿")]
    for i, (t, symbol) in enumerate(transform_items):
        yy = 275 + i * 86
        s.circle(735, yy, 26, fill=WHITE, stroke=ORANGE, sw=2)
        s.text(735, yy + 9, symbol, 30, fill=ORANGE, weight=700, anchor="middle")
        s.text(785, yy + 8, t, 22, weight=600)

    # Filters
    filters = ["关节限位", "速度连续", "足端无穿透", "接触一致", "落地可恢复"]
    for i, t in enumerate(filters):
        yy = 258 + i * 68
        s.circle(1040, yy, 15, fill=GREEN, stroke=GREEN, sw=1)
        s.text(1040, yy + 7, "✓", 18, fill=WHITE, weight=700, anchor="middle")
        s.text(1072, yy + 7, t, 21, weight=600)
    s.text(1110, 625, "不合格样本不进入Teacher训练", 18, fill=GRAY, anchor="middle")

    # Coverage scatter
    cx, cy = 1420, 430
    s.line(cx - 90, cy, cx + 90, cy, stroke=GRAY, sw=2, arrow=True)
    s.line(cx, cy + 150, cx, cy - 160, stroke=GRAY, sw=2, arrow=True)
    rnd = random.Random(8)
    colors = [BLUE, TEAL, GREEN, ORANGE, PURPLE]
    for ring, rad in enumerate([45, 85, 125]):
        s.ellipse(cx, cy, rad, rad, stroke=GRID, sw=1, dash="5 5")
        for k in range(10):
            a = 2 * math.pi * k / 10 + ring * 0.12
            rr = rad + rnd.uniform(-8, 8)
            px, py = cx + rr * math.cos(a), cy - rr * math.sin(a)
            s.circle(px, py, 7, fill=colors[(k + ring) % len(colors)], stroke=WHITE, sw=1)
    s.text(cx + 97, cy + 3, "Δx", 18, fill=GRAY)
    s.text(cx + 4, cy - 168, "Δy", 18, fill=GRAY)
    s.text(cx, 625, "多方向 × 多距离", 21, fill=TEAL, weight=700, anchor="middle")
    s.rect(190, 735, 1220, 90, fill="#FAFBFD", stroke=MID, sw=1, rx=18)
    s.text(800, 790, "离线检索负责组织参考数据；部署阶段不访问动作数据库，也不执行在线 Motion Matching", 25, fill=NAVY, weight=650, anchor="middle")
    s.save("fig03_reference_augmentation.svg")


def fig04_teacher_student():
    s = SVG(title="Teacher–Student信息接口与DAgger-PPO联合优化")
    # Teacher side
    s.rect(50, 120, 610, 650, fill=ORANGE_BG, stroke=ORANGE, sw=3, rx=24)
    s.text(355, 175, "Teacher（训练时专家）", 29, fill=ORANGE, weight=700, anchor="middle")
    inputs_t = ["仿真完整状态 sₜ", "动作相位 φₜ", "短时未来参考 rₜ", "参考足端与接触"]
    for i, t in enumerate(inputs_t):
        yy = 225 + i * 72
        s.rect(90, yy, 230, 50, fill=WHITE, stroke=ORANGE, sw=2, rx=12)
        s.text(205, yy + 33, t, 20, anchor="middle")
        s.line(320, yy + 25, 390, 390, stroke=ORANGE, sw=2, arrow=True)
    s.circle(455, 390, 84, fill=WHITE, stroke=ORANGE, sw=4)
    s.multiline(455, 380, ["Teacher", "π_E"], 25, fill=ORANGE, weight=700, gap=1.3)
    s.line(455, 478, 455, 540, stroke=ORANGE, sw=4, arrow=True)
    s.rect(335, 550, 240, 62, fill=WHITE, stroke=ORANGE, sw=2, rx=15)
    s.text(455, 590, "专家动作 aₜᴱ", 24, fill=ORANGE, weight=700, anchor="middle")
    s.text(355, 690, "作用：把运动学参考转换为", 21, fill=GRAY, anchor="middle")
    s.text(355, 720, "满足动力学与接触约束的控制行为", 21, fill=GRAY, anchor="middle")

    # Student side
    s.rect(940, 120, 610, 650, fill=MINT, stroke=TEAL, sw=3, rx=24)
    s.text(1245, 175, "Student（部署策略）", 29, fill=TEAL, weight=700, anchor="middle")
    inputs_s = ["本体观测 oₜ", "二维目标位移 g", "跳跃触发 zₜ", "上一时刻动作"]
    for i, t in enumerate(inputs_s):
        yy = 225 + i * 72
        s.rect(980, yy, 230, 50, fill=WHITE, stroke=TEAL, sw=2, rx=12)
        s.text(1095, yy + 33, t, 20, anchor="middle")
        s.line(1210, yy + 25, 1280, 390, stroke=TEAL, sw=2, arrow=True, arrow_id="arrow-green")
    s.circle(1345, 390, 84, fill=WHITE, stroke=TEAL, sw=4)
    s.multiline(1345, 380, ["Student", "π_S"], 25, fill=TEAL, weight=700, gap=1.3)
    s.line(1345, 478, 1345, 540, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    s.rect(1225, 550, 240, 62, fill=WHITE, stroke=TEAL, sw=2, rx=15)
    s.text(1345, 590, "关节动作 aₜ", 24, fill=TEAL, weight=700, anchor="middle")
    s.text(1245, 690, "部署时不输入相位、未来姿态", 21, fill=GRAY, anchor="middle")
    s.text(1245, 720, "或在线检索得到的参考运动", 21, fill=GRAY, anchor="middle")

    # Center bridge
    s.rect(700, 175, 200, 115, fill=PURPLE_BG, stroke=PURPLE, sw=3, rx=18)
    s.multiline(800, 218, ["实际位移", "重标注 g"], 23, fill=PURPLE, weight=700, gap=1.35)
    s.line(660, 235, 690, 235, stroke=PURPLE, sw=3, arrow=True)
    s.line(900, 235, 930, 235, stroke=PURPLE, sw=3, arrow=True)
    s.rect(690, 345, 220, 150, fill=WHITE, stroke=NAVY, sw=3, rx=18)
    s.multiline(800, 390, ["Student访问状态", "查询Teacher动作", "聚合DAgger数据"], 21, weight=650, gap=1.45)
    s.path("M 940 420 C 905 420, 900 420, 910 420", stroke=NAVY, sw=3, arrow=True)
    s.path("M 690 455 C 665 500, 660 535, 700 585", stroke=NAVY, sw=3, arrow=True)
    s.rect(680, 570, 240, 115, fill="#F8FAFC", stroke=NAVY, sw=3, rx=18)
    s.multiline(800, 610, ["L = (1−α)L_PPO", "+ αL_act"], 23, fill=NAVY, weight=700, gap=1.4)
    s.text(800, 825, "DAgger覆盖Student偏离专家后的状态；PPO直接优化目标到达与落地恢复", 25, fill=NAVY, weight=650, anchor="middle")
    s.save("fig04_teacher_student.svg")


def fig05_sequence():
    s = SVG(width=1800, height=760, title="单次目标位移跳跃的动作阶段（示意）")
    raw_png = (OUT / "fig05_jump_sequence_raw.png").read_bytes()
    embedded = "data:image/png;base64," + base64.b64encode(raw_png).decode("ascii")
    s.image(30, 90, 1740, 580, embedded)
    stages = ["准备", "下蹲蓄力", "起跳", "早期腾空", "腾空顶点", "双脚触地", "稳定恢复"]
    times = ["t=0.00 s", "0.22 s", "0.38 s", "0.50 s", "0.64 s", "0.82 s", "1.30 s"]
    xs = [145, 390, 635, 880, 1125, 1370, 1615]
    for i, x in enumerate(xs):
        s.line(x, 615, x, 650, stroke=MID, sw=2)
        s.text(x, 690, stages[i], 23, fill=NAVY, weight=700, anchor="middle")
        s.text(x, 720, times[i], 17, fill=GRAY, anchor="middle")
    s.line(120, 645, 1650, 645, stroke=NAVY, sw=3, arrow=True)
    s.text(1770, 735, "AI生成动作示意；正式稿应替换为真实仿真连续帧", 16, fill=GRAY, anchor="end")
    s.save("fig05_jump_sequence.svg")


def fig06_landing_scatter():
    s = SVG(title="目标位置与实际落点分布")
    left, top, w, h = 140, 120, 1120, 650
    xmap, ymap = axes(s, left, top, w, h, -0.6, 0.8, -0.6, 0.6,
                       "前后目标位移 Δx / m", "左右目标位移 Δy / m",
                       [-0.6, -0.3, 0, 0.3, 0.6], [-0.6, -0.3, 0, 0.3, 0.6])
    targets = [
        (0.60, 0.00, BLUE, "前"),
        (0.42, 0.34, TEAL, "左前"),
        (0.00, -0.45, PURPLE, "右"),
        (-0.38, 0.00, ORANGE, "后"),
    ]
    rnd = random.Random(42)
    for tx, ty, color, label in targets:
        px, py = xmap(tx), ymap(ty)
        s.ellipse(px, py, w * 0.10 / 1.4, h * 0.10 / 1.2, stroke=color, sw=2, dash="7 5", opacity=0.8)
        for _ in range(75):
            sx = 0.035 if tx >= 0 else 0.055
            sy = 0.035 if abs(ty) > 0.05 else 0.030
            ax = rnd.gauss(tx - (0.012 if tx < 0 else 0.004), sx)
            ay = rnd.gauss(ty, sy)
            s.circle(xmap(ax), ymap(ay), 4, fill=color, stroke=color, sw=0, opacity=0.35)
        # target cross
        s.line(px - 12, py - 12, px + 12, py + 12, stroke=color, sw=4)
        s.line(px - 12, py + 12, px + 12, py - 12, stroke=color, sw=4)
        s.text(px + 18, py - 16, label, 19, fill=color, weight=700)

    s.rect(1305, 155, 245, 410, fill=WHITE, stroke=GRID, sw=2, rx=18)
    s.text(1428, 205, "图例", 25, fill=NAVY, weight=700, anchor="middle")
    s.line(1340, 255, 1364, 279, stroke=BLUE, sw=4)
    s.line(1340, 279, 1364, 255, stroke=BLUE, sw=4)
    s.text(1390, 274, "目标位置", 21)
    s.circle(1352, 330, 6, fill=TEAL, stroke=TEAL, sw=0, opacity=0.5)
    s.text(1390, 337, "实际落点", 21)
    s.ellipse(1352, 395, 28, 20, stroke=ORANGE, sw=2, dash="6 4")
    s.text(1390, 402, "0.10 m容差", 21)
    s.text(1428, 470, "误差定义", 22, fill=GRAY, weight=700, anchor="middle")
    s.text(1428, 515, "eₚ = ‖Δp − g‖₂", 23, fill=NAVY, weight=700, anchor="middle")
    footer(s)
    s.save("fig06_landing_scatter.svg")


def heat_color(v):
    # Interpolate pale gray -> teal -> dark green for v in [55, 96]
    stops = [(55, (237, 242, 247)), (75, (169, 215, 208)), (90, (66, 168, 143)), (96, (19, 108, 100))]
    for (v0, c0), (v1, c1) in zip(stops, stops[1:]):
        if v <= v1:
            t = max(0, min(1, (v - v0) / (v1 - v0)))
            c = tuple(round(a + t * (b - a)) for a, b in zip(c0, c1))
            return "#%02X%02X%02X" % c
    return "#136C64"


def fig07_heatmap():
    s = SVG(title="二维目标空间上的联合成功率")
    xs = [-0.4, -0.2, 0.0, 0.2, 0.4, 0.6]
    ys = [0.5, 0.3, 0.1, -0.1, -0.3, -0.5]
    vals = [
        [58, 69, 78, 85, 86, 80],
        [66, 76, 86, 92, 93, 88],
        [72, 83, 90, 95, 96, 94],
        [73, 84, 91, 95, 95, 93],
        [67, 77, 87, 92, 92, 86],
        [57, 68, 77, 84, 85, 78],
    ]
    x0, y0, cell = 300, 145, 100
    for r, yv in enumerate(ys):
        s.text(x0 - 35, y0 + r * cell + 61, f"{yv:+.1f}", 20, fill=GRAY, anchor="end")
        for c, xv in enumerate(xs):
            value = vals[r][c]
            fill = heat_color(value)
            s.rect(x0 + c * cell, y0 + r * cell, cell - 4, cell - 4, fill=fill, stroke=WHITE, sw=2, rx=8)
            txt = WHITE if value >= 83 else NAVY
            s.text(x0 + c * cell + 48, y0 + r * cell + 60, f"{value}%", 22, fill=txt, weight=700, anchor="middle")
    for c, xv in enumerate(xs):
        s.text(x0 + c * cell + 48, y0 + 6 * cell + 35, f"{xv:+.1f}", 20, fill=GRAY, anchor="middle")
    s.text(x0 + 300, 815, "前后目标位移 Δx / m", 24, weight=650, anchor="middle")
    s.text(170, 455, "左右目标位移 Δy / m", 24, weight=650, anchor="middle")

    # legend and findings
    s.rect(1020, 145, 480, 600, fill="#FBFCFE", stroke=GRID, sw=2, rx=22)
    s.text(1260, 200, "成功率色标", 25, fill=NAVY, weight=700, anchor="middle")
    for i in range(180):
        v = 55 + i / 179 * 41
        s.rect(1100 + i * 1.8, 235, 2, 34, fill=heat_color(v), stroke=heat_color(v), sw=0, rx=0)
    for v in [55, 75, 90, 96]:
        px = 1100 + (v - 55) / 41 * 322
        s.text(px, 300, f"{v}%", 18, fill=GRAY, anchor="middle")
    notes = [
        ("前向中等距离", "成功率最高", GREEN),
        ("后向目标", "起跳与恢复更困难", ORANGE),
        ("侧向边界", "落点方差增大", PURPLE),
        ("经验可行域外", "应拒绝或拆分命令", RED),
    ]
    for i, (a, b, c) in enumerate(notes):
        yy = 365 + i * 88
        s.circle(1080, yy - 7, 9, fill=c, stroke=c, sw=0)
        s.text(1110, yy, a, 22, fill=c, weight=700)
        s.text(1110, yy + 31, b, 19, fill=GRAY)
    footer(s)
    s.save("fig07_success_heatmap.svg")


def fig08_ablation():
    s = SVG(title="方法对比与关键模块消融")
    # Left panel success
    s.text(420, 120, "联合成功率 / %", 25, fill=NAVY, weight=700, anchor="middle")
    methods = ["直接PPO", "无Teacher", "纯行为克隆", "无DAgger", "DAgger", "完整方法"]
    success = [42.6, 61.7, 73.8, 78.1, 84.9, 91.3]
    colors = [RED, ORANGE, PURPLE, "#6F91C7", CYAN, GREEN]
    base_x, base_y, maxw = 220, 180, 500
    for i, (m, v, c) in enumerate(zip(methods, success, colors)):
        yy = base_y + i * 90
        s.text(base_x - 20, yy + 30, m, 21, anchor="end", weight=600)
        s.rect(base_x, yy, maxw, 44, fill=LIGHT, stroke=LIGHT, sw=0, rx=10)
        s.rect(base_x, yy, maxw * v / 100, 44, fill=c, stroke=c, sw=0, rx=10)
        s.text(base_x + maxw * v / 100 + 12, yy + 31, f"{v:.1f}", 20, fill=c, weight=700)
    s.line(base_x, 735, base_x + maxw, 735, stroke=DARK, sw=2)
    for v in [0, 20, 40, 60, 80, 100]:
        xx = base_x + maxw * v / 100
        s.line(xx, 735, xx, 743, stroke=DARK, sw=2)
        s.text(xx, 770, str(v), 18, fill=GRAY, anchor="middle")

    # Right panel errors
    s.text(1190, 120, "平均目标误差 / m", 25, fill=NAVY, weight=700, anchor="middle")
    methods2 = ["完整方法", "名义位移标签", "无近邻增强", "无DAgger", "无PPO", "无Teacher"]
    errors = [0.061, 0.081, 0.088, 0.105, 0.116, 0.137]
    colors2 = [GREEN, PURPLE, CYAN, "#6F91C7", ORANGE, RED]
    base_x2 = 1010
    for i, (m, v, c) in enumerate(zip(methods2, errors, colors2)):
        yy = base_y + i * 90
        s.text(base_x2 - 20, yy + 30, m, 21, anchor="end", weight=600)
        s.rect(base_x2, yy, maxw, 44, fill=LIGHT, stroke=LIGHT, sw=0, rx=10)
        s.rect(base_x2, yy, maxw * v / 0.16, 44, fill=c, stroke=c, sw=0, rx=10)
        s.text(base_x2 + maxw * v / 0.16 + 12, yy + 31, f"{v:.3f}", 20, fill=c, weight=700)
    s.line(base_x2, 735, base_x2 + maxw, 735, stroke=DARK, sw=2)
    for v in [0, 0.04, 0.08, 0.12, 0.16]:
        xx = base_x2 + maxw * v / 0.16
        s.line(xx, 735, xx, 743, stroke=DARK, sw=2)
        s.text(xx, 770, f"{v:.2f}", 18, fill=GRAY, anchor="middle")
    s.line(800, 120, 800, 790, stroke=GRID, sw=2)
    footer(s)
    s.save("fig08_ablation.svg")


def smooth_curve(x, start, end, tau, wobble=0.0):
    return end - (end - start) * math.exp(-x / tau) + wobble * math.sin(x / 700)


def fig09_training():
    s = SVG(title="Teacher与Student训练过程")
    panels = [
        (95, 140, "Teacher跟踪回报", 0, 30000, 0, 100, BLUE, "迭代次数", "归一化回报"),
        (850, 140, "Student联合成功率", 0, 160000, 0, 100, GREEN, "迭代次数", "成功率 / %"),
        (95, 490, "Student目标误差", 0, 160000, 0, 0.30, ORANGE, "迭代次数", "误差 / m"),
        (850, 490, "模仿权重 α", 0, 20000, 0, 1.0, PURPLE, "迭代次数", "权重"),
    ]
    for idx, (x, y, title, xmin, xmax, ymin, ymax, color, xl, yl) in enumerate(panels):
        w, h = 600, 240
        s.text(x + w / 2, y - 18, title, 23, fill=NAVY, weight=700, anchor="middle")
        xticks = [xmin, (xmin + xmax) / 2, xmax]
        yticks = [ymin, (ymin + ymax) / 2, ymax]
        xm, ym = axes(s, x, y, w, h, xmin, xmax, ymin, ymax, xl, yl, xticks, yticks)
        pts = []
        for j in range(81):
            xx = xmin + (xmax - xmin) * j / 80
            if idx == 0:
                yy = smooth_curve(xx, 12, 94, 6000, 1.5)
            elif idx == 1:
                yy = smooth_curve(xx, 5, 92, 36000, 1.5)
            elif idx == 2:
                yy = 0.055 + (0.28 - 0.055) * math.exp(-xx / 33000) + 0.004 * math.sin(xx / 6000)
            else:
                yy = max(0.1, 1 - xx / 10000)
            pts.append((xm(xx), ym(yy)))
        d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
        # uncertainty ribbon for first three
        if idx < 3:
            upper, lower = [], []
            for j, (px, py) in enumerate(pts):
                band = (18 if idx < 2 else 0.03) * math.exp(-j / 30) + (3 if idx < 2 else 0.006)
                v = ymin + (y + h - py) / h * (ymax - ymin)
                upper.append((px, ym(min(ymax, v + band))))
                lower.append((px, ym(max(ymin, v - band))))
            pd = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in upper)
            pd += " L " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in reversed(lower)) + " Z"
            s.path(pd, fill=color, stroke="none", sw=0, opacity=0.14)
        s.path(d, stroke=color, sw=4)
    footer(s)
    s.save("fig09_training_curves.svg")


def fig10_cdf():
    s = SVG(title="目标位移误差累计分布")
    x0, y0, w, h = 190, 125, 1030, 650
    xm, ym = axes(s, x0, y0, w, h, 0, 0.25, 0, 1.0, "目标误差 eₚ / m", "累计比例 P(eₚ≤δ)",
                  [0, 0.05, 0.10, 0.15, 0.20, 0.25], [0, 0.25, 0.5, 0.75, 1.0])
    curves = [
        ("完整方法", 0.055, GREEN),
        ("无DAgger", 0.085, ORANGE),
        ("纯行为克隆", 0.095, PURPLE),
        ("直接PPO", 0.155, RED),
    ]
    for label, scale, color in curves:
        pts = []
        for i in range(101):
            x = 0.25 * i / 100
            y = 1 - math.exp(-((x / scale) ** 2.2))
            pts.append((xm(x), ym(y)))
        s.path("M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts), stroke=color, sw=5)
    threshold = xm(0.10)
    s.line(threshold, y0, threshold, y0 + h, stroke=BLUE, sw=3, dash="10 7")
    s.text(threshold + 12, y0 + 40, "主判据 δ=0.10 m", 22, fill=BLUE, weight=700)
    s.rect(1280, 175, 250, 300, fill=WHITE, stroke=GRID, sw=2, rx=18)
    s.text(1405, 220, "方法", 23, fill=NAVY, weight=700, anchor="middle")
    for i, (label, _, color) in enumerate(curves):
        yy = 275 + i * 55
        s.line(1310, yy, 1360, yy, stroke=color, sw=5)
        s.text(1380, yy + 7, label, 20)
    s.rect(1280, 530, 250, 150, fill=SKY, stroke=BLUE, sw=2, rx=18)
    s.multiline(1405, 575, ["曲线越靠左上", "目标控制越准确"], 21, fill=BLUE, weight=700, gap=1.45)
    footer(s)
    s.save("fig10_error_cdf.svg")


def fig11_robustness():
    s = SVG(title="动力学随机化与控制延迟下的鲁棒性")
    # Left grouped bars
    s.text(420, 125, "不同扰动条件", 25, fill=NAVY, weight=700, anchor="middle")
    labels = ["标称", "摩擦", "质量/质心", "观测噪声", "20 ms延迟", "联合随机化"]
    vals = [91.3, 88.7, 87.9, 89.2, 82.6, 79.8]
    cols = [GREEN, TEAL, CYAN, BLUE, ORANGE, RED]
    x0, y0, w, h = 100, 180, 650, 540
    s.line(x0, y0 + h, x0 + w, y0 + h, stroke=DARK, sw=2)
    s.line(x0, y0, x0, y0 + h, stroke=DARK, sw=2)
    for v in [0, 20, 40, 60, 80, 100]:
        py = y0 + h - h * v / 100
        s.line(x0, py, x0 + w, py, stroke=GRID, sw=1)
        s.text(x0 - 12, py + 6, str(v), 18, fill=GRAY, anchor="end")
    bw = 78
    for i, (lab, v, c) in enumerate(zip(labels, vals, cols)):
        xx = x0 + 42 + i * 102
        bh = h * v / 100
        s.rect(xx, y0 + h - bh, bw, bh, fill=c, stroke=c, sw=0, rx=8)
        s.text(xx + bw / 2, y0 + h - bh - 12, f"{v:.1f}", 18, fill=c, weight=700, anchor="middle")
        s.text(xx + bw / 2, y0 + h + 35, lab, 17, fill=GRAY, anchor="middle")
    s.raw(
        f'<text x="45" y="450" transform="rotate(-90 45 450)" fill="{DARK}" '
        'font-family="Noto Sans CJK SC, sans-serif" font-size="22" font-weight="650" '
        'text-anchor="middle">联合成功率 / %</text>'
    )

    # Right latency curve
    s.text(1180, 125, "控制延迟敏感性", 25, fill=NAVY, weight=700, anchor="middle")
    lx, ly, lw, lh = 900, 180, 590, 540
    xm, ym = axes(s, lx, ly, lw, lh, 0, 40, 50, 100, "额外控制延迟 / ms", "联合成功率 / %",
                  [0, 10, 20, 30, 40], [50, 60, 70, 80, 90, 100])
    delays = [0, 10, 20, 30, 40]
    succ = [91.3, 88.9, 82.6, 73.4, 61.2]
    pts = [(xm(a), ym(b)) for a, b in zip(delays, succ)]
    s.path("M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts), stroke=ORANGE, sw=5)
    for (px, py), v in zip(pts, succ):
        s.circle(px, py, 8, fill=ORANGE, stroke=WHITE, sw=3)
        s.text(px, py - 18, f"{v:.1f}", 18, fill=ORANGE, weight=700, anchor="middle")
    s.line(xm(20), ly, xm(20), ly + lh, stroke=RED, sw=2, dash="8 6")
    s.text(xm(20) + 10, ly + 35, "明显退化区", 19, fill=RED, weight=700)
    footer(s)
    s.save("fig11_robustness.svg")


def main():
    fig01_framework()
    fig02_target_command()
    fig03_augmentation()
    fig04_teacher_student()
    fig05_sequence()
    fig06_landing_scatter()
    fig07_heatmap()
    fig08_ablation()
    fig09_training()
    fig10_cdf()
    fig11_robustness()
    print("Generated 11 SVG figures in", OUT)


if __name__ == "__main__":
    main()
