#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# robot_views24 明确允许部分注册，使用 API 最终返回重建导出，实际数量以 model/cameras.json 为准。
# 该条件的最终重算命令另记录在 rerun_robot_views24.sh。
# mkdir -p outputs/ablations/robot_views24/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/robot_views24.json > outputs/ablations/robot_views24/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/robot_views48/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/robot_views48.json > outputs/ablations/robot_views48/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/robot_views48.json > outputs/ablations/robot_views48/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/robot_views48.json > outputs/ablations/robot_views48/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/robot_views48.json > outputs/ablations/robot_views48/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/robot_gt_poses/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/robot_gt_poses.json > outputs/ablations/robot_gt_poses/logs/prepare.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/robot_gt_poses.json > outputs/ablations/robot_gt_poses/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/robot_gt_poses.json > outputs/ablations/robot_gt_poses/logs/evaluate.log 2>&1

