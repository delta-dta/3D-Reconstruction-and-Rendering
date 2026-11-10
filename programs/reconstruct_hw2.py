"""Recover cameras and sparse points from the configured training images only."""

import argparse
import json
from pathlib import Path
import sqlite3
import time

import numpy as np
from PIL import Image, ImageDraw
import pycolmap


def align_centers(source, target):
    mean_source, mean_target = source.mean(0), target.mean(0)
    x, y = source - mean_source, target - mean_target
    u, singular, vt = np.linalg.svd(y.T @ x / len(x))
    signs = np.ones(3)
    signs[-1] = np.linalg.det(u @ vt)
    rotation = u @ np.diag(signs) @ vt
    scale = float((singular * signs).sum() / np.mean(np.sum(x * x, axis=1)))
    translation = mean_target - scale * rotation @ mean_source
    return scale, rotation, translation


def draw_matches(database, data, output, first, second):
    ids = dict(database.execute('SELECT name, image_id FROM images'))
    id1, id2 = ids[first], ids[second]
    low, high = sorted((id1, id2))
    pair_id = low * 2147483647 + high
    count, payload = database.execute('SELECT rows, data FROM two_view_geometries WHERE pair_id=?', (pair_id,)).fetchone()
    matches = np.frombuffer(payload, np.uint32).reshape(count, 2).copy()
    if id1 > id2:
        matches = matches[:, ::-1]
    points = []
    for image_id in [id1, id2]:
        rows, columns, payload = database.execute('SELECT rows, cols, data FROM keypoints WHERE image_id=?', (image_id,)).fetchone()
        points.append(np.frombuffer(payload, np.float32).reshape(rows, columns)[:, :2])
    first_image, second_image = [Image.open(data / 'images' / name).convert('RGB') for name in [first, second]]
    canvas = Image.new('RGB', (1024, 540), 'white')
    canvas.paste(first_image, (0, 28))
    canvas.paste(second_image, (512, 28))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), f'{first} - {second}: {count} geometrically verified matches', fill='black')
    rng = np.random.default_rng(20261106)
    indices = np.linspace(0, len(matches) - 1, min(80, len(matches)), dtype=int)
    for index in indices:
        a, b = matches[index]
        x1, y1 = points[0][a] + [-0.5, 27.5]
        x2, y2 = points[1][b] + [511.5, 27.5]
        color = tuple(int(value) for value in rng.integers(30, 220, 3))
        draw.line((x1, y1, x2, y2), fill=color, width=1)
        draw.ellipse((x1-2, y1-2, x1+2, y1+2), outline=color)
        draw.ellipse((x2-2, y2-2, x2+2, y2+2), outline=color)
    path = output / f'matches_{Path(first).stem}_{Path(second).stem}.jpg'
    canvas.save(path, quality=95)
    return {'first': first, 'second': second, 'verified_matches': count, 'image': str(path.relative_to(output.parent))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    root = Path(config['output_dir'])
    data, sfm = root / 'data', root / 'sfm'
    sfm.mkdir(exist_ok=True)
    (sfm / 'matches').mkdir(exist_ok=True)
    (sfm / 'raw').mkdir(exist_ok=True)
    (sfm / 'aligned_text').mkdir(exist_ok=True)
    metadata = json.loads((data / 'metadata.json').read_text())
    train = {frame['name']: frame for frame in metadata['frames'] if frame['split'] == 'train'}
    intrinsic = np.array(metadata['intrinsic'])
    camera_params = ','.join(str(value) for value in [intrinsic[0,0], intrinsic[1,1], intrinsic[0,2], intrinsic[1,2]])
    database_path = sfm / 'database.db'
    start = time.monotonic()
    reuse_raw = 'raw_reconstruction' in config['sfm']
    if reuse_raw:
        print(json.dumps({'stage': 'export_saved_reconstruction', 'source': config['sfm']['raw_reconstruction']}), flush=True)
        reconstruction = pycolmap.Reconstruction(config['sfm']['raw_reconstruction'])
    else:
        print(json.dumps({'stage': 'extract_features', 'train_images': len(train), 'test_images_used': 0}), flush=True)
        pycolmap.extract_features(
            str(database_path), str(data / 'images'),
            camera_mode=pycolmap.CameraMode.SINGLE, camera_model='PINHOLE',
            reader_options={'camera_params': camera_params, 'mask_path': str(data / 'colmap_masks')},
            extraction_options={'num_threads': config['sfm']['threads'], 'use_gpu': False,
                                'max_image_size': metadata['width'], 'sift': {'max_num_features': config['sfm']['max_num_features']}},
            device=pycolmap.Device.cpu,
        )
        print(json.dumps({'stage': 'match_and_verify'}), flush=True)
        pycolmap.match_exhaustive(
            str(database_path),
            matching_options={'num_threads': config['sfm']['threads'], 'use_gpu': False,
                              'sift': {'max_ratio': config['sfm']['matching_max_ratio'], 'cross_check': True}},
            verification_options={'ransac': {'max_error': config['sfm']['verification_max_error']}},
            device=pycolmap.Device.cpu,
        )
        print(json.dumps({'stage': 'incremental_mapping'}), flush=True)
        options = pycolmap.IncrementalPipelineOptions({
            'num_threads': config['sfm']['threads'], 'random_seed': config['seed'], 'multiple_models': False,
            'ba_refine_focal_length': False, 'ba_refine_principal_point': False, 'ba_refine_extra_params': False,
            'mapper': {'abs_pose_refine_focal_length': False, 'abs_pose_refine_extra_params': False},
        })
        maps = pycolmap.incremental_mapping(str(database_path), str(data / 'images'), str(sfm / 'raw'), options=options)
        reconstruction = maps[0]
    if config['sfm'].get('require_all_registered', True) and reconstruction.num_reg_images() != len(train):
        raise RuntimeError(f'Only {reconstruction.num_reg_images()} of {len(train)} training images registered.')
    images = sorted(reconstruction.images.values(), key=lambda image: image.name)
    source_centers = np.array([image.projection_center() for image in images])
    target_centers = np.array([np.array(train[image.name]['c2w_cv'])[:3,3] for image in images])
    scale, rotation, translation = align_centers(source_centers, target_centers)
    reconstruction.transform(pycolmap.Sim3d(scale, pycolmap.Rotation3d(rotation), translation))
    aligned = data / 'sparse' / '0'
    aligned.mkdir(parents=True, exist_ok=True)
    reconstruction.write(str(aligned))
    reconstruction.write_text(str(sfm / 'aligned_text'))
    reconstruction.export_PLY(str(sfm / 'points_aligned.ply'))
    cameras, center_errors, angle_errors = [], [], []
    for image in images:
        w2c = image.cam_from_world().matrix()
        pose = np.eye(4)
        pose[:3] = w2c
        gt = np.array(train[image.name]['w2c_cv'])
        center = image.projection_center()
        target = np.array(train[image.name]['c2w_cv'])[:3,3]
        center_error = float(np.linalg.norm(center - target))
        cosine = np.clip((np.trace(w2c[:3,:3] @ gt[:3,:3].T) - 1) / 2, -1, 1)
        angle_error = float(np.degrees(np.arccos(cosine)))
        center_errors.append(center_error)
        angle_errors.append(angle_error)
        cameras.append({'name': image.name, 'w2c_cv_estimated': pose.tolist(), 'center_aligned': center.tolist(),
                        'center_gt': target.tolist(), 'center_error': center_error, 'rotation_error_degrees': angle_error})
    (sfm / 'cameras.json').write_text(json.dumps(cameras, indent=2) + '\n')
    (sfm / 'alignment.json').write_text(json.dumps({'source': 'SfM', 'target': 'Blender normalized world', 'fit_images': len(images), 'input_images': len(train), 'test_images_used': 0,
        'scale': scale, 'rotation': rotation.tolist(), 'translation': translation.tolist()}, indent=2) + '\n')
    with sqlite3.connect(database_path) as database:
        keypoints = [row[0] for row in database.execute('SELECT rows FROM keypoints')]
        verified = [row[0] for row in database.execute('SELECT rows FROM two_view_geometries WHERE rows>0')]
        examples = [draw_matches(database, data, sfm / 'matches', first, second) for first, second in config['sfm'].get('match_pairs', [
            ('r01_v01.png', 'r01_v02.png'), ('r01_v11.png', 'r01_v14.png'),
            ('r00_v01.png', 'r01_v01.png'), ('r01_v21.png', 'r02_v21.png')])]
    summary = {'complete': True, 'train_images': len(train), 'registered_images': reconstruction.num_reg_images(),
        'test_images_used': 0, 'points3D': reconstruction.num_points3D(),
        'mean_reprojection_error_pixels': reconstruction.compute_mean_reprojection_error(),
        'median_keypoints': float(np.median(keypoints)), 'verified_pairs': len(verified),
        'median_pair_inliers': float(np.median(verified)),
        'center_rmse_object_units': float(np.sqrt(np.mean(np.square(center_errors)))),
        'median_rotation_error_degrees': float(np.median(angle_errors)),
        'max_rotation_error_degrees': max(angle_errors), 'matches': examples,
        'elapsed_seconds': None if reuse_raw else round(time.monotonic() - start, 2),
        'reused_raw_reconstruction': config['sfm'].get('raw_reconstruction'),
        'registration_policy': 'all_images_required' if config['sfm'].get('require_all_registered', True) else 'train_registered_subset',
        'initialization': 'SIFT image correspondences and COLMAP triangulated points; no GLB surface points or true extrinsics supplied to SfM',
        'alignment': 'Seven-degree-of-freedom similarity fit using training camera centers only',
    }
    (sfm / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
