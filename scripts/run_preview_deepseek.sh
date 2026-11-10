#!/usr/bin/env bash
set -e

# 已完成：31,607 个渲染模型全部判别，保留 7,819 个。
# OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 taskset -c 4,5,6,7,12,13 /data/260010047/miniconda3/envs/3dvision/bin/python /data/260010047/3d_homework/programs/filter_previews_deepseek.py --config /data/260010047/3d_homework/configs/preview_deepseek.json
