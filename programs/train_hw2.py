"""Optimize an object's 3D Gaussians with the official implementation."""

import argparse
import csv
import json
from pathlib import Path
import random
import sys
import time

import numpy as np
import pycolmap
import torch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    root = Path(config['output_dir'])
    sys.path.insert(0, config['gaussian_repo'])
    import train as trainer
    from arguments import ModelParams, OptimizationParams, PipelineParams
    from utils.general_utils import safe_state
    from fused_ssim import fused_ssim
    from simple_knn._C import distCUDA2
    import diff_gaussian_rasterization

    torch.set_num_threads(4)
    safe_state(False)
    random.seed(config['seed'])
    np.random.seed(config['seed'])
    torch.manual_seed(config['seed'])
    probe = torch.rand((16, 3), device='cuda')
    assert torch.isfinite(distCUDA2(probe)).all()
    image = torch.rand((1, 3, 32, 32), device='cuda', requires_grad=True)
    fused_ssim(image, image.detach()).backward()
    parameters = argparse.ArgumentParser()
    lp, op, pp = ModelParams(parameters), OptimizationParams(parameters), PipelineParams(parameters)
    args = parameters.parse_args([])
    args.source_path = str(root / 'data')
    args.model_path = str(root / 'model')
    args.resolution = 1
    args.white_background = config['training']['white_background']
    args.sh_degree = config['training']['sh_degree']
    args.eval = False
    args.data_device = 'cuda'
    args.iterations = config['training']['iterations']
    args.position_lr_max_steps = args.iterations
    args.densify_until_iter = config['training']['densify_until_iter']
    args.random_background = config['training']['random_background']
    args.depth_l1_weight_init = 0.0
    args.depth_l1_weight_final = 0.0
    dataset, optimization, pipeline = lp.extract(args), op.extract(args), pp.extract(args)
    (root / 'model').mkdir(exist_ok=True)
    splits = json.loads((root / 'data/splits.json').read_text())
    registered = pycolmap.Reconstruction(str(root / 'data/sparse/0')).num_reg_images()
    initialization = 'COLMAP estimated cameras and triangulated points, aligned by training camera centers'
    if config.get('experiment', {}).get('kind') == 'gt_poses':
        initialization = 'Ground-truth training cameras; identical COLMAP sparse-point initialization to the 96-view baseline'
    (root / 'model' / 'training_config.json').write_text(json.dumps({
        'model': vars(dataset), 'optimization': vars(optimization), 'pipeline': vars(pipeline),
        'seed': config['seed'], 'train_images': registered, 'input_train_images': len(splits['train']), 'held_out_test_images': len(splits['test']),
        'initialization': initialization,
    }, indent=2) + '\n')
    start = time.monotonic()
    log = (root / 'model' / 'loss.csv').open('w', newline='')
    writer = csv.writer(log)
    writer.writerow(['iteration', 'loss', 'l1', 'gaussians', 'elapsed_seconds'])

    def report(tb_writer, iteration, ll1, loss, loss_function, elapsed, testing_iterations, scene, render_function, render_args, train_test_exp):
        if iteration != 1 and iteration % 100 != 0 and iteration != args.iterations:
            return
        snapshot = {'iteration': iteration, 'total': args.iterations, 'loss': float(loss.detach()),
            'l1': float(ll1.detach()), 'gaussians': len(scene.gaussians.get_xyz),
            'elapsed_seconds': round(time.monotonic() - start, 2), 'complete': False}
        writer.writerow([snapshot[key] for key in ['iteration', 'loss', 'l1', 'gaussians', 'elapsed_seconds']])
        log.flush()
        temporary = root / 'training_progress.tmp'
        temporary.write_text(json.dumps(snapshot) + '\n')
        temporary.replace(root / 'training_progress.json')
        if iteration == 1 or iteration % 1000 == 0:
            print(json.dumps(snapshot), flush=True)

    trainer.training_report = report
    trainer.training(dataset, optimization, pipeline, [], config['training']['save_iterations'],
        config['training']['checkpoint_iterations'], None, -1)
    log.close()
    progress = json.loads((root / 'training_progress.json').read_text())
    progress.update({'complete': True, 'elapsed_seconds': round(time.monotonic() - start, 2)})
    (root / 'training_progress.json').write_text(json.dumps(progress) + '\n')
    (root / 'model' / 'summary.json').write_text(json.dumps(progress, indent=2) + '\n')
    print(json.dumps(progress), flush=True)


if __name__ == '__main__':
    main()
