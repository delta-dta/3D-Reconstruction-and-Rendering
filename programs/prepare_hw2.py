"""Composite multiview images, export foreground masks and fixed splits."""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    config = json.loads(Path(parser.parse_args().config).read_text())
    root = Path(config['output_dir'])
    data = root / 'data'
    metadata = json.loads((data / 'metadata.json').read_text())
    for folder in ['images', 'test_images', 'masks', 'colmap_masks']:
        (data / folder).mkdir(exist_ok=True)
    radius = config['sfm']['mask_erosion_pixels']
    kernel = np.ones((2 * radius + 1,) * 2, np.uint8)
    contact = Image.new('RGB', (1280, 1000), 'white')
    draw = ImageDraw.Draw(contact)
    for index, frame in enumerate(metadata['frames']):
        rgba = Image.open(data / frame['rgba']).convert('RGBA')
        rgb = Image.alpha_composite(Image.new('RGBA', rgba.size, 'white'), rgba).convert('RGB')
        folder = 'images' if frame['split'] == 'train' else 'test_images'
        rgb.save(data / folder / frame['name'])
        mask = (np.asarray(rgba)[:, :, 3] > 127).astype(np.uint8) * 255
        Image.fromarray(mask).save(data / 'masks' / frame['name'])
        if frame['split'] == 'train':
            Image.fromarray(cv2.erode(mask, kernel)).save(data / 'colmap_masks' / (frame['name'] + '.png'))
        if index % 10 == 0:
            position = index // 10
            left, top = (position % 4) * 320, (position // 4) * 330
            contact.paste(rgb.resize((300, 300), Image.Resampling.LANCZOS), (left + 10, top + 25))
            draw.text((left + 10, top + 5), f"{frame['name']} {frame['split']} elev={frame['elevation_degrees']}", fill='black')
    splits = {split: [frame['name'] for frame in metadata['frames'] if frame['split'] == split] for split in ['train', 'test']}
    (data / 'splits.json').write_text(json.dumps(splits, indent=2) + '\n')
    contact.save(root / 'dataset_overview.jpg', quality=95)
    (data / 'summary.json').write_text(json.dumps({'uid': config['uid'], 'width': metadata['width'], 'height': metadata['height'], 'train': len(splits['train']), 'test': len(splits['test']), 'complete': True}, indent=2) + '\n')
    print(json.dumps({'train': len(splits['train']), 'test': len(splits['test']), 'complete': True}), flush=True)


if __name__ == '__main__':
    main()
