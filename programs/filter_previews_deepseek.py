"""Filter rendered Objaverse previews with SIFT and the DeepSeek vision API.

Only accepted assets and aggregate checkpoint/usage are persisted. A completed
request batch is committed together; interrupted uncommitted requests may need
to be repeated. No automatic retries or alternative classifier are used.
"""

import argparse
import base64
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import json
from pathlib import Path
import shutil
import signal
import time
from urllib.request import Request, urlopen

import cv2
import numpy as np
from PIL import Image


COUNT_FIELDS = ("processed", "texture_passed", "kept", "duplicates", "requests")
TOKEN_FIELDS = (
    "prompt_tokens", "prompt_cache_hit_tokens", "prompt_cache_miss_tokens",
    "completion_tokens", "total_tokens",
)
STOP_REQUESTED = False


def prepare_views(row, config, sift):
    sheet = Image.new("RGB", (512, 512), "white")
    counts, fractions = [], []
    kernel = np.ones((2 * config["foreground_erosion_pixels"] + 1,) * 2, np.uint8)
    for index, path in enumerate(row["preview_images"]):
        rgba = Image.open(path).convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)
        mask = (np.asarray(rgba)[:, :, 3] > 127).astype(np.uint8) * 255
        fractions.append(float((mask > 0).mean()))
        rgb = Image.alpha_composite(Image.new("RGBA", rgba.size, "white"), rgba).convert("RGB")
        gray = cv2.cvtColor(np.asarray(rgb), cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (0, 0), config["gaussian_sigma"])
        interior = cv2.erode(mask, kernel)
        counts.append(len(sift.detect(gray, interior)))
        sheet.paste(rgb, ((index % 2) * 256, (index // 2) * 256))
    median_sift = float(np.median(counts))
    valid = sum(value >= config["foreground_fraction_min"] for value in fractions)
    keep = valid >= config["foreground_valid_views_min"] and median_sift >= config["sift_count_min"]
    return sheet, median_sift, keep


def classify(row, config, api_key):
    encoded = base64.b64encode(Path(row["contact_image"]).read_bytes()).decode("ascii")
    body = {
        "model": config["model"],
        "thinking": config["thinking"],
        "response_format": config["response_format"],
        "max_tokens": config["max_tokens"],
        "temperature": config["temperature"],
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": config["prompt"]},
            {"type": "image_url", "image_url": {
                "url": "data:image/jpeg;base64," + encoded,
                "detail": config["image_detail"],
            }},
        ]}],
    }
    request = Request(
        config["endpoint"], data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    start = time.monotonic()
    with urlopen(request, timeout=config["timeout_seconds"]) as response:
        result = json.load(response)
    choice = result["choices"][0]
    if choice["finish_reason"] != "stop":
        raise RuntimeError(f"Incomplete DeepSeek response for {row['uid']}: {choice['finish_reason']}")
    answer = json.loads(choice["message"]["content"])
    if not isinstance(answer["caption"], str) or any(
        type(answer[field]) is not bool for field in config["required_answers"]
    ):
        raise ValueError(f"Invalid boolean/caption response for {row['uid']}")
    keep = all(answer[field] == expected for field, expected in config["required_answers"].items())
    return {"uid": row["uid"], "keep": keep}, result["usage"], result["model"], time.monotonic() - start


def stop_after_batch(signum, frame):
    global STOP_REQUESTED
    STOP_REQUESTED = True


def prepare_candidate(row, config):
    return prepare_views(row, config, cv2.SIFT_create())


def load_state(config):
    progress_path = Path(config["progress_path"])
    saved = json.loads(progress_path.read_text()) if progress_path.exists() else None
    if saved is not None and saved.get("engine") != config["engine"]:
        raise RuntimeError("The saved visual checkpoint belongs to another classifier.")
    manifest_path = Path(config["output_dir"]) / "cleaned_models.jsonl"
    accepted = []
    if manifest_path.exists():
        payload = manifest_path.read_bytes()
        complete_end = payload.rfind(b"\n") + 1
        accepted = [json.loads(line) for line in payload[:complete_end].splitlines()]
        if any(row.get("visual_engine") != config["engine"] for row in accepted):
            raise RuntimeError("The existing accepted manifest belongs to another classifier.")
        with manifest_path.open("r+b") as manifest:
            manifest.truncate(complete_end)
    workers = range(config["render_workers"])
    counts = {field: saved[field] if saved else 0 for field in COUNT_FIELDS}
    if counts["kept"] > len(accepted):
        raise RuntimeError("The accepted manifest is shorter than the saved visual checkpoint.")
    counts["kept"] = len(accepted)
    return {
        "counts": counts,
        "offsets_per_worker": saved["offsets_per_worker"] if saved else {str(worker): 0 for worker in workers},
        "consumed_per_worker": saved["consumed_per_worker"] if saved else {str(worker): 0 for worker in workers},
        "usage": Counter(saved["usage"] if saved else {field: 0 for field in TOKEN_FIELDS}),
        "models_returned": set(saved["models_returned"]) if saved else set(),
        "request_seconds": saved["request_seconds"] if saved else 0,
        "elapsed_seconds": saved["elapsed_seconds"] if saved else 0,
        "complete": saved["complete"] if saved else False,
        "accepted": accepted,
    }


def run(config):
    state = load_state(config)
    cv2.setNumThreads(1)
    output_dir = Path(config["output_dir"])
    (output_dir / "previews").mkdir(parents=True, exist_ok=True)
    progress_path = Path(config["progress_path"])
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_dir = Path(config["render_manifest_dir"])
    scratch = Path(config["request_scratch_dir"])
    scratch.mkdir(parents=True, exist_ok=True)
    workers = range(config["render_workers"])
    counts, usage = state["counts"], state["usage"]
    offsets, consumed = state["offsets_per_worker"], state["consumed_per_worker"]
    accepted_uids = {row["uid"] for row in state["accepted"]}
    hashes = {row["sha256"] for row in state["accepted"]}
    uids_path = output_dir / "cleaned_uids.txt"
    uids_path.write_text("".join(row["uid"] + "\n" for row in state["accepted"]), encoding="utf-8")
    start = time.monotonic()
    last_reported = counts["processed"]

    def update_progress(complete=False, announce=False):
        nonlocal last_reported
        cost = {
            period + "_estimate_usd": round(sum(usage[field] * rate for field, rate in rates.items()) / 1_000_000, 8)
            for period, rates in config["price_per_million_usd"].items()
        }
        snapshot = {
            "engine": config["engine"], "model_requested": config["model"],
            "model_version_at_setup": config["model_version_at_setup"],
            **counts, "complete": complete, "offsets_per_worker": offsets,
            "consumed_per_worker": consumed, "usage": dict(usage), "cost": cost,
            "usage_scope": "committed request batches",
            "models_returned": sorted(state["models_returned"]),
            "request_seconds": round(state["request_seconds"], 3),
            "elapsed_seconds": round(state["elapsed_seconds"] + time.monotonic() - start, 1),
            "max_cost_usd": config["max_cost_usd"],
        }
        temporary = progress_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(snapshot) + "\n")
        temporary.replace(progress_path)
        if announce or complete or counts["processed"] - last_reported >= config["progress_every"]:
            print(json.dumps(snapshot), flush=True)
            last_reported = counts["processed"]

    update_progress(complete=state["complete"], announce=True)
    if state["complete"]:
        return
    api_key = Path(config["secret_file"]).read_text().strip()
    if not api_key:
        raise ValueError("The API credential file is empty")
    with (output_dir / "cleaned_models.jsonl").open("a", encoding="utf-8") as manifest, \
         uids_path.open("a", encoding="utf-8") as uids, \
         ThreadPoolExecutor(max_workers=config["preprocess_workers"]) as preprocessing, \
         ThreadPoolExecutor(max_workers=config["concurrency"]) as executor:
        while not STOP_REQUESTED:
            batch = []
            candidates = []
            read_count = 0
            for worker in workers:
                path = manifest_dir / f"rendered_{worker}.jsonl"
                if not path.exists():
                    continue
                worker_key = str(worker)
                with path.open("rb") as source:
                    source.seek(offsets[worker_key])
                    while read_count < config["read_batch_size"]:
                        line = source.readline()
                        if not line.endswith(b"\n"):
                            break
                        offsets[worker_key] = source.tell()
                        row = json.loads(line)
                        consumed[worker_key] += 1
                        counts["processed"] += 1
                        read_count += 1
                        if row["uid"] in accepted_uids:
                            # A kept result may precede the last checkpoint after
                            # interruption; replay it without another paid call.
                            counts["texture_passed"] += 1
                        elif row["sha256"] in hashes:
                            counts["duplicates"] += 1
                        else:
                            candidates.append(row)
                if read_count == config["read_batch_size"]:
                    break

            prepared = preprocessing.map(partial(prepare_candidate, config=config), candidates)
            for row, (sheet, sift_count, keep) in zip(candidates, prepared):
                if keep:
                    counts["texture_passed"] += 1
                    contact = scratch / f"{row['uid']}.jpg"
                    sheet.save(contact, quality=90)
                    batch.append((row, contact, sift_count))
                sheet.close()

            if batch:
                peak = config["price_per_million_usd"]["peak"]
                spent = sum(usage[field] * rate for field, rate in peak.items()) / 1_000_000
                next_batch_max = len(batch) * (
                    config["max_prompt_tokens_per_request"] * peak["prompt_cache_miss_tokens"]
                    + config["max_tokens"] * peak["completion_tokens"]
                ) / 1_000_000
                if spent + next_batch_max > config["max_cost_usd"]:
                    raise RuntimeError(
                        f"DeepSeek budget limit ${config['max_cost_usd']:.2f} would be exceeded; "
                        "no requests were sent for this batch."
                    )
                request_rows = [
                    {"uid": row["uid"], "contact_image": str(contact)}
                    for row, contact, sift_count in batch
                ]
                # Resolve the entire batch before accepting assets or advancing
                # the checkpoint. Request failures stop this run immediately.
                results = list(executor.map(partial(classify, config=config, api_key=api_key), request_rows))
                for (row, contact, sift_count), (decision, tokens, model, latency) in zip(batch, results):
                    counts["requests"] += 1
                    state["models_returned"].add(model)
                    state["request_seconds"] += latency
                    for field in TOKEN_FIELDS:
                        usage[field] += tokens[field]
                    if not decision["keep"] or row["uid"] in accepted_uids:
                        continue
                    if row["sha256"] in hashes:
                        counts["duplicates"] += 1
                        continue
                    preview = f"previews/{row['uid']}.jpg"
                    shutil.copyfile(contact, output_dir / preview)
                    result = {key: value for key, value in row.items() if key != "preview_images"}
                    result.update({
                        "preview": preview, "sift_count": sift_count,
                        "visual_engine": config["engine"], "visual_model": model,
                    })
                    manifest.write(json.dumps(result, ensure_ascii=False) + "\n")
                    uids.write(row["uid"] + "\n")
                    accepted_uids.add(row["uid"])
                    hashes.add(row["sha256"])
                    counts["kept"] += 1
                manifest.flush()
                uids.flush()

            complete = True
            for worker in workers:
                path = manifest_dir / f"progress_{worker}.json"
                if not path.exists():
                    complete = False
                    continue
                rendered = json.loads(path.read_text())
                complete &= rendered["complete"] and consumed[str(worker)] == rendered["rendered"]
            update_progress(complete=complete)
            for row, contact, sift_count in batch:
                contact.unlink()
            if complete or STOP_REQUESTED:
                break
            if not read_count:
                time.sleep(config["poll_seconds"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, stop_after_batch)
    run(json.loads(Path(args.config).read_text()))


if __name__ == "__main__":
    main()
