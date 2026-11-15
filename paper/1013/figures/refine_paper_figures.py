"""Regenerate figures 2–4 and 6–11 from the manuscript and demo series.

Requires NumPy, Matplotlib and Noto Sans CJK SC. Run from any directory.
"""

from pathlib import Path
import random
from math import erf
from statistics import NormalDist

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.font_manager import fontManager
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
from matplotlib.ticker import MultipleLocator
import numpy as np

from generate_figures import smooth_curve


OUT = Path(__file__).resolve().parent
BLUE, RUST, GRAY = "#285d7b", "#9d5138", "#58636d"
INK = "#252b30"
available_fonts = {font.name for font in fontManager.ttflist}
cjk_font = next((name for name in ("Noto Sans CJK SC", "Noto Sans CJK JP")
                 if name in available_fonts), None)
if cjk_font is None:
    raise RuntimeError("Install Noto Sans CJK to render the Chinese figure labels.")
mpl.rcParams.update({
    "font.family": [cjk_font, "DejaVu Sans"],
    "font.size": 10, "text.color": INK, "axes.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .75,
    "legend.frameon": False, "axes.unicode_minus": False,
    "svg.fonttype": "none", "svg.hashsalt": "paper-1013", "pdf.fonttype": 3,
})


def save(fig, name, source=None):
    if source:
        fig.text(.99, .012, source, ha="right", fontsize=8, color=GRAY)
    for folder, suffix in (("", "svg"), ("png", "png"), ("pdf", "pdf")):
        path = OUT / folder / f"{name}.{suffix}"
        metadata = {"Date": None} if suffix == "svg" else None
        fig.savefig(path, dpi=300, metadata=metadata)
        if suffix == "svg":
            lines = path.read_text(encoding="utf-8").splitlines()
            path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")
    plt.close(fig)


def panel(ax, title):
    ax.set_title(title, loc="left", fontsize=11, pad=8)


def grid(ax, axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color="#dce1e5", linewidth=.6)


def arrow(ax, points, color=INK, style="-"):
    for a, b in zip(points[:-2], points[1:-1]):
        ax.plot(*zip(a, b), color=color, ls=style, lw=1)
    ax.add_patch(FancyArrowPatch(*points[-2:], arrowstyle="-|>", mutation_scale=10,
                                lw=1, color=color, linestyle=style, shrinkA=0, shrinkB=0))


def schematic(height):
    fig, ax = plt.subplots(figsize=(10, height / 10))
    fig.subplots_adjust(left=.025, right=.975, bottom=.05, top=.96)
    ax.set(xlim=(0, 100), ylim=(0, height))
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, body="", accent=INK, fill="white"):
    ax.add_patch(Rectangle((x, y), w, h, ec=accent, fc=fill, lw=.9))
    ax.text(x+w/2, y+h*(.71 if body else .50), title, ha="center", va="center",
            weight="medium", color=accent)
    if body:
        ax.text(x+w/2, y+h*.30, body, ha="center", va="center", fontsize=9)


def target():
    fig, ax = plt.subplots(figsize=(6.2, 3.35))
    fig.subplots_adjust(left=.08, right=.97, top=.97, bottom=.11)
    ax.set(xlim=(-.07, .71), ylim=(-.05, .36), aspect="equal")
    ax.axis("off")
    origin, goal, land = (0, 0), (.52, .25), (.44, .12)
    arrow(ax, [origin, (.66, 0)], GRAY)
    arrow(ax, [origin, (0, .33)], GRAY)
    ax.text(.67, -.006, "$x$", color=GRAY)
    ax.text(-.018, .338, "$y$", color=GRAY)
    ax.text(-.057, -.034, r"起跳坐标系 $\mathcal{B}_0$", fontsize=9)
    ax.plot([goal[0], goal[0], 0], [0, goal[1], goal[1]], ls=":", lw=.8, color=GRAY)
    arrow(ax, [origin, goal], BLUE)
    arrow(ax, [origin, land], RUST)
    ax.plot(*zip(land, goal), ls="--", color=GRAY, lw=1)
    ax.scatter(*zip(origin, goal, land), s=18, c=[INK, BLUE, RUST], zorder=3)
    ax.text(.53, .267, r"目标 $g$", color=BLUE)
    ax.text(.45, .087, r"实际位移 $\Delta p$", color=RUST)
    ax.text(.527, .173, r"$e_p=\|\Delta p-g\|_2$", color=GRAY, fontsize=9)
    ax.text(.52, -.025, r"$\Delta x^*$", ha="center", fontsize=9)
    ax.text(-.012, .25, r"$\Delta y^*$", ha="right", fontsize=9)
    fig.text(.5, .025, "起跳时锁定局部坐标系与目标，地面位置均指基座水平投影。", ha="center", fontsize=9)
    save(fig, "fig02_target_displacement_command")


