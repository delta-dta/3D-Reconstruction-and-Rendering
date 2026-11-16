#!/usr/bin/env bash
set -e

# 从仓库根目录运行，先激活 3dvision。
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/3dvision-cuda-cache
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=1

# 编织器物仅保留为匹配歧义案例：前三阶段完成，训练中止，未执行其评估与 GIF。
# 正式对象由 run_hw2_shoe.sh 中的彩色跑鞋替换。
# mkdir -p outputs/hw2_basket/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_basket.json > outputs/hw2_basket/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_basket.json > outputs/hw2_basket/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_basket.json > outputs/hw2_basket/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_basket.json > outputs/hw2_basket/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_basket.json > outputs/hw2_basket/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_basket.json > outputs/hw2_basket/logs/finalize.log 2>&1

# mkdir -p outputs/hw2_brain/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_brain.json > outputs/hw2_brain/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_brain.json > outputs/hw2_brain/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_brain.json > outputs/hw2_brain/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_brain.json > outputs/hw2_brain/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_brain.json > outputs/hw2_brain/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_brain.json > outputs/hw2_brain/logs/finalize.log 2>&1

# mkdir -p outputs/hw2_stone/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_stone.json > outputs/hw2_stone/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_stone.json > outputs/hw2_stone/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_stone.json > outputs/hw2_stone/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_stone.json > outputs/hw2_stone/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_stone.json > outputs/hw2_stone/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_stone.json > outputs/hw2_stone/logs/finalize.log 2>&1

# mkdir -p outputs/hw2_candle/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_candle.json > outputs/hw2_candle/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_candle.json > outputs/hw2_candle/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_candle.json > outputs/hw2_candle/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_candle.json > outputs/hw2_candle/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_candle.json > outputs/hw2_candle/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_candle.json > outputs/hw2_candle/logs/finalize.log 2>&1

# mkdir -p outputs/hw2_jug/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_jug.json > outputs/hw2_jug/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_jug.json > outputs/hw2_jug/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_jug.json > outputs/hw2_jug/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_jug.json > outputs/hw2_jug/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_jug.json > outputs/hw2_jug/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_jug.json > outputs/hw2_jug/logs/finalize.log 2>&1

# mkdir -p outputs/hw2_owl/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_owl.json > outputs/hw2_owl/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_owl.json > outputs/hw2_owl/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_owl.json > outputs/hw2_owl/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_owl.json > outputs/hw2_owl/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_owl.json > outputs/hw2_owl/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_owl.json > outputs/hw2_owl/logs/finalize.log 2>&1

# mkdir -p outputs/hw2_robot/logs
# LD_LIBRARY_PATH=.tools/system-libs/usr/lib/x86_64-linux-gnu taskset -c 0,1,2,3 .tools/blender-4.5.3-linux-x64/blender --background -t 4 --factory-startup --python-exit-code 1 --python programs/render_hw2.py -- --config configs/hw2_robot.json > outputs/hw2_robot/logs/render.log 2>&1
# python -B programs/prepare_hw2.py --config configs/hw2_robot.json > outputs/hw2_robot/logs/prepare.log 2>&1
# OMP_NUM_THREADS=12 python -B programs/reconstruct_hw2.py --config configs/hw2_robot.json > outputs/hw2_robot/logs/sfm.log 2>&1
# python -B programs/train_hw2.py --config configs/hw2_robot.json > outputs/hw2_robot/logs/train.log 2>&1
# python -B programs/evaluate_hw2.py --config configs/hw2_robot.json > outputs/hw2_robot/logs/evaluate.log 2>&1
# python -B programs/finalize_hw2.py --config configs/hw2_robot.json > outputs/hw2_robot/logs/finalize.log 2>&1

