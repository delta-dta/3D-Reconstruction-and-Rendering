#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/evaluate.log 2>&1
