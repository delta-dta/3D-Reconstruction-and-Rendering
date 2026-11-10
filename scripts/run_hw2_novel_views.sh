#!/usr/bin/env bash
set -e

export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/shell/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/shell_novel.json > /data/260010047/3d_homework/outputs/novel_views/shell/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/shell_novel.json > /data/260010047/3d_homework/outputs/novel_views/shell/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/shell_novel.json > /data/260010047/3d_homework/outputs/novel_views/shell/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/can/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/can_novel.json > /data/260010047/3d_homework/outputs/novel_views/can/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_novel.json > /data/260010047/3d_homework/outputs/novel_views/can/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/can_novel.json > /data/260010047/3d_homework/outputs/novel_views/can/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/shoe/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/shoe_novel.json > /data/260010047/3d_homework/outputs/novel_views/shoe/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/shoe_novel.json > /data/260010047/3d_homework/outputs/novel_views/shoe/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/shoe_novel.json > /data/260010047/3d_homework/outputs/novel_views/shoe/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/brain/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/brain_novel.json > /data/260010047/3d_homework/outputs/novel_views/brain/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/brain_novel.json > /data/260010047/3d_homework/outputs/novel_views/brain/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/brain_novel.json > /data/260010047/3d_homework/outputs/novel_views/brain/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/stone/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/stone_novel.json > /data/260010047/3d_homework/outputs/novel_views/stone/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/stone_novel.json > /data/260010047/3d_homework/outputs/novel_views/stone/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/stone_novel.json > /data/260010047/3d_homework/outputs/novel_views/stone/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/candle/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/candle_novel.json > /data/260010047/3d_homework/outputs/novel_views/candle/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/candle_novel.json > /data/260010047/3d_homework/outputs/novel_views/candle/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/candle_novel.json > /data/260010047/3d_homework/outputs/novel_views/candle/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/jug/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/jug_novel.json > /data/260010047/3d_homework/outputs/novel_views/jug/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/jug_novel.json > /data/260010047/3d_homework/outputs/novel_views/jug/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/jug_novel.json > /data/260010047/3d_homework/outputs/novel_views/jug/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/owl/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/owl_novel.json > /data/260010047/3d_homework/outputs/novel_views/owl/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/owl_novel.json > /data/260010047/3d_homework/outputs/novel_views/owl/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/owl_novel.json > /data/260010047/3d_homework/outputs/novel_views/owl/logs/evaluate.log 2>&1

mkdir -p /data/260010047/3d_homework/outputs/novel_views/robot/logs
LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/robot_novel.json > /data/260010047/3d_homework/outputs/novel_views/robot/logs/render.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_novel.json > /data/260010047/3d_homework/outputs/novel_views/robot/logs/prepare.log 2>&1
/data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/robot_novel.json > /data/260010047/3d_homework/outputs/novel_views/robot/logs/evaluate.log 2>&1

# mkdir -p /data/260010047/3d_homework/outputs/novel_views/lamb/logs
# LD_LIBRARY_PATH=/data/260010047/3d_homework/.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 /data/260010047/3d_homework/.tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python /data/260010047/3d_homework/programs/render_hw2.py -- --config /data/260010047/3d_homework/configs/experiments/lamb_novel.json > /data/260010047/3d_homework/outputs/novel_views/lamb/logs/render.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/prepare_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_novel.json > /data/260010047/3d_homework/outputs/novel_views/lamb/logs/prepare.log 2>&1
# /data/260010047/miniconda3/envs/3dvision/bin/python -B /data/260010047/3d_homework/programs/evaluate_hw2.py --config /data/260010047/3d_homework/configs/experiments/lamb_novel.json > /data/260010047/3d_homework/outputs/novel_views/lamb/logs/evaluate.log 2>&1

