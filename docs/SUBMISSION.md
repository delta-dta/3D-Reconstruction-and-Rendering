# 提交说明

实验和材料由项目代码生成；组号、成员姓名及实际分工、目标 GitHub 地址目前尚未确定，集中填写在 `configs/submission.json`。成员条目格式为 `{"name":"姓名","contribution":"实际贡献"}`。填写后重新生成课程报告。

## 对应作业要求

| 要求 | 项目中的内容 |
|---|---|
| 使用作业 1 清洗数据 | 完整清洗清单、10 物体 UID 与源 SHA，`results/assignment1/` |
| 完整图像 → 重建 → NeRF 或 3DGS 流程 | `programs/`、`configs/`、`scripts/` 与 `docs/COURSE_REPORT.md` |
| 10 个不同物体 | `configs/hw2_course.json` 与十个结果目录 |
| 每物体一张 GIF | `results/hw2_*/reconstruction.gif` |
| 全部物体的匹配结果 | 每个 `sfm/` 下匹配图、全部验证图像对 CSV、关键点与全部内点 NPZ |
| 流程影响分析 | `docs/EXPERIMENTS.md`，图像数、位姿、时长、新高度测试 |
| 全部提示词 | `configs/preview_deepseek.json`、`docs/PROMPTS.md`、`docs/AI_USAGE.md` |
| 环境与复现 | `environment.yml`、固定源代码提交、CUDA 补丁和复现说明 |
| 组号、成员、贡献 | `configs/submission.json`，由本人填写 |
| GitHub 链接 | 目标仓库确定后填入配置与报告 |

## 本地与仓库内容

本机完整 `outputs/` 与 `cleaned/` 用于学习和继续优化。仓库提交 `results/` 的精简成果、源码、配置与文档；中间缓存、Conda、编译工具、API Key 和大型训练检查点通过 `.gitignore` 排除。

课程压缩包 `dist/coursework_submission.zip` 由本地 Git 中已提交内容生成，可离线解压查看根目录 `index.html`。Markdown 报告在 GitHub 中直接阅读；网页也可在本地浏览器打开。

## 上传目标仓库

待目标仓库创建并授权后，在项目目录设置远程地址并推送。下面的仓库地址需要替换成自己的实际地址：

```bash
git -c safe.directory=/data/260010047/3d_homework remote add origin https://github.com/你的账号/你的仓库.git
git -c safe.directory=/data/260010047/3d_homework push -u origin main
```

命令中的 `safe.directory` 用于当前容器与共享目录的所有者差异，不修改全局 Git 配置。更换目录时对应修改。

不要把 `ds_api_key`、`.env`、`.tools/`、Conda 环境或整个 `outputs/` 加入提交。资产署名和第三方代码来源见 `ASSET_CREDITS.md`、`THIRD_PARTY.md`。
