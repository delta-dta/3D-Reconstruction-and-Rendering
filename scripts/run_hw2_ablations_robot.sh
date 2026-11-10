#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# robot_views24 明确允许部分注册，使用 API 最终返回重建导出，实际数量以 model/cameras.json 为准。
# 该条件的最终重算命令另记录在 rerun_robot_views24.sh。
# mkdir -p /data/260010047/3d_homework/outputs/ablations/robot_views24/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views24.json > /data/260010047/3d_homework/outputs/ablations/robot_views24/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/robot_views48/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/robot_views48.json > /data/260010047/3d_homework/outputs/ablations/robot_views48/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views48.json > /data/260010047/3d_homework/outputs/ablations/robot_views48/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views48.json > /data/260010047/3d_homework/outputs/ablations/robot_views48/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_views48.json > /data/260010047/3d_homework/outputs/ablations/robot_views48/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/ablations/robot_gt_poses/logs
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2_experiment.py --config /data/260010047/3d_homework/configs/experiments/robot_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/robot_gt_poses/logs/prepare.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/robot_gt_poses/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_gt_poses.json > /data/260010047/3d_homework/outputs/ablations/robot_gt_poses/logs/evaluate.log 2>&1

