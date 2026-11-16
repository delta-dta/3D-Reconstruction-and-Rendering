# 环境、执行顺序与复现

作业2现在提供统一入口 `programs/run_pipeline.py`。从新克隆仓库开始运行时，先看[PIPELINE](PIPELINE.md)：在 `configs/pipeline.json` 设置数据与工具位置，再执行六阶段完整流程。下面保留正式实验的环境、命令记录及对照实验说明。

## 实验环境与工作目录

正式实验使用RTX 5090（32 GB），Conda环境名为 `3dvision`。从仓库根目录执行下列命令；在 `configs/pipeline.json` 中设置Objaverse数据根目录与工具位置。

```bash
conda env create -f environment.yml
conda activate 3dvision
```

Python 程序使用该环境；Blender 使用自带 Python。环境定义在 `environment.yml`，不继承系统 Python 的 site-packages。

## 已完成命令的约定

启动脚本均不接收参数。具体对象、实验参数与结果目录在对应 JSON 配置中。执行完成的完整命令已用 `#` 注释保留；复现时取消需要执行的命令注释。清洗的续跑依据已有进度，其他实验按指定目录执行，不自动尝试其他配置。

重新做实验时建议复制对应配置，明确改成一个新的输出目录，再把该配置的完整命令加入启动脚本。这样可以同时保留原有结果与修改后的实验。

## 数据清洗

| 顺序 | 启动脚本 | 主要输出 |
|---|---|---|
| 1 | `scripts/run_coarse_filter.sh` | `outputs/coarse_candidates.jsonl` |
| 2 | `scripts/run_glb_filter.sh` | `outputs/material_candidates.jsonl` |
| 3 | `scripts/run_render_full.sh` | `outputs/full_frames/`、`outputs/full_render/` |
| 4 | `scripts/run_preview_deepseek.sh` | `cleaned/cleaned_models.jsonl` 与 UID 清单 |
| 5 | `scripts/run_finalize_cleaning.sh` | CSV、页面、10 物体清单 |

正式清洗清单已保存在 `results/assignment1/`，后续重建可直接按清单准备源GLB。完整清洗参数在 `configs/`，实际筛选提示词与请求设置见 [PROMPTS](PROMPTS.md)。

## 作业 2 单物体与 10 物体主实验

羊摆件的阶段脚本为 `run_hw2_render_lamb.sh`、`run_hw2_prepare_lamb.sh`、`run_hw2_sfm_lamb.sh`、`run_hw2_train_lamb.sh`、`run_hw2_evaluate_lamb.sh`、`run_hw2_finalize_lamb.sh`。它们现在调用共用的 `programs/*_hw2.py`。

其余对象的固定完整命令集中在：

| 脚本 | 对象 |
|---|---|
| `scripts/run_hw2_first_two.sh` | shell、can |
| `scripts/run_hw2_remaining.sh` | brain、stone、candle、jug、owl、robot；另保留 basket 的 SfM 案例命令 |
| `scripts/run_hw2_shoe.sh` | shoe，替换重复纹理导致位姿歧义的 basket 候选 |

每个对象严格按 render → prepare → reconstruct → train → evaluate → finalize 执行。输出位于 `outputs/hw2_对象/`，各阶段日志在 `logs/`。

进度查看：

```bash
python -B programs/course_status.py
```

训练日志包含 tqdm 的回车更新。查看进度优先读取 `training_progress.json`，避免用按行 tail 打印很长的进度条内容。

## 对照实验

| 脚本 | 条件 | 是否重新训练 |
|---|---|---|
| `scripts/run_hw2_checkpoints.sh` | 全部 10 物体，7k 模型同测试集评估 | 否 |
| `scripts/run_hw2_ablations_lamb_can.sh` | lamb/can，各 views24、views48、gt_poses | 是，共 6 次 |
| `scripts/run_hw2_ablations_robot.sh` | robot 的 views24、views48、gt_poses | 是，共 3 次 |
| `scripts/run_hw2_novel_views.sh` | 全部 10 物体，0°/30°/60°各 12 个新视角 | 否，生成参考图并评价 |
| `scripts/run_finalize_course.sh` | 聚合报告、图表、精简结果和网页 | 否 |

