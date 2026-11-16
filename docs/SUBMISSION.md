# 第一组：作业2提交说明

组号：**第一组**。成员代称：**成员1、成员2、成员3、成员4**。四人按相近工作量分配，各预计25%，具体任务见正式报告第1节及 `configs/submission.json`；提交前核对实际贡献。

GitHub仓库：**https://github.com/delta-dta/3D-Reconstruction-and-Rendering**  
Git克隆地址：`https://github.com/delta-dta/3D-Reconstruction-and-Rendering.git`

## 作业网站提交两项

1. **报告附件**：[HOMEWORK2_REPORT.pdf](HOMEWORK2_REPORT.pdf)。报告包含完整流程、实际结果、影响因素实验、组号、成员分工和GitHub链接。[Markdown源文件](HOMEWORK2_REPORT.md)与PDF同源，随仓库保存。
2. **GitHub仓库链接**：将上面的仓库地址填入网站的链接栏；若无独立链接栏，写入提交备注。报告开头与正文中也已列出该地址。

网站备注可直接填写：

```text
第一组：成员1、成员2、成员3、成员4。
作业2采用SIFT/COLMAP + 3D Gaussian Splatting，完成10物体重建、匹配结果与10个GIF。
GitHub：https://github.com/delta-dta/3D-Reconstruction-and-Rendering
报告：HOMEWORK2_REPORT.pdf。代码、完整业务提示词、匹配结果与GIF见仓库。
```

原始要求未限定报告格式；PDF用于直接阅读，Markdown提供可编辑源文件。仓库使用main分支，包含下表中的代码、提示词、匹配结果和动画。网站提交PDF及仓库链接。

## 仓库内容与要求对应

| 要求 | 文件位置 |
|---|---|
| 流程文档、分析与发现 | `docs/HOMEWORK2_REPORT.md`、`.pdf`；`docs/EXPERIMENTS.md` |
| 完整代码与配置 | `programs/`、`configs/`、`scripts/`、`patches/`、`environment.yml` |
| 统一pipeline入口 | `programs/run_pipeline.py`、`configs/pipeline.json`、`docs/PIPELINE.md` |
| 作业1清洗数据来源 | `results/assignment1/` 的清洗清单、10物体UID与源SHA |
| 全部业务提示词 | `configs/preview_deepseek.json`、`docs/PROMPTS.md`；AI辅助范围在 `docs/AI_USAGE.md` |
| 全部10物体匹配 | `results/hw2_*/sfm/`：4张匹配图、完整验证图像对CSV、关键点与内点NPZ |
| 每物体GIF | `results/hw2_*/reconstruction.gif`，共10个，各72帧 |
| 对照结果 | `results/ablations/`、`experiments.csv`、`iterations.csv`、`novel_views.csv` |
| 成员与贡献安排 | 报告第1节、`configs/submission.json` |
| 环境与复现 | `docs/REPRODUCE.md`、`environment.yml`、固定官方代码版本 |
| 可浏览展示 | 根目录 `index.html` 与每物体结果页 |

## 下载包与离线阅读

`dist/coursework_submission.zip` 是本地已提交Git内容的完整快照，包含报告、源码、配置与精简结果，可作为补充附件或备份。下载后完整解压，再用浏览器打开根目录 `index.html`。需要保留 `results/`、`docs/` 与首页的相对位置，单独下载HTML不包含图片。PDF的图像已嵌入，可单独下载阅读；PDF文件链接指向GitHub。

完整训练数据、数据库、PLY与最终检查点保留在本机 `outputs/`，用于学习和优化。工具、Conda、API Key、大型检查点和中间缓存不进入Git或提交包。资产署名和第三方来源见 `ASSET_CREDITS.md`、`THIRD_PARTY.md`。

## 仓库推送

后续修改完成后，使用已经配置好的origin推送：

```bash
git -c safe.directory=/data/260010047/3d_homework push -u origin main
```

不要将API Key、`.tools/`、Conda环境或整个 `outputs/` 加入提交。
