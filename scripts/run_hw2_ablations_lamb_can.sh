#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/lamb_views24/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/lamb_views24.json > /data/260010047/3d_homework/outputs/ablations/lamb_views24/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_views24.json > /data/260010047/3d_homework/outputs/ablations/lamb_views24/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_views24.json > /data/260010047/3d_homework/outputs/ablations/lamb_views24/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_views24.json > /data/260010047/3d_homework/outputs/ablations/lamb_views24/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/lamb_views48/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/lamb_views48.json > /data/260010047/3d_homework/outputs/ablations/lamb_views48/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_views48.json > /data/260010047/3d_homework/outputs/ablations/lamb_views48/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_views48.json > /data/260010047/3d_homework/outputs/ablations/lamb_views48/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_views48.json > /data/260010047/3d_homework/outputs/ablations/lamb_views48/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/lamb_gt_poses/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/lamb_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/lamb_gt_poses/logs/prepare.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/lamb_gt_poses/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/lamb_gt_poses/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/can_views24/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/can_views24.json > /data/260010047/3d_homework/outputs/ablations/can_views24/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_views24.json > /data/260010047/3d_homework/outputs/ablations/can_views24/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_views24.json > /data/260010047/3d_homework/outputs/ablations/can_views24/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_views24.json > /data/260010047/3d_homework/outputs/ablations/can_views24/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/can_views48/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/can_views48.json > /data/260010047/3d_homework/outputs/ablations/can_views48/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_views48.json > /data/260010047/3d_homework/outputs/ablations/can_views48/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_views48.json > /data/260010047/3d_homework/outputs/ablations/can_views48/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_views48.json > /data/260010047/3d_homework/outputs/ablations/can_views48/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/can_gt_poses/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/can_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/can_gt_poses/logs/prepare.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/can_gt_poses/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/can_gt_poses/logs/evaluate.log 2>&1

