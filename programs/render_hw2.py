"""Render a selected Objaverse object's multiview images and calibrated poses."""

import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_candidates import configure_scene, quiet_blender


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    config = json.loads(Path(args.config).read_text())
    render = config['render']
    rows = [json.loads(line) for line in Path(config['cleaned_manifest']).read_text().splitlines()]
    row = next(row for row in rows if row['uid'] == config['uid'])
    output = Path(config['output_dir']) / 'data'
    (output / 'rgba').mkdir(parents=True, exist_ok=True)
    scratch = Path('/tmp/hw2_render') / config['uid']
    scratch.mkdir(parents=True, exist_ok=True)
    local_asset = scratch / 'object.glb'
    shutil.copyfile(row['path'], local_asset)
    scene, camera, permanent = configure_scene(render)
    with quiet_blender():
        bpy.ops.import_scene.gltf(filepath=str(local_asset), import_pack_images=True)
    imported = [obj for obj in scene.objects if obj not in permanent]
    for obj in list(imported):
        if obj.type in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)
            imported.remove(obj)
    normalization = Matrix(row['normalization'])
    for obj in imported:
        if obj.parent is None:
            obj.matrix_world = normalization @ obj.matrix_world
    bpy.context.view_layer.update()
    meshes = [obj for obj in imported if obj.type == 'MESH' and not obj.hide_render]
    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    radius = max(point.length for point in corners)
    distance = radius / math.sin(camera.data.angle_x / 2) * render['camera_margin']
    resolution = render['resolution']
    focal = camera.data.lens / camera.data.sensor_width * resolution
    intrinsic = [[focal, 0, resolution / 2], [0, focal, resolution / 2], [0, 0, 1]]
    cv_from_blender = Matrix.Diagonal((1, -1, -1, 1))
    frames = []
    total = len(render['elevations_degrees']) * render['views_per_ring']
    for ring, elevation in enumerate(render['elevations_degrees']):
        for view in range(render['views_per_ring']):
            azimuth = 360 * view / render['views_per_ring'] + render.get('azimuth_offset_degrees', 0)
            az, el = math.radians(azimuth), math.radians(elevation)
            camera.location = (distance * math.cos(el) * math.cos(az), distance * math.cos(el) * math.sin(az), distance * math.sin(el))
            camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
            bpy.context.view_layer.update()
            name = f'r{ring:02d}_v{view:02d}.png'
            scene.render.filepath = str(scratch / name)
            scene.cycles.seed = config['seed'] + len(frames)
            with quiet_blender():
                bpy.ops.render.render(write_still=True)
            shutil.copyfile(scratch / name, output / 'rgba' / name)
            c2w_blender = camera.matrix_world.copy()
            c2w_cv = c2w_blender @ cv_from_blender
            frames.append({
                'name': name, 'rgba': f'rgba/{name}', 'ring': ring,
                'azimuth_degrees': azimuth, 'elevation_degrees': elevation,
                'split': 'test' if view % render['test_every'] == 0 else 'train',
                'c2w_blender': [list(line) for line in c2w_blender],
                'c2w_cv': [list(line) for line in c2w_cv],
                'w2c_cv': [list(line) for line in c2w_cv.inverted()],
            })
            progress = {'stage': 'render', 'processed': len(frames), 'total': total, 'name': name}
            progress_path = output.parent / 'render_progress.json'
            temporary = progress_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(progress) + '\n')
            temporary.replace(progress_path)
            print(json.dumps(progress), flush=True)
    metadata = {
        'uid': row['uid'], 'name': row['name'], 'source_glb': row['path'], 'source_sha256': row['sha256'],
        'normalization': row['normalization'], 'width': resolution, 'height': resolution,
        'intrinsic': intrinsic, 'camera_distance': distance, 'seed': config['seed'],
        'world_convention': 'Blender world, Z up; object centered with longest extent 2',
        'camera_convention': 'c2w_cv: X right, Y down, Z forward; c2w_blender: X right, Y up, -Z forward',
        'frames': frames,
    }
    (output / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'complete': True, 'frames': len(frames), 'train': sum(frame['split'] == 'train' for frame in frames), 'test': sum(frame['split'] == 'test' for frame in frames)}), flush=True)


if __name__ == '__main__':
    main()