def augmentation():
    fig, ax = schematic(25)
    stages = [
        ("基础动作", "重定向跳跃片段"),
        ("近邻检索", "运动特征与目标位移"),
        ("参考增强", "旋转、幅度与相位"),
        ("可行性筛选", "限位、速度与接触"),
        ("参考轨迹族", "多方向、多距离"),
    ]
    for i, (title, body) in enumerate(stages):
        x = 1 + 20*i
        box(ax, x, 9, 18, 9, title, body, BLUE if i == 4 else INK)
        if i < 4:
            arrow(ax, [(x+18, 13.5), (x+20, 13.5)])
    ax.text(29.5, 5.3, r"$i^*=\arg\min_i\,[\|x-x_i\|_W^2+\lambda_g\|g-g_i\|_2^2]$",
            ha="center", fontsize=10)
    arrow(ax, [(90, 9), (90, 5.4)], BLUE)
    ax.text(90, 3.5, "供 Teacher 跟踪训练", ha="center", color=BLUE, fontsize=9)
    save(fig, "fig03_reference_augmentation")


def distillation():
    fig, ax = schematic(55)
    fig.set_size_inches(8.4, 4.65)
    fig.subplots_adjust(left=.018, right=.982, bottom=.02, top=.98)
    cool, warm = "#edf4f8", "#f8efea"
    ax.add_patch(Rectangle((1, 17), 98, 37, fc="#f7f9fa", ec="#d5dde3", lw=.65))
    ax.add_patch(Rectangle((1, 1), 98, 14, fc="#f3f7fa", ec="#d5dde3", lw=.65))
    ax.text(4, 51.1, "(a) Student 训练", va="center", weight="bold", fontsize=10.5)
    ax.text(4, 12.8, "(b) 仿真闭环执行", va="center", weight="bold", fontsize=10.5)

    box(ax, 4, 41, 20, 7, "重标注专家数据", r"$D_E$")
    box(ax, 29, 41, 15, 7, "BC 初始化", accent=RUST, fill=warm)
    box(ax, 50, 41, 21, 7, "Student", r"$\pi_S(a_t\mid o_t,g,z_t)$", BLUE, cool)
    box(ax, 77, 41, 19, 7, "G1 / PhysX", "采集 Student 轨迹")
    arrow(ax, [(24, 44.5), (29, 44.5)], RUST)
    arrow(ax, [(44, 44.5), (50, 44.5)], RUST)
    arrow(ax, [(71, 44.5), (77, 44.5)], BLUE)

    box(ax, 16, 28, 37, 7, "DAgger 专家监督", "查询冻结 Teacher，聚合专家标签", RUST, warm)
    box(ax, 59, 28, 37, 7, "PPO 任务优化", "使用交互样本与任务回报", BLUE, cool)
    arrow(ax, [(80, 41), (80, 37.6), (34.5, 37.6), (34.5, 35)], RUST)
    arrow(ax, [(89, 41), (89, 35)], BLUE)
    ax.text(69, 38.15, r"访问状态与对应参考 $(s_t,r_t)$",
            ha="center", color=RUST, fontsize=8)

    box(ax, 16, 18.5, 80, 6, "联合更新",
        r"$L_k=(1-\alpha_k)L_{\mathrm{PPO}}+\alpha_kL_{\mathrm{act}}$", BLUE, cool)
    arrow(ax, [(34.5, 28), (34.5, 24.5)], RUST)
    arrow(ax, [(77.5, 28), (77.5, 24.5)], BLUE)
    arrow(ax, [(16, 21.5), (8, 21.5), (8, 39.7), (53, 39.7), (53, 41)], BLUE)
    ax.text(9, 27, "更新\n策略", color=BLUE, ha="left", va="center", fontsize=8)

    box(ax, 4, 4.5, 30, 6, "执行输入", r"$o_t,\ g,\ z_t$（96 维）")
    box(ax, 50, 4.5, 21, 6, "固定 Student", r"$\pi_S^*$", BLUE, cool)
    box(ax, 77, 4.5, 19, 6, "G1 / PhysX", "29 维关节位置目标")
    arrow(ax, [(60.5, 18.5), (60.5, 10.5)], BLUE)
    ax.text(62.4, 15.7, "导出策略", color=BLUE, fontsize=8, va="center")
    arrow(ax, [(34, 7.5), (50, 7.5)], BLUE)
    arrow(ax, [(71, 7.5), (77, 7.5)], BLUE)
    arrow(ax, [(86.5, 4.5), (86.5, 2), (19, 2), (19, 4.5)], GRAY, "--")
    ax.text(52.75, 2.35, r"本体观测 $o_{t+1}$", ha="center", fontsize=8, color=GRAY)
    save(fig, "fig04_teacher_student")


