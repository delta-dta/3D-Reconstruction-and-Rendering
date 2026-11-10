"""Create explicit view-count or ground-truth-pose controls from a baseline."""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pycolmap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    source = Path(config['source_output_dir'])
    root = Path(config['output_dir'])
    data = root / 'data'
    data.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((source / 'data/metadata.json').read_text())
    train = [frame for frame in metadata['frames'] if frame['split'] == 'train']
    selected = train[::config['experiment']['train_stride']]
    selected_names = {frame['name'] for frame in selected}
    metadata['frames'] = [frame for frame in metadata['frames'] if frame['split'] == 'test' or frame['name'] in selected_names]
    for folder in ['images', 'test_images', 'masks', 'colmap_masks']:
        (data / folder).mkdir(exist_ok=True)
    for frame in metadata['frames']:
        name = frame['name']
        folder = 'images' if frame['split'] == 'train' else 'test_images'
        os.link(source / 'data' / folder / name, data / folder / name)
        os.link(source / 'data/masks' / name, data / 'masks' / name)
        if frame['split'] == 'train':
            os.link(source / 'data/colmap_masks' / (name + '.png'), data / 'colmap_masks' / (name + '.png'))
    metadata['experiment'] = config['experiment']
    metadata['source_output_dir'] = str(source)
    # RGBA is shared for inspection; SfM and training read the split RGB folders.
    (data / 'rgba').symlink_to(source / 'data/rgba', target_is_directory=True)
    (data / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    splits = {split: [frame['name'] for frame in metadata['frames'] if frame['split'] == split] for split in ['train', 'test']}
    (data / 'splits.json').write_text(json.dumps(splits, indent=2) + '\n')
    summary = {'uid': config['uid'], 'width': metadata['width'], 'height': metadata['height'],
               'train': len(splits['train']), 'test': len(splits['test']), 'complete': True,
               'experiment': config['experiment'], 'source_output_dir': str(source)}
    (data / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    if config['experiment']['kind'] == 'gt_poses':
        reconstruction = pycolmap.Reconstruction(str(source / 'data/sparse/0'))
        frames = {frame['name']: frame for frame in selected}
        for image in reconstruction.images.values():
            pose = np.array(frames[image.name]['w2c_cv'])
            reconstruction.frames[image.frame_id].set_cam_from_world(
                image.camera_id, pycolmap.Rigid3d(pycolmap.Rotation3d(pose[:3, :3]), pose[:3, 3]))
        sparse = data / 'sparse/0'
        sparse.mkdir(parents=True)
        reconstruction.write(str(sparse))
        # The 3DGS reader converts points3D.bin to PLY; positions/colors are identical.
        original = pycolmap.Reconstruction(str(source / 'data/sparse/0'))
        assert reconstruction.num_points3D() == original.num_points3D()
        assert all(np.array_equal(point.xyz, original.points3D[pid].xyz) for pid, point in reconstruction.points3D.items())
        control = {'complete': True, 'experiment': 'ground-truth training poses', 'train_images': len(selected),
                   'test_images_used': 0, 'same_sparse_initialization': True,
                   'points3D': reconstruction.num_points3D(), 'source_output_dir': str(source)}
        (root / 'pose_control.json').write_text(json.dumps(control, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
