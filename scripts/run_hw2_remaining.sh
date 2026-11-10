#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_basket/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_basket.json > /data/260010047/3d_homework/outputs/hw2_basket/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_basket.json > /data/260010047/3d_homework/outputs/hw2_basket/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_basket.json > /data/260010047/3d_homework/outputs/hw2_basket/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_basket.json > /data/260010047/3d_homework/outputs/hw2_basket/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_basket.json > /data/260010047/3d_homework/outputs/hw2_basket/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_basket.json > /data/260010047/3d_homework/outputs/hw2_basket/logs/finalize.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_brain/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_brain.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_brain.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_brain.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_brain.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_brain.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_brain.json > /data/260010047/3d_homework/outputs/hw2_brain/logs/finalize.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_stone/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_stone.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_stone.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_stone.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_stone.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_stone.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_stone.json > /data/260010047/3d_homework/outputs/hw2_stone/logs/finalize.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_candle/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_candle.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_candle.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_candle.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_candle.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_candle.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_candle.json > /data/260010047/3d_homework/outputs/hw2_candle/logs/finalize.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_jug/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_jug.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_jug.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_jug.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_jug.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_jug.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_jug.json > /data/260010047/3d_homework/outputs/hw2_jug/logs/finalize.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_owl/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_owl.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_owl.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_owl.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_owl.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_owl.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_owl.json > /data/260010047/3d_homework/outputs/hw2_owl/logs/finalize.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/hw2_robot/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/hw2_robot.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/hw2_robot.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/reconstruct_hw2.py --config /data/260010047/3d_homework/configs/hw2_robot.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/sfm.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/train_hw2.py --config /data/260010047/3d_homework/configs/hw2_robot.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/train.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/hw2_robot.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/evaluate.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/finalize_hw2.py --config /data/260010047/3d_homework/configs/hw2_robot.json > /data/260010047/3d_homework/outputs/hw2_robot/logs/finalize.log 2>&1

