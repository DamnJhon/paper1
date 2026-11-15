#!/usr/bin/env python3
"""Generate an image-led, paper-style method overview.

The composition follows the visual grammar common in robotics overview
figures: qualitative robot motion is the primary carrier of information,
while algorithm labels and arrows are deliberately sparse.  The output is
self-contained SVG; it reuses the existing AI-generated jump sequence only
as a schematic illustration, never as an experimental result.
"""

from __future__ import annotations

import base64
from collections import deque
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

from generate_figures import (
    BLUE,
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
    SKY,
    TEAL,
    WHITE,
    SVG,
    esc,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "overview"
OUT.mkdir(exist_ok=True)
SOURCE = Image.open(HERE / "fig05_jump_sequence_raw.png").convert("RGB")


def save(svg: SVG, name: str) -> None:
    svg.parts.append("</svg>")
    (OUT / name).write_text("\n".join(svg.parts), encoding="utf-8")


def crop_uri(box: tuple[int, int, int, int]) -> str:
    crop = SOURCE.crop(box).convert("RGBA")
    # The source illustration has a near-white studio background.  Remove it
    # so individual poses can be composed without visible rectangular tiles.
    luminance = crop.convert("L")
    alpha = luminance.point(lambda value: max(0, min(255, (253 - value) * 42)))
    # Keep only the dominant connected foreground object.  This removes a
    # hand or foot from an adjacent pose when the source sequence is cropped.
    binary = alpha.point(lambda value: 255 if value >= 105 else 0)
    width, height = binary.size
    pixels = binary.load()
    visited = bytearray(width * height)
    largest: list[tuple[int, int]] = []
    for yy in range(height):
        for xx in range(width):
            idx = yy * width + xx
            if visited[idx] or pixels[xx, yy] == 0:
                continue
            visited[idx] = 1
            queue = deque([(xx, yy)])
            component: list[tuple[int, int]] = []
            while queue:
                cx, cy = queue.popleft()
                component.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        nidx = ny * width + nx
                        if not visited[nidx] and pixels[nx, ny] != 0:
                            visited[nidx] = 1
                            queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component
    object_mask = Image.new("L", (width, height), 0)
    object_pixels = object_mask.load()
    for xx, yy in largest:
        object_pixels[xx, yy] = 255
    object_mask = object_mask.filter(ImageFilter.MaxFilter(13))
    crop.putalpha(ImageChops.multiply(alpha, object_mask))
    data = BytesIO()
    crop.save(data, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(data.getvalue()).decode("ascii")


POSES = {
    "stand-left": crop_uri((25, 45, 235, 650)),
    "crouch-left": crop_uri((235, 170, 555, 650)),
    "takeoff": crop_uri((540, 70, 865, 650)),
    "flight-left": crop_uri((880, 35, 1165, 610)),
    "flight-right": crop_uri((1165, 15, 1500, 600)),
    "landing": crop_uri((1520, 170, 1825, 650)),
    "stand-right": crop_uri((1860, 45, 2085, 650)),
}


def image(svg: SVG, key: str, x, y, w, h, opacity=1.0) -> None:
    svg.raw(
        f'<image x="{x}" y="{y}" width="{w}" height="{h}" '
        f'xlink:href="{esc(POSES[key])}" preserveAspectRatio="xMidYMid meet" opacity="{opacity}"/>'
    )


def label(svg: SVG, x, y, text, size=20, fill=DARK, weight=500, anchor="start") -> None:
    svg.text(x, y, text, size, fill=fill, weight=weight, anchor=anchor)


def stage_header(svg: SVG, x, y, letter: str, title: str, subtitle: str, color: str) -> None:
    svg.text(x, y, f"({letter})", 25, fill=color, weight=700)
    svg.text(x + 48, y, title, 27, fill=NAVY, weight=700)
    svg.line(x, y + 17, x + 355, y + 17, stroke=color, sw=4)
    svg.text(x, y + 50, subtitle, 18, fill=GRAY, weight=450)


def small_chip(svg: SVG, x, y, w, text, fill, color) -> None:
    svg.rect(x, y, w, 38, fill=fill, stroke=fill, sw=0, rx=5)
    svg.text(x + w / 2, y + 26, text, 17, fill=color, weight=650, anchor="middle")


def paper_style_framework() -> None:
    s = SVG(1900, 860)
    # Background groups are deliberately borderless and nearly white.
    s.raw('<rect x="24" y="35" width="1390" height="760" rx="16" fill="#FBFCFE"/>')
    s.raw('<rect x="1434" y="35" width="442" height="760" rx="16" fill="#F7FBF9"/>')
    s.text(48, 70, "TRAINING", 17, fill=BLUE, weight=700)
    s.line(1450, 38, 1450, 796, stroke=GREEN, sw=2.5, dash="8 7")
    s.text(1474, 70, "DEPLOYMENT", 17, fill=GREEN, weight=700)

    # (a) Reference family: motion itself is the dominant visual element.
    stage_header(s, 52, 123, "a", "多方向、多距离参考族", "离线运动数据准备", BLUE)
    image(s, "stand-left", 58, 170, 100, 250, opacity=0.72)
    image(s, "crouch-left", 135, 170, 130, 250, opacity=0.82)
    image(s, "takeoff", 235, 165, 145, 255, opacity=0.92)
    image(s, "flight-left", 330, 160, 150, 260)
    s.line(90, 432, 430, 432, stroke=MID, sw=2.5, arrow=True)
    s.text(260, 462, "基础跳跃片段", 18, fill=GRAY, weight=600, anchor="middle")

    # A compact top-down fan conveys direction/range augmentation without boxes.
    ox, oy = 265, 615
    s.circle(ox, oy, 7, fill=NAVY, stroke=NAVY, sw=0)
    for dx, dy, color in [(115, -95, BLUE), (145, -38, TEAL), (105, 58, PURPLE), (-72, -60, MID)]:
        s.line(ox, oy, ox + dx, oy + dy, stroke=color, sw=3.5, arrow=True, arrow_id="arrow-blue" if color == BLUE else "arrow")
    s.path(f"M {ox + 32} {oy - 5} A 52 52 0 0 0 {ox + 20} {oy - 42}", stroke=BLUE, sw=2, dash="5 5")
    s.circle(ox + 115, oy - 95, 10, fill=BLUE, stroke=WHITE, sw=2)
    s.circle(ox + 145, oy - 38, 10, fill=TEAL, stroke=WHITE, sw=2)
    s.circle(ox + 105, oy + 58, 10, fill=PURPLE, stroke=WHITE, sw=2)
    label(s, 52, 720, "近邻检索  ·  平面旋转  ·  幅度调整  ·  可行性筛选", 18, fill=NAVY, weight=650)
    label(s, 52, 755, "输出：增强参考轨迹  r₁:T", 20, fill=BLUE, weight=700)

    # (b) Teacher: reference ghost + physics execution + actual displacement relabeling.
    stage_header(s, 505, 123, "b", "Teacher 物理跟踪", "完整参考与仿真特权信息", ORANGE)
    s.text(555, 205, "参考动作", 17, fill=GRAY, weight=600, anchor="middle")
    image(s, "takeoff", 500, 220, 135, 245, opacity=0.22)
    image(s, "flight-left", 590, 210, 140, 255, opacity=0.22)
    s.line(690, 338, 785, 338, stroke=ORANGE, sw=4, arrow=True)
    small_chip(s, 746, 214, 150, "πE(sₜ, rₜ)", ORANGE_BG, ORANGE)
    image(s, "takeoff", 780, 252, 150, 265, opacity=0.95)
    image(s, "flight-left", 870, 235, 160, 280, opacity=1.0)
    label(s, 813, 525, "PhysX / G1", 20, fill=NAVY, weight=700)
    label(s, 813, 552, "动力学可执行专家轨迹", 18, fill=GRAY, weight=600)

    # Relabeling inset: only the essential geometric distinction.
    px, py = 650, 690
    s.line(px, py, px + 255, py, stroke=MID, sw=2, arrow=True)
    s.line(px, py, px, py - 120, stroke=MID, sw=2, arrow=True)
    s.circle(px, py, 6, fill=NAVY, stroke=NAVY, sw=0)
    s.line(px, py, px + 200, py - 105, stroke=BLUE, sw=3, dash="8 6", arrow=True, arrow_id="arrow-blue")
    s.line(px, py, px + 165, py - 63, stroke=ORANGE, sw=4, arrow=True)
    s.circle(px + 200, py - 105, 8, fill=BLUE, stroke=WHITE, sw=2)
    s.circle(px + 165, py - 63, 9, fill=ORANGE, stroke=WHITE, sw=2)
    s.line(642, 718, 687, 718, stroke=BLUE, sw=2.5, dash="7 5")
    label(s, 695, 724, "名义参考", 15, fill=BLUE, weight=600)
    s.line(785, 718, 830, 718, stroke=ORANGE, sw=3)
    label(s, 838, 724, "Teacher 实际位移", 15, fill=ORANGE, weight=600)
    label(s, 642, 755, "gᵢ ← Δpᵢ(actual)", 21, fill=ORANGE, weight=700)
    label(s, 820, 755, "实际位移重标注", 17, fill=GRAY, weight=600)

    # (c) Student distillation: one central policy, two learning signals.
    stage_header(s, 1015, 123, "c", "Student 蒸馏", "DAgger 专家监督 + PPO 任务回报", PURPLE)
    small_chip(s, 1060, 205, 160, "Teacher  πE", ORANGE_BG, ORANGE)
    small_chip(s, 1245, 205, 130, "数据 Dᴱ", PURPLE_BG, PURPLE)
    s.line(1140, 245, 1190, 330, stroke=ORANGE, sw=3.5, dash="7 5", arrow=True)
    s.line(1310, 245, 1260, 330, stroke=PURPLE, sw=3.5, dash="7 5", arrow=True)
    s.text(1130, 285, "aₜᴱ", 17, fill=ORANGE, weight=700)
    s.rect(1100, 338, 230, 94, fill=MINT, stroke=TEAL, sw=2.5, rx=10)
    s.text(1215, 377, "Student  πS", 25, fill=TEAL, weight=700, anchor="middle")
    s.text(1215, 408, "πS(aₜ | oₜ, g, zₜ)", 18, fill=NAVY, weight=600, anchor="middle")
    s.line(1215, 436, 1215, 485, stroke=TEAL, sw=4, arrow=True, arrow_id="arrow-green")
    image(s, "landing", 1135, 462, 175, 255)
    s.line(1105, 650, 1320, 650, stroke=MID, sw=2)
    s.text(1215, 681, "Student rollout", 18, fill=GRAY, weight=600, anchor="middle")
    s.path("M 1130 625 C 1050 600 1045 445 1090 405", stroke=ORANGE, sw=3, dash="7 5", arrow=True)
    s.text(1035, 535, "DAgger", 17, fill=ORANGE, weight=700, anchor="middle")
    s.path("M 1305 625 C 1380 590 1382 452 1342 405", stroke=GREEN, sw=3.5, arrow=True, arrow_id="arrow-green")
    s.text(1390, 535, "Rₛ / PPO", 17, fill=GREEN, weight=700, anchor="middle")
    label(s, 1040, 748, "动作结构", 17, fill=ORANGE, weight=650)
    s.line(1125, 741, 1200, 741, stroke=ORANGE, sw=3, dash="7 5")
    label(s, 1220, 748, "任务成功", 17, fill=GREEN, weight=650)
    s.line(1305, 741, 1380, 741, stroke=GREEN, sw=3)

    # (d) Deployment: large robot and target geometry, not another algorithm panel.
    stage_header(s, 1470, 123, "d", "二维目标闭环部署", "仅使用可测本体状态与目标命令", GREEN)
    small_chip(s, 1518, 190, 270, "oₜ  +  g=(Δx*,Δy*)  +  zₜ", MINT, TEAL)
    image(s, "flight-right", 1460, 245, 230, 340)
    image(s, "landing", 1640, 310, 225, 315, opacity=0.92)
    s.line(1500, 648, 1835, 648, stroke=MID, sw=2.5, arrow=True)
    s.line(1518, 648, 1780, 648, stroke=GREEN, sw=5, arrow=True, arrow_id="arrow-green")
    s.circle(1780, 648, 13, fill=GREEN, stroke=WHITE, sw=3)
    label(s, 1530, 680, "起跳", 17, fill=GRAY, weight=600)
    label(s, 1760, 680, "目标 g", 18, fill=GREEN, weight=700)
    s.path("M 1820 590 C 1880 495 1850 300 1765 250", stroke=TEAL, sw=3, dash="8 6", arrow=True, arrow_id="arrow-green")
    label(s, 1780, 410, "本体反馈", 16, fill=TEAL, weight=650, anchor="middle")
    label(s, 1510, 732, "πS  →  29维关节位置动作  →  G1", 20, fill=NAVY, weight=700)
    s.line(1480, 768, 1845, 768, stroke=GRID, sw=1.5)
    label(s, 1660, 803, "无相位  ·  无未来参考  ·  无在线动作检索", 17, fill=RED, weight=650, anchor="middle")
    label(s, 1660, 830, "机器人画面为方法示意，非实验结果", 13, fill=GRAY, weight=500, anchor="middle")

    # One clean narrative arrow along the bottom of the training region.
    s.line(430, 814, 1405, 814, stroke=NAVY, sw=2.5, arrow=True)
    s.text(900, 839, "reference family  →  physics teacher  →  displacement relabeling  →  policy distillation",
           15, fill=GRAY, weight=500, anchor="middle")

    save(s, "fig01_overall_framework_v2.svg")


if __name__ == "__main__":
    paper_style_framework()
    print(f"Generated {OUT / 'fig01_overall_framework_v2.svg'}")
