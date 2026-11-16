#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
# 已完成：31,607 个渲染模型全部判别，保留 7,819 个。
# OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 taskset -c 4,5,6,7,12,13 python programs/filter_previews_deepseek.py --config configs/preview_deepseek.json
