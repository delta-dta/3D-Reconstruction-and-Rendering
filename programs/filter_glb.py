"""Filter GLB surface types and material/color availability without reading geometry buffers."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import json
import math
import os
from pathlib import Path
import struct


def select_asset(row, config):
    try:
        with open(row["path"], "rb") as source:
            actual_size = os.fstat(source.fileno()).st_size
            if actual_size > config["max_file_bytes"]:
                return None
            magic, version, declared_size = struct.unpack("<4sII", source.read(12))
            json_size, chunk_type = struct.unpack("<II", source.read(8))
            if (
                magic != b"glTF" or version != 2 or declared_size != actual_size
                or chunk_type != 0x4E4F534A or json_size > actual_size - 20
            ):
                return None
            asset = json.loads(source.read(json_size))
        if asset.get("animations"):
            return None

        triangles = transparent = reflective = color_information = 0
        textured = vertex_colored = 0
        colors = Counter()
        materials = asset.get("materials", [])
        accessors = asset["accessors"]

        for mesh in asset["meshes"]:
            for primitive in mesh["primitives"]:
                mode = primitive.get("mode", 4)
                if mode not in (4, 5, 6):
                    return None
                attributes = primitive["attributes"]
                accessor_index = primitive["indices"] if "indices" in primitive else attributes["POSITION"]
                count = accessors[accessor_index]["count"]
                face_count = count // 3 if mode == 4 else max(0, count - 2)
                triangles += face_count

                material = materials[primitive["material"]] if "material" in primitive else {}
                pbr = material.get("pbrMetallicRoughness", {})
                extensions = material.get("extensions", {})
                specular_glossiness = extensions.get("KHR_materials_pbrSpecularGlossiness")
                if specular_glossiness is not None:
                    color = specular_glossiness.get("diffuseFactor", [1, 1, 1, 1])
                    has_texture = "diffuseTexture" in specular_glossiness
                    is_reflective = (
                        "specularGlossinessTexture" not in specular_glossiness
                        and specular_glossiness.get("glossinessFactor", 1) >= config["min_reflective_glossiness"]
                        and max(specular_glossiness.get("specularFactor", [1, 1, 1])) >= config["min_reflective_specular"]
                    )
                else:
                    color = pbr.get("baseColorFactor", [1, 1, 1, 1])
                    has_texture = "baseColorTexture" in pbr
                    is_reflective = (
                        "metallicRoughnessTexture" not in pbr
                        and pbr.get("metallicFactor", 1) >= config["min_reflective_metallic"]
                        and pbr.get("roughnessFactor", 1) <= config["max_reflective_roughness"]
                    )
                is_transparent = (
                    material.get("alphaMode", "OPAQUE") == "BLEND"
                    or color[3] < config["min_opaque_alpha"]
                    or extensions.get("KHR_materials_transmission", {}).get("transmissionFactor", 0) > config["max_transmission"]
                )
                has_vertex_color = "COLOR_0" in attributes
                transparent += face_count * is_transparent
                reflective += face_count * is_reflective
                textured += face_count * has_texture
                vertex_colored += face_count * has_vertex_color
                color_information += face_count * (has_texture or has_vertex_color)
                colors[tuple(color[:3])] += face_count

        if not config["min_faces"] <= triangles <= config["max_faces"]:
            return None
        transparent_fraction = transparent / triangles
        reflective_fraction = reflective / triangles
        if (
            transparent_fraction > config["max_unsuitable_material_fraction"]
            or reflective_fraction > config["max_unsuitable_material_fraction"]
        ):
            return None
        substantial_colors = [
            color for color, count in colors.items()
            if count / triangles >= config["min_color_information_fraction"]
        ]
        multicolor = any(
            math.dist(left, right) >= config["min_color_distance"]
            for index, left in enumerate(substantial_colors)
            for right in substantial_colors[index + 1:]
        )
        if color_information / triangles < config["min_color_information_fraction"] and not multicolor:
            return None
        return {
            **row,
            "file_bytes": actual_size,
            "triangle_count": triangles,
            "mesh_count": len(asset["meshes"]),
            "image_count": len(asset.get("images", [])),
            "surface_flags": {
                "base_color_texture_fraction": round(textured / triangles, 4),
                "vertex_color_fraction": round(vertex_colored / triangles, 4),
                "color_information_fraction": round(color_information / triangles, 4),
                "has_substantial_material_color_variation": multicolor,
                "transparent_fraction": round(transparent_fraction, 4),
                "strongly_reflective_fraction": round(reflective_fraction, 4),
            },
        }
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    with open(config["input"], encoding="utf-8") as source:
        rows = [json.loads(line) for line in source]
    input_counts = Counter(row["shard"] for row in rows)
    kept_counts = Counter()
    kept = 0
    with ThreadPoolExecutor(max_workers=config["workers"]) as executor:
        results = executor.map(partial(select_asset, config=config), rows)
        with open(config["output"], "w", encoding="utf-8") as output:
            for index, result in enumerate(results, 1):
                if result is not None:
                    output.write(json.dumps(result, ensure_ascii=False) + "\n")
                    kept += 1
                    kept_counts[result["shard"]] += 1
                if index % 1000 == 0 or index == len(rows):
                    output.flush()
                    print(json.dumps({"processed": index, "total": len(rows), "kept": kept}), flush=True)
    summary = {
        "input_count": len(rows),
        "kept_count": kept,
        "removed_count": len(rows) - kept,
        "shards": [
            {"shard": shard, "input_count": input_counts[shard], "kept_count": kept_counts[shard]}
            for shard in sorted(input_counts)
        ],
    }
    Path(config["summary"]).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