def scatter():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    fig.subplots_adjust(left=.13, right=.97, bottom=.15, top=.87)
    rnd = random.Random(42)
    groups = [(.60, 0, "前向", BLUE, (9, 12)), (.42, .34, "左前", "#327267", (8, 10)),
              (0, -.45, "右向", "#6f5d8f", (11, -13)), (-.38, 0, "后向", RUST, (-15, 15))]
    for x, y, label, color, offset in groups:
        points = [(rnd.gauss(x-(.012 if x < 0 else .004), .055 if x < 0 else .035),
                   rnd.gauss(y, .035 if abs(y) > .05 else .030)) for _ in range(75)]
        ax.scatter(*zip(*points), s=12, color=color, alpha=.40, edgecolors="none")
        ax.add_patch(Circle((x, y), .10, ec=color, fc="none", ls="--", lw=.85))
        ax.scatter(x, y, marker="x", color=INK, s=42, linewidths=1.35, zorder=4)
        ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", fontsize=9)
    ax.set(xlim=(-.61, .80), ylim=(-.61, .52), aspect="equal",
           xlabel=r"实际前后位移 $\Delta p_x$ (m)", ylabel=r"实际左右位移 $\Delta p_y$ (m)")
    ax.xaxis.set_major_locator(MultipleLocator(.2))
    ax.yaxis.set_major_locator(MultipleLocator(.2))
    grid(ax, "both")
    ax.legend(handles=[
        Line2D([], [], marker="x", ls="none", color=INK, label="目标"),
        Line2D([], [], marker="o", ls="none", ms=4, color=GRAY, label="合成落点"),
        Line2D([], [], ls="--", lw=1, color=GRAY, label="0.10 m 容差"),
    ], ncol=3, loc="lower center", bbox_to_anchor=(.5, 1.015))
    save(fig, "fig06_landing_scatter", "合成演示数据 · 每个目标 75 个示意样本")


def heatmap():
    fig, ax = plt.subplots(figsize=(6.35, 4.45))
    fig.subplots_adjust(left=.14, right=.88, bottom=.15, top=.96)
    values = np.array([
        [57, 68, 77, 84, 85, 78], [67, 77, 87, 92, 92, 86],
        [73, 84, 91, 95, 95, 93], [72, 83, 90, 95, 96, 94],
        [66, 76, 86, 92, 93, 88], [58, 69, 78, 85, 86, 80],
    ])
    x, y = np.arange(6)*.2-.4, np.arange(6)*.2-.5
    mesh = ax.pcolormesh(x, y, values, shading="nearest", cmap="Blues",
                         vmin=50, vmax=100, edgecolors="white", linewidth=.55)
    for row, col in np.ndindex(values.shape):
        value = values[row, col]
        ax.text(x[col], y[row], str(value), ha="center", va="center",
                color="white" if value >= 83 else INK, fontsize=9)
    ax.set(xticks=x, yticks=y, aspect="equal",
           xlabel=r"目标前后位移 $\Delta x^*$ (m)", ylabel=r"目标左右位移 $\Delta y^*$ (m)")
    fig.colorbar(mesh, ax=ax, pad=.05, ticks=np.arange(50, 101, 10),
                 label="联合成功率 (%)")
    save(fig, "fig07_success_heatmap", "合成演示数据 · 逐目标网格")


