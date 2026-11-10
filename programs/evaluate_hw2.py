"""Evaluate held-out views and optionally render an orbit from trained Gaussians."""

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw
import torch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    root = Path(config['output_dir'])
    sys.path.insert(0, config['gaussian_repo'])
    from arguments import PipelineParams
    from gaussian_renderer import render
    from scene import GaussianModel
    from scene.cameras import MiniCam
    from utils.graphics_utils import getProjectionMatrix
    from utils.loss_utils import ssim

    torch.set_num_threads(4)
    metadata = json.loads((root / 'data/metadata.json').read_text())
    model_dir = Path(config.get('model_dir', str(root / 'model')))
    training = json.loads((model_dir / 'summary.json').read_text())
    training_config = json.loads((model_dir / 'training_config.json').read_text())
    assert training['complete'] and training['iteration'] >= config['evaluation']['iteration']
    evaluation = root / config['evaluation'].get('directory', 'evaluation')
    (evaluation / 'test_renders').mkdir(parents=True, exist_ok=True)
    (evaluation / 'comparisons').mkdir(exist_ok=True)
    (root / 'orbit').mkdir(exist_ok=True)
    width, height = metadata['width'], metadata['height']
    intrinsic = np.array(metadata['intrinsic'])
    fovx, fovy = 2 * math.atan(width / (2 * intrinsic[0,0])), 2 * math.atan(height / (2 * intrinsic[1,1]))
    projection = getProjectionMatrix(znear=0.01, zfar=100, fovX=fovx, fovY=fovy).T.cuda()
    gaussians = GaussianModel(config['training']['sh_degree'])
    model_path = model_dir / 'point_cloud' / f"iteration_{config['evaluation']['iteration']}" / 'point_cloud.ply'
    gaussians.load_ply(str(model_path))
    parameters = argparse.ArgumentParser()
    pipe = PipelineParams(parameters).extract(parameters.parse_args([]))
    background = torch.ones(3, device='cuda')

    def camera(w2c):
        world_view = torch.tensor(w2c, dtype=torch.float32, device='cuda').T
        return MiniCam(width, height, fovy, fovx, 0.01, 100, world_view, world_view @ projection)

    @torch.inference_mode()
    def predict(w2c):
        return render(camera(w2c), gaussians, pipe, background)['render'].clamp(0, 1)

    def to_image(tensor):
        pixels = (tensor.detach().cpu().permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
        return Image.fromarray(pixels)

    results = []
    test_frames = [frame for frame in metadata['frames'] if frame['split'] == 'test']
    for frame in test_frames:
        predicted = predict(np.array(frame['w2c_cv']))
        reference_image = Image.open(root / 'data/test_images' / frame['name']).convert('RGB')
        reference = torch.tensor(np.array(reference_image).copy(), device='cuda', dtype=torch.float32).permute(2,0,1) / 255
        mask_array = np.array(Image.open(root / 'data/masks' / frame['name'])) > 127
        mask = torch.tensor(mask_array, device='cuda')
        difference = (predicted - reference).square()
        mse = difference.mean()
        foreground_mse = difference[:, mask].mean()
        score = {'name': frame['name'], 'psnr': float(-10 * torch.log10(mse)),
            'ssim': float(ssim(predicted, reference)),
            'foreground_psnr': float(-10 * torch.log10(foreground_mse)),
            'foreground_fraction': float(mask_array.mean())}
        results.append(score)
        prediction_image = to_image(predicted)
        prediction_image.save(evaluation / 'test_renders' / frame['name'])
        error = (predicted - reference).abs().mean(0).detach().cpu().numpy()
        heatmap = np.stack([np.minimum(error * 4, 1), np.minimum(error * 1.5, 1), np.zeros_like(error)], -1)
        panel = Image.new('RGB', (width * 3, height + 30), 'white')
        panel.paste(reference_image, (0, 30))
        panel.paste(prediction_image, (width, 30))
        panel.paste(Image.fromarray((heatmap * 255).round().astype(np.uint8)), (width * 2, 30))
        draw = ImageDraw.Draw(panel)
        draw.text((8, 8), f"Ground truth: {frame['name']}", fill='black')
        draw.text((width + 8, 8), f"3DGS: PSNR {score['psnr']:.2f}, SSIM {score['ssim']:.4f}", fill='black')
        draw.text((width * 2 + 8, 8), 'Absolute RGB error (amplified)', fill='black')
        panel.save(evaluation / 'comparisons' / (Path(frame['name']).stem + '.jpg'), quality=95)
        print(json.dumps({'stage': 'evaluate', 'processed': len(results), 'total': len(test_frames), **score}), flush=True)

    orbit = []
    elevation = math.radians(config['evaluation']['orbit_elevation_degrees'])
    for index in range(config['evaluation']['orbit_frames']):
        azimuth = 2 * math.pi * index / config['evaluation']['orbit_frames']
        distance = metadata['camera_distance']
        center = distance * np.array([math.cos(elevation)*math.cos(azimuth), math.cos(elevation)*math.sin(azimuth), math.sin(elevation)])
        forward = -center / np.linalg.norm(center)
        right = np.cross(forward, [0.,0.,1.])
        right /= np.linalg.norm(right)
        down = np.cross(forward, right)
        c2w = np.eye(4)
        c2w[:3,:3] = np.stack([right, down, forward], 1)
        c2w[:3,3] = center
        image = to_image(predict(np.linalg.inv(c2w)))
        image.save(root / 'orbit' / f'frame_{index:03d}.png')
        orbit.append(image)
    if orbit:
        orbit[0].save(root / 'reconstruction.gif', save_all=True, append_images=orbit[1:],
            duration=config['evaluation']['gif_duration_ms'], loop=0, optimize=False, disposal=2)
    summary = {'complete': True, 'test_views': len(results), 'train_views': training_config['train_images'],
        'iteration': config['evaluation']['iteration'],
        'mean_psnr': float(np.mean([row['psnr'] for row in results])),
        'mean_ssim': float(np.mean([row['ssim'] for row in results])),
        'mean_foreground_psnr': float(np.mean([row['foreground_psnr'] for row in results])),
        'gaussians': len(gaussians.get_xyz), 'orbit_frames': len(orbit),
        'gif': 'reconstruction.gif' if orbit else None, 'model_ply': str(model_path),
        'test_camera_source': 'Blender ground-truth extrinsics in the train-center-aligned reconstruction coordinate system',
        'evaluation_scope': f'{len(results)} held-out views; neither their RGB images nor their camera poses were supplied to SfM or 3DGS training',
        'metric_definition': 'Mean per-view PSNR/SSIM on RGB in [0,1] including white background; foreground PSNR uses the ground-truth alpha>0.5 mask',
        'per_view': results,
    }
    (evaluation / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({key: value for key, value in summary.items() if key != 'per_view'}), flush=True)


if __name__ == '__main__':
    main()
