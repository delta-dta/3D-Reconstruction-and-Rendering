"""Select static Objaverse assets in the agreed face-count and size range."""

import argparse
import gzip
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    root = Path(config["dataset_root"])
    candidates_path = Path(config["coarse_candidates"])
    candidates_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {"input_count": 0, "kept_count": 0, "shards": []}

    with candidates_path.open("w", encoding="utf-8") as output:
        for shard in config["shards"]:
            with gzip.open(root / "metadata" / f"{shard}.json.gz", "rt") as source:
                records = json.load(source)
            kept = 0
            for uid in sorted(records):
                record = records[uid]
                glb = record["archives"]["glb"]
                if not (
                    record["animationCount"] == 0
                    and config["min_faces"] <= glb["faceCount"] <= config["max_faces"]
                    and glb["size"] <= config["max_file_bytes"]
                ):
                    continue
                selected = {
                    "uid": uid,
                    "shard": shard,
                    "path": str(root / "glbs" / shard / f"{uid}.glb"),
                    "name": record["name"],
                    "tags": [tag["name"] for tag in record["tags"]],
                    "categories": [category["name"] for category in record["categories"]],
                    "metadata_faces": glb["faceCount"],
                    "metadata_size": glb["size"],
                    "license": record["license"],
                }
                output.write(json.dumps(selected, ensure_ascii=False) + "\n")
                kept += 1
            counts = {"shard": shard, "input_count": len(records), "kept_count": kept}
            summary["shards"].append(counts)
            summary["input_count"] += len(records)
            summary["kept_count"] += kept
            print(json.dumps(counts), flush=True)

    summary["removed_count"] = summary["input_count"] - summary["kept_count"]
    summary["criteria"] = {
        "animation_count": 0,
        "min_faces": config["min_faces"],
        "max_faces": config["max_faces"],
        "max_file_bytes": config["max_file_bytes"],
    }
    Path(config["coarse_summary"]).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in summary.items() if key != "shards"}), flush=True)


if __name__ == "__main__":
    main()