def dot_rows(ax, values, colors, fmt, pad):
    rows = np.arange(len(values))
    ax.scatter(values, rows, color=colors, s=28, zorder=3)
    for value, row in zip(values, rows):
        ax.text(value+pad, row, fmt.format(value), va="center", fontsize=9)
    ax.set_ylim(len(values)-.45, -.55)
    grid(ax, "x")
    ax.tick_params(axis="y", length=0)


def ablation():
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.2, 3.8), sharey=True)
    fig.subplots_adjust(left=.21, right=.96, bottom=.16, top=.88, wspace=.20)
    names = ["完整方法", "固定模仿权重", "名义参考位移标签", "无近邻检索增强",
             "无 DAgger", "无 PPO 目标", "无 Teacher"]
    colors = [BLUE] + [GRAY]*6
    dot_rows(a, [91.3, 87.8, 85.5, 83.6, 78.1, 75.2, 61.7], colors, "{:.1f}", 1)
    dot_rows(b, [.061, .073, .081, .088, .105, .116, .137], colors, "{:.3f}", .003)
    a.set(yticks=np.arange(7), yticklabels=names, xlim=(55, 102), xticks=[60,70,80,90,100],
          xlabel="联合成功率 (%)")
    b.set(xlim=(.045, .16), xticks=[.06,.09,.12,.15], xlabel="平均目标误差 (m)")
    panel(a, "(a) 联合成功率")
    panel(b, "(b) 平均目标误差")
    save(fig, "fig08_ablation", "合成演示数据 · 论文表 8")


def training():
    fig, axes = plt.subplots(2, 2, figsize=(8, 5.2))
    fig.subplots_adjust(left=.12, right=.97, top=.89, bottom=.14, hspace=.67, wspace=.36)
    teacher = np.linspace(0, 30000, 81)
    student = np.linspace(0, 160000, 81)
    specs = [
        ("(a) Teacher 跟踪", teacher, [smooth_curve(x, 12, 94, 6000, 1.5) for x in teacher],
         "归一化回报", (0, 100), BLUE),
        ("(b) Student 联合成功率", student, [smooth_curve(x, 5, 92, 36000, 1.5) for x in student],
         "联合成功率 (%)", (0, 100), BLUE),
        ("(c) Student 目标误差", student,
         .055+.225*np.exp(-student/33000)+.004*np.sin(student/6000), "平均误差 (m)", (0, .30), RUST),
        ("(d) 模仿权重调度", np.array([0, 9000, 20000]), [1, .1, .1],
         r"模仿权重 $\alpha_k$", (0, 1.05), GRAY),
    ]
    for ax, (title, x, y, label, limits, color) in zip(axes.flat, specs):
        panel(ax, title)
        ax.plot(x/1000, y, color=color, lw=1.55)
        ax.set(xlabel="更新步数 (千步)", ylabel=label, ylim=limits, xlim=(0, x[-1]/1000))
        grid(ax)
    save(fig, "fig09_training_curves", "(a)–(c) 合成示意曲线 · (d) 论文设定")


