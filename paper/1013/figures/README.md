# 论文图片清单

本目录包含论文配图的可编辑SVG、PNG预览和PDF排版版本。数值结果沿用论文声明的虚构仿真数据，不代表实际代码输出。

| 图号 | 文件 | 建议图题 | 建议放置位置 |
| --- | --- | --- | --- |
| 图1 | `fig01_overall_framework` | 训练与部署信息分离的整体框架 | 第3节开头 |
| 图2 | `fig02_target_displacement_command` | 二维目标位移命令及坐标定义 | 3.1问题定义 |
| 图3 | `fig03_reference_augmentation` | 基于运动特征近邻检索的参考数据增强 | 3.3参考族构建 |
| 图4 | `fig04_teacher_student` | Teacher–Student信息接口与DAgger-PPO联合优化 | 3.7联合优化 |
| 图5 | `fig05_jump_sequence` | 单次目标位移跳跃的动作阶段 | 5.1总体性能 |
| 图6 | `fig06_landing_scatter` | 目标位置与实际落点分布 | 5.3目标区域性能 |
| 图7 | `fig07_success_heatmap` | 二维目标空间上的联合成功率 | 5.3目标区域性能 |
| 图8 | `fig08_ablation` | 方法对比与关键模块消融 | 5.5模块消融 |
| 图9 | `fig09_training_curves` | Teacher与Student训练过程 | 5.6训练过程与收敛性 |
| 图10 | `fig10_error_cdf` | 目标位移误差累计分布 | 5.7容差敏感性 |
| 图11 | `fig11_robustness` | 动力学随机化与控制延迟下的鲁棒性 | 5.8鲁棒性实验 |

## 新增流程图与概览图

`overview/` 目录包含两张基于最新论文正文重新整理的补充视觉稿：

- `method_training_flow`：详细展示参考族构建、Teacher、实际位移重标注、DAgger-PPO闭环与部署接口，适合方法章节或答辩讲解。
- `graphical_abstract`：将任务定义、四阶段训练、部署接口、动作阶段、联合成功判据和论文主要合成数字集中在一页，适合首页概览或答辩开场。
- `fig01_overall_framework_v2`：面向正式论文主图的图像主导版本。参考机器人学习论文常见的“动作画面 + 少量算法信息流”构图，弱化外框、公式和长文本，突出参考族、Teacher物理执行、实际位移重标注、Student蒸馏及目标条件部署。

两张图均提供SVG、PNG和PDF格式。图形摘要复用了`fig05_jump_sequence_raw.png`中的AI生成机器人动作示意；图中的性能数字仍属于论文声明的合成演示数据。

重新生成：

```bash
python 1013/figures/generate_overview_figures.py
python 1013/figures/generate_paper_style_framework.py
```

## 格式

- 根目录下的 `.svg`：可编辑矢量源图。
- `png/`：1600×900左右的预览和Markdown插图。
- `pdf/`：论文排版用矢量PDF。
- `refine_paper_figures.py`：图2–4及图6–11的当前绘图脚本，一次导出SVG、PNG和PDF。
- `generate_figures.py`：初稿生成脚本，用于图1与图5。全量运行会重新生成旧版SVG。

## 图5说明

`fig05_jump_sequence_raw.png` 使用内置图像生成工具制作，提示词为：

> 为机器人论文生成一幅白色背景、七阶段、同一人形机器人完成前向站立跳跃的连续三维技术渲染；阶段包括准备、下蹲、起跳、早期腾空、腾空顶点、双脚触地和稳定恢复；机器人外观与比例保持一致，不含文字、箭头、标识或水印。

该图只用于动作阶段示意，不是仿真结果。正式论文应使用真实仿真视频按统一时间戳截取连续帧替换。

## 数据声明

图6—图11使用论文中的虚构数据和补充演示数据。图9(a)–(c)为公式生成的示意曲线。图10(a)使用表4的汇总值构造误差CDF，图10(b)使用表9的联合成功率。导入真实评测结果后，可更新绘图脚本中的数据并重新生成。脚本需要 NumPy、Matplotlib 和 Noto Sans CJK 字体。

```bash
python 1013/figures/refine_paper_figures.py
```
