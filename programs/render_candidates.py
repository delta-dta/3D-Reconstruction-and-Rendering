"""Render four fixed Blender views of every material-filtered Objaverse candidate."""

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time

import bpy
from mathutils import Matrix, Vector


@contextmanager
def quiet_blender():
    sys.stdout.flush()
    saved = os.dup(1)
    with open(os.devnull, "w") as sink:
        os.dup2(sink.fileno(), 1)
        try:
            yield
        finally:
            os.dup2(saved, 1)
            os.close(saved)


@contextmanager
def gpu_render_slot(scene, gpu_lock):
    fcntl.flock(gpu_lock.fileno(), fcntl.LOCK_EX)
    try:
        scene.render.use_persistent_data = True
        yield
    finally:
        try:
            scene.render.use_persistent_data = False
        finally:
            fcntl.flock(gpu_lock.fileno(), fcntl.LOCK_UN)


def configure_scene(config):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "CUDA"
    preferences.get_devices()
    for device in preferences.devices:
        device.use = device.type == "CUDA"
    if not any(device.use for device in preferences.devices):
        raise RuntimeError("Cycles CUDA device is required.")
    scene.cycles.samples = config["samples"]
    scene.cycles.use_denoising = config["denoising"]
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.denoising_use_gpu = True
    scene.cycles.max_bounces = 2
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 1
    scene.cycles.transmission_bounces = 1
    scene.cycles.transparent_max_bounces = 2
    scene.render.threads_mode = "FIXED"
    scene.render.threads = config["cpu_threads"]
    scene.render.use_persistent_data = True
    scene.render.use_simplify = True
    scene.cycles.texture_limit_render = config["texture_limit"]
    scene.render.resolution_x = config["resolution"]
    scene.render.resolution_y = config["resolution"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    world = bpy.data.worlds.new("HW1_world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65
    scene.world = world
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = "HW1_camera"
    camera.data.lens = 50
    camera.data.sensor_width = 36
    camera.data.clip_start = 0.01
    camera.data.clip_end = 100
    scene.camera = camera
    permanent = {camera}
    for position, energy in [((3, -4, 5), 450), ((-4, -1, 2), 300), ((0, 4, 4), 350)]:
        bpy.ops.object.light_add(type="AREA", location=position)
        lamp = bpy.context.object
        lamp.name = "HW1_light"
        lamp.data.energy = energy
        lamp.data.size = 4
        lamp.rotation_euler = (-lamp.location).to_track_quat("-Z", "Y").to_euler()
        permanent.add(lamp)
    return scene, camera, permanent


def clear_asset(permanent):
    bpy.data.batch_remove([obj for obj in bpy.data.objects if obj not in permanent])
    for collection in list(bpy.data.collections):
        if not any(obj in permanent for obj in collection.all_objects):
            bpy.data.collections.remove(collection)
    bpy.data.orphans_purge(do_recursive=True)


def render_one(row, config, scene, camera, permanent, scratch, gpu_lock):
    # Free previous texture handles before reusing packed-image datablock names.
    scene.render.use_persistent_data = False
    scene.render.use_persistent_data = True
    clear_asset(permanent)
    source = Path(row["path"])
    payload = source.read_bytes()
    if len(payload) > config["max_file_bytes"]:
        return None
    digest = hashlib.sha256(payload).hexdigest()
    local_asset = scratch / "asset.glb"
    local_asset.write_bytes(payload)
    del payload
    try:
        with quiet_blender():
            bpy.ops.import_scene.gltf(filepath=str(local_asset), import_pack_images=True)
    except RuntimeError:
        return None
    imported = [obj for obj in bpy.context.scene.objects if obj not in permanent]
    for obj in list(imported):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)
            imported.remove(obj)
    active = set(bpy.context.view_layer.objects)
    meshes = [obj for obj in imported if obj in active and obj.type == "MESH" and not obj.hide_render]
    if not meshes:
        return None
    face_count = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        face_count += len(obj.data.loop_triangles)
    if not config["min_faces"] <= face_count <= config["max_faces"]:
        return None
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = [obj.evaluated_get(depsgraph) for obj in meshes]
    corners = [obj.matrix_world @ Vector(corner) for obj in evaluated for corner in obj.bound_box]
    lower = Vector(tuple(min(point[axis] for point in corners) for axis in range(3)))
    upper = Vector(tuple(max(point[axis] for point in corners) for axis in range(3)))
    extent = upper - lower
    longest = max(extent)
    if not math.isfinite(longest) or longest <= 0:
        return None
    scale = 2 / longest
    center = (lower + upper) / 2
    normalization = Matrix.Scale(scale, 4) @ Matrix.Translation(-center)
    for obj in imported:
        if obj.parent is None:
            obj.matrix_world = normalization @ obj.matrix_world
    bpy.context.view_layer.update()
    radius = extent.length * scale / 2
    distance = radius / math.sin(camera.data.angle_x / 2) * 1.12
    output_dir = Path(config["frames_dir"]) / row["uid"]
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    with gpu_render_slot(scene, gpu_lock):
        for index, (azimuth, elevation) in enumerate(config["view_angles_degrees"]):
            azimuth, elevation = math.radians(azimuth), math.radians(elevation)
            camera.location = (
                distance * math.cos(elevation) * math.cos(azimuth),
                distance * math.cos(elevation) * math.sin(azimuth),
                distance * math.sin(elevation),
            )
            camera.rotation_euler = (-camera.location).to_track_quat("-Z", "Y").to_euler()
            local_frame = scratch / f"view_{index}.png"
            scene.render.filepath = str(local_frame)
            with quiet_blender():
                bpy.ops.render.render(write_still=True)
            destination = output_dir / f"view_{index}.png"
            image_paths.append(str(destination))
    for index, destination in enumerate(image_paths):
        shutil.copyfile(scratch / f"view_{index}.png", destination)
    return {
        **row,
        "sha256": digest,
        "rendered_faces": face_count,
        "normalization": [list(line) for line in normalization],
        "preview_images": image_paths,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--worker", type=int, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    config = json.loads(Path(args.config).read_text())
    rows = [json.loads(line) for line in Path(config["input"]).read_text().splitlines()]
    rows = rows[args.worker::config["workers"]]
    output_dir = Path(config["manifest_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    scratch = Path(config["scratch_root"]) / f"worker_{args.worker}"
    scratch.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"rendered_{args.worker}.jsonl"
    progress_path = output_dir / f"progress_{args.worker}.json"
    processed = 0
    kept = 0
    previous_elapsed = 0
    if config["resume"] and manifest_path.exists():
        with manifest_path.open("r+b") as manifest:
            payload = manifest.read()
            complete_end = payload.rfind(b"\n") + 1
            manifest.truncate(complete_end)
        complete_lines = payload[:complete_end].splitlines()
        kept = len(complete_lines)
        if complete_lines:
            last = json.loads(complete_lines[-1])
            processed = last["input_index"]
            if last["uid"] != rows[processed - 1]["uid"]:
                raise RuntimeError("Saved render manifest does not match the configured worker input.")
            if not all(Path(path).is_file() for path in last["preview_images"]):
                raise RuntimeError("Saved render images are missing; the saved run cannot be resumed.")
    if config["resume"] and progress_path.exists():
        saved = json.loads(progress_path.read_text())
        if saved["total"] != len(rows) or saved["worker"] != args.worker or saved["rendered"] > kept:
            raise RuntimeError("Saved render progress does not match the render manifest.")
        processed = max(processed, saved["processed"])
        previous_elapsed = saved["elapsed_seconds"]
    start = time.monotonic()

    def update_progress(index):
        progress = {
            "worker": args.worker, "processed": index, "total": len(rows),
            "rendered": kept,
            "elapsed_seconds": round(previous_elapsed + time.monotonic() - start, 1),
            "complete": index == len(rows),
        }
        temporary = progress_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(progress) + "\n")
        temporary.replace(progress_path)
        print(json.dumps(progress), flush=True)

    update_progress(processed)
    if processed == len(rows):
        return
    scene, camera, permanent = configure_scene(config)
    mode = "a" if config["resume"] else "w"
    slot = args.worker % config["gpu_render_slots"]
    lock_path = Path(config["scratch_root"]) / f"gpu_slot_{slot}.lock"
    with lock_path.open("a") as gpu_lock, manifest_path.open(mode, encoding="utf-8") as output:
        for index, row in enumerate(rows[processed:], processed + 1):
            try:
                result = render_one(row, config, scene, camera, permanent, scratch, gpu_lock)
            except (ValueError, OSError, KeyError, IndexError):
                result = None
            if result is not None:
                result["input_index"] = index
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
                output.flush()
                kept += 1
            if index % config["progress_every"] == 0 or index == len(rows):
                update_progress(index)
    clear_asset(permanent)


if __name__ == "__main__":
    main()