def cdf():
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.7, 3.7))
    fig.subplots_adjust(left=.10, right=.97, bottom=.19, top=.88, wspace=.39)
    x = np.linspace(0, .55, 551)
    z95 = NormalDist().inv_cdf(.95)
    for name, mean, q95, color, style in [
        ("完整方法", .061, .129, BLUE, "-"), ("DAgger", .083, .178, RUST, "--"),
        ("纯行为克隆", .112, .236, "#536d69", "-."), ("直接 PPO", .183, .352, GRAY, ":"),
    ]:
        if name == "完整方法":
            # Keep the error-only CDF above the joint success rates in table 9.
            errors = np.array([.01, .038, .05, .10, q95, .15, .20])
            fractions = np.array([0, .10, .72, .92, .95, .96, .975])
            partial_mean = np.sum(np.diff(fractions)*(errors[1:]+errors[:-1])/2)
            tail_endpoint = 2*(mean-partial_mean)/(1-fractions[-1])-errors[-1]
            cumulative = 100*np.interp(x, np.r_[errors, tail_endpoint], np.r_[fractions, 1])
        else:
            # Use a lognormal model that matches the reported mean and 95th percentile.
            sigma = z95 - np.sqrt(z95**2 - 2*np.log(q95/mean))
            mu = np.log(mean) - sigma**2/2
            normal_z = (np.log(x[1:])-mu)/sigma
            cumulative = np.r_[0, [50*(1+erf(z/np.sqrt(2))) for z in normal_z]]
        a.plot(x, cumulative, label=name, color=color, ls=style, lw=1.5)
    a.axvline(.10, color="#a1a9af", lw=.8, ls="--")
    a.set(xlim=(0,.55), ylim=(0,102), xlabel=r"目标误差 $e_p$ (m)", ylabel="累计比例 (%)")
    a.legend(loc="lower right", fontsize=8)
    panel(a, "(a) 目标误差 CDF（示意）")
    tolerances = [.05, .10, .15, .20]
    rates = [69.7,91.3,95.2,96.8]
    b.axvline(.10, color="#a1a9af", lw=.8, ls="--")
    b.plot(tolerances, rates, "o-", color=BLUE, lw=1.2, ms=4)
    for x, y in zip(tolerances, rates):
        b.annotate(f"{y:.1f}", (x,y), xytext=(0,6), textcoords="offset points", ha="center", fontsize=8)
    b.set(xlim=(.03,.22), ylim=(60,104), xticks=tolerances,
          xlabel="目标误差容差 (m)", ylabel="联合成功率 (%)")
    panel(b, "(b) 容差敏感性（表 9）")
    for ax in (a,b):
        grid(ax)
    save(fig, "fig10_error_cdf", "合成演示数据 · (a) 示意分布（匹配表 4 均值与 P95） · (b) 表 9")


def robustness():
    fig, (a,b) = plt.subplots(1, 2, figsize=(8.65, 3.65))
    fig.subplots_adjust(left=.18, right=.96, bottom=.19, top=.88, wspace=.41)
    labels = ["标称动力学", "摩擦随机化", "质量／质心随机化", "观测噪声", "20 ms 延迟", "联合随机化"]
    rates = [91.3,88.7,87.9,89.2,82.6,79.8]
    dot_rows(a, rates, [BLUE]+[GRAY]*5, "{:.1f}", 1)
    a.set(yticks=np.arange(6), yticklabels=labels, xlim=(50,101), xticks=[50,60,70,80,90,100],
          xlabel="联合成功率 (%)")
    panel(a, "(a) 扰动条件对比")
    delays, rates = [0,10,20,30,40], [91.3,88.9,82.6,73.4,61.2]
    b.plot(delays, rates, color=BLUE, lw=1.3, ls="--")
    b.scatter([0,20], [91.3,82.6], color=BLUE, s=24, zorder=3, label="表 10 条件")
    b.scatter([10,30,40], [88.9,73.4,61.2], facecolors="white", edgecolors=BLUE,
              s=24, zorder=3, label="补充演示点")
    b.set(xlim=(-2,42), ylim=(50,101), xticks=delays, xlabel="额外控制延迟 (ms)", ylabel="联合成功率 (%)")
    b.legend(fontsize=8, loc="lower left")
    panel(b, "(b) 控制延迟敏感性")
    grid(b)
    save(fig, "fig11_robustness", "合成演示数据 · 论文表 10 与补充延迟点")


if __name__ == "__main__":
    for draw in (target, augmentation, distillation, scatter, heatmap, ablation, training, cdf, robustness):
        draw()
