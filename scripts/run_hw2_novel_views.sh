#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# mkdir -p outputs/novel_views/shell/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/shell_novel.json > outputs/novel_views/shell/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/shell_novel.json > outputs/novel_views/shell/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/shell_novel.json > outputs/novel_views/shell/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/can/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/can_novel.json > outputs/novel_views/can/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/can_novel.json > outputs/novel_views/can/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/can_novel.json > outputs/novel_views/can/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/shoe/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/shoe_novel.json > outputs/novel_views/shoe/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/shoe_novel.json > outputs/novel_views/shoe/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/shoe_novel.json > outputs/novel_views/shoe/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/brain/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/brain_novel.json > outputs/novel_views/brain/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/brain_novel.json > outputs/novel_views/brain/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/brain_novel.json > outputs/novel_views/brain/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/stone/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/stone_novel.json > outputs/novel_views/stone/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/stone_novel.json > outputs/novel_views/stone/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/stone_novel.json > outputs/novel_views/stone/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/candle/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/candle_novel.json > outputs/novel_views/candle/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/candle_novel.json > outputs/novel_views/candle/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/candle_novel.json > outputs/novel_views/candle/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/jug/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/jug_novel.json > outputs/novel_views/jug/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/jug_novel.json > outputs/novel_views/jug/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/jug_novel.json > outputs/novel_views/jug/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/owl/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/owl_novel.json > outputs/novel_views/owl/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/owl_novel.json > outputs/novel_views/owl/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/owl_novel.json > outputs/novel_views/owl/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/robot/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/robot_novel.json > outputs/novel_views/robot/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/robot_novel.json > outputs/novel_views/robot/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/robot_novel.json > outputs/novel_views/robot/logs/evaluate.log 2>&1

# mkdir -p outputs/novel_views/lamb/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/experiments/lamb_novel.json > outputs/novel_views/lamb/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/experiments/lamb_novel.json > outputs/novel_views/lamb/logs/prepare.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/experiments/lamb_novel.json > outputs/novel_views/lamb/logs/evaluate.log 2>&1

