"""Controlled forgery attacks against our own generated documents, each
paired with a pixel-exact ground-truth mask. Tonight ships attack A only
(DOB modification); B-E (portrait replacement, screen recapture, face
mismatch, expiry) land on day 2 per the plan -- this module is structured
so they slot in as additional entries in ATTACKS without touching A.

Every attack function has the same contract:
    (doc_png_path, doc_json_path, rng) -> (forged_image: PIL.Image, mask: np.ndarray uint8, meta: dict)
mask is the same H x W as the document, 255 inside the tampered region, 0
elsewhere -- the ground truth that core/forensics/*.py will be scored
against on day 2.
"""
from __future__ import annotations

import datetime as dt
import json
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config import FONTS, PATHS
from core.fields import VIZ_CELL_H, VIZ_CELL_W, VIZ_LAYOUT
from core.textgrid import draw_char_grid


def _blank_mask(size: tuple[int, int]) -> np.ndarray:
    w, h = size
    return np.zeros((h, w), dtype=np.uint8)


def _fill_mask_bbox(mask: np.ndarray, bbox_xyxy: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = bbox_xyxy
    mask[y0:y1, x0:x1] = 255


def attack_dob_modification(doc_png_path: Path, doc_json_path: Path, rng: random.Random
                             ) -> tuple[Image.Image, np.ndarray, dict]:
    """Repaint the VIZ date-of-birth field with a different date. The MRZ
    is left byte-for-byte untouched, so the forged document's own two
    sources of truth -- the printed field and the machine-readable zone --
    now disagree. That disagreement is the whole attack: a forger fixing
    the field a human reads and forgetting the one a machine reads is, per
    the commercial-vendor literature cited in docs/01-RESEARCH.md, the
    single most common real forgery pattern.
    """
    img = Image.open(doc_png_path).convert("RGB")
    truth = json.loads(doc_json_path.read_text())

    bbox = tuple(truth["bboxes"]["date_of_birth"])  # x0, y0, x1, y1
    original_dob = truth["raw_dates"]["date_of_birth"]
    orig_date = dt.date.fromisoformat(original_dob)

    # a different, still-plausible date -- shift the year so it reads
    # naturally rather than looking like random noise in a screenshot
    new_date = orig_date.replace(year=orig_date.year - rng.randint(1, 8))
    new_text = new_date.strftime("%d %b %Y")

    forged = img.copy()
    draw = ImageDraw.Draw(forged)

    # Erase the old text with a solid fill sampled from this SAME bbox's
    # own clean margin (its top few pixels sit above the glyph ink, so
    # they are always background regardless of which field this is or
    # what any neighbouring row contains -- copying a patch from another
    # row was tried first and is wrong: every row has real printed text,
    # so it drags that row's characters into the target field instead of
    # erasing anything). A flat fill instead of the page's true wavy
    # guilloche texture is a visible seam under close inspection -- left
    # deliberately, since a flat retouched patch is itself a realistic
    # forensic tell (see core/forensics/noise.py, day 2), not a flaw to
    # hide.
    x0, y0, x1, y1 = bbox
    bg_strip = np.asarray(img.crop((x0, y0, x1, y0 + 3)))
    bg_color = tuple(int(c) for c in bg_strip.reshape(-1, 3).mean(axis=0))
    draw.rectangle(bbox, fill=bg_color)

    value_font = ImageFont.truetype(FONTS["mono_bold"], 19)
    layout = VIZ_LAYOUT["date_of_birth"]
    draw_char_grid(draw, new_text, x0, y0, VIZ_CELL_W, VIZ_CELL_H, layout["n_cols"],
                    value_font, fill=(20, 24, 34))

    mask = _blank_mask(img.size)
    _fill_mask_bbox(mask, bbox)

    meta = {
        "attack": "A",
        "name": "dob_modification",
        "field": "date_of_birth",
        "original_value": original_dob,
        "forged_value": new_date.isoformat(),
        "bbox": list(bbox),
        "mrz_untouched": True,
        "expected_detection_tier": "rules (cross-zone consistency)",
    }
    return forged, mask, meta


ATTACKS = {
    "A": attack_dob_modification,
}


def apply_attack(attack_id: str, doc_id: str, seed: int | None = None) -> tuple[Path, Path, Path]:
    rng = random.Random(seed)
    fn = ATTACKS[attack_id]
    png_path = PATHS["documents"] / f"{doc_id}.png"
    json_path = PATHS["documents"] / f"{doc_id}.json"
    forged_img, mask, meta = fn(png_path, json_path, rng)

    out_dir = PATHS["forged"]
    out_dir.mkdir(parents=True, exist_ok=True)
    forged_path = out_dir / f"forged_{doc_id}_{attack_id}.png"
    mask_path = out_dir / f"mask_{doc_id}_{attack_id}.png"
    meta_path = out_dir / f"forged_{doc_id}_{attack_id}.json"

    forged_img.save(forged_path)
    Image.fromarray(mask).save(mask_path)
    meta["source_doc"] = doc_id
    meta_path.write_text(json.dumps(meta, indent=2))
    return forged_path, mask_path, meta_path


if __name__ == "__main__":
    forged, mask, meta = apply_attack("A", "demo_0001", seed=1)
    print(f"wrote {forged}")
    print(f"wrote {mask}")
    print(f"wrote {meta}")
