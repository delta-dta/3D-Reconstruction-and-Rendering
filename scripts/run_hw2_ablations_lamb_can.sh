#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# mkdir -p outputs/ablations/lamb_views24/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/lamb_views24.json > outputs/ablations/lamb_views24/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/lamb_views24.json > outputs/ablations/lamb_views24/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/lamb_views24.json > outputs/ablations/lamb_views24/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/lamb_views24.json > outputs/ablations/lamb_views24/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/lamb_views48/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/lamb_views48.json > outputs/ablations/lamb_views48/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/lamb_views48.json > outputs/ablations/lamb_views48/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/lamb_views48.json > outputs/ablations/lamb_views48/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/lamb_views48.json > outputs/ablations/lamb_views48/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/lamb_gt_poses/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/lamb_gt_poses.json > outputs/ablations/lamb_gt_poses/logs/prepare.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/lamb_gt_poses.json > outputs/ablations/lamb_gt_poses/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/lamb_gt_poses.json > outputs/ablations/lamb_gt_poses/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/can_views24/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/can_views24.json > outputs/ablations/can_views24/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/can_views24.json > outputs/ablations/can_views24/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/can_views24.json > outputs/ablations/can_views24/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/can_views24.json > outputs/ablations/can_views24/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/can_views48/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/can_views48.json > outputs/ablations/can_views48/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/experiments/can_views48.json > outputs/ablations/can_views48/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/can_views48.json > outputs/ablations/can_views48/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/can_views48.json > outputs/ablations/can_views48/logs/evaluate.log 2>&1

# mkdir -p outputs/ablations/can_gt_poses/logs
# python -B programs/prepare_hw2_experiment.py --config configs/experiments/can_gt_poses.json > outputs/ablations/can_gt_poses/logs/prepare.log 2>&1
# python -B programs/train_hw2.py --config configs/experiments/can_gt_poses.json > outputs/ablations/can_gt_poses/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/can_gt_poses.json > outputs/ablations/can_gt_poses/logs/evaluate.log 2>&1