视图数量子集由 `prepare_hw2_experiment.py` 准备，RGB 与掩码使用硬链接，不重复复制。该准备步骤应在新的输出目录执行；已经建立的数据保留在原处。

位姿对照保持相同稀疏点，只设置真实训练外参。新高度评估通过 `model_dir` 明确读取主实验模型，并在独立目录保存图像与指标。

机器人24图与48图条件分别注册24/24和48/48张相机，对齐后的旋转误差中位数分别为66.976°和17.824°。各条件使用实际恢复结果训练，在相同留出视角上评价；正式96图基线恢复正确环绕相机结构。具体数据见 [EXPERIMENTS](EXPERIMENTS.md)。

## 新环境搭建

1. 根据 `environment.yml` 创建并激活 `3dvision`。
2. 使用CUDA 12.9与兼容GCC；正式实验使用GCC 13.3。RTX 5090构建设置为 `TORCH_CUDA_ARCH_LIST=12.0`。
3. 按 [PIPELINE](PIPELINE.md) 获取固定提交的官方3DGS，初始化三个计算子模块、应用标准头文件补丁并安装扩展。
4. 准备Blender 4.5.3至 `.tools/blender-4.5.3-linux-x64/`，安装所需系统图形库。附加库目录可在 `configs/pipeline.json` 的 `blender_library_path` 中设置。
5. 使源 Objaverse 文件位于配置指定路径。可先依照 `results/assignment1/cleaned_uids.txt` 准备所需对象，再复现单物体。

阶段脚本记录正式实验命令。跨机器复现主流程使用统一入口 `programs/run_pipeline.py`，按仓库位置解析项目路径，在 `configs/pipeline.json` 中设置数据与工具位置。物体和对照配置中的项目路径均从仓库根目录解析。

## 结果保存在哪里

| 目录 | 用途 |
|---|---|
| `cleaned/` | 本机完整清洗结果与预览 |
| `outputs/full_frames/` | 清洗中间渲染，可复用做外观判别 |
| `outputs/hw2_*/` | 10 物体完整输入、SfM、3DGS、检查点和评价 |
| `outputs/ablations/` | 9 个对照条件的完整过程 |
| `outputs/novel_views/` | 360 张新高度参考图及对照 |
| `results/` | 可提交的匹配、GIF、指标、必要相机数据和图表 |
| `docs/` | 正式报告、实验、复现、提示词与资产署名 |

必要条件都已写入配置。优先复制一个已有配置开展下一次实验，保持测试划分固定，再对照新的指标与误差图。

## 正式报告的 Markdown 与 PDF

第一组的正式报告为 `docs/HOMEWORK2_REPORT.md`，导出文件为 `docs/HOMEWORK2_REPORT.pdf`。组员姓名、分工和目标仓库记录在 `configs/submission.json`。

PDF导出使用WeasyPrint 66.0，依赖系统Pango、Harfbuzz、Fontconfig和Noto CJK字体。新Ubuntu环境按官方安装说明准备 `libpango-1.0-0`、`libpangoft2-1.0-0`、`libharfbuzz0b`、`libharfbuzz-subset0` 和 `fonts-noto-cjk`，Python依赖在 `environment.yml` 与 `configs/report_requirements.txt` 中。

```bash
conda activate 3dvision
python -B programs/prepare_submission.py
python -B programs/export_hw2_report.py
```

第一条命令只同步组员、仓库、课程概览与结果首页，不重跑训练或改动实验指标。第二条从Markdown转换PDF，将图像嵌入文件，并将PDF内的相对文件链接转换成目标GitHub仓库中的路径。导出时核对十物体主表、UID、实际筛选提示词与中文文字提取；摘要在 `results/submission_verification.json`，逐页预览在 `outputs/report_export/`。

阶段评价读取7k/30k高斯PLY；最终恢复状态用于继续训练。扩展编译步骤见 [PIPELINE](PIPELINE.md)。
