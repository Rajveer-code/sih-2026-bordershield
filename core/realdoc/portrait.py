"""Portrait/face-region discovery on arbitrary real documents.

The synthetic Mode A pipeline knows the exact portrait bbox
(core/fields.py::PORTRAIT_BBOX) because it drew the document itself. A real
document has no such registry -- this module finds the most plausible
portrait candidate by scoring every YuNet detection on the full page, or
returns None rather than guessing. core/realdoc/pipeline.py treats None as
"PORTRAIT NOT RELIABLY DETECTED" and skips biometric comparison entirely.
"""
from __future__ import annotations

import numpy as np

from core.face.pipeline import MIN_FACE_SIZE, detect_faces

MIN_CONFIDENCE = 0.75      # above YuNet's own 0.7 floor -- a document scan
                           # has more clutter than a clean live capture
MIN_SIZE_FRACTION = 0.06   # face box shorter side, as a fraction of the image's shorter side.
                           # Measured against real documents: a genuine ID
                           # portrait ran 10-23% of the page's shorter side
                           # (passport ~10%, college ID ~23%); a false
                           # positive on a marksheet -- YuNet found a small
                           # seal/stamp graphic at confidence 0.93, high
                           # enough that MIN_CONFIDENCE alone didn't catch
                           # it -- measured ~4%. 6% sits with margin between
                           # the two on real evidence, not a guess.


def find_portrait(bgr: np.ndarray) -> np.ndarray | None:
    """Best-scoring YuNet face row (bbox+landmarks+score, same 15-value
    shape as core.face.pipeline.detect_largest_face), or None if nothing on
    the page plausibly reads as a document portrait."""
    h, w = bgr.shape[:2]
    faces = detect_faces(bgr)
    if len(faces) == 0:
        return None

    short_side = min(h, w)
    # MIN_FACE_SIZE also floors the *absolute* pixel size: on a very small
    # upload, MIN_SIZE_FRACTION alone could accept a box too small for the
    # live quality gate (core.face.pipeline.quality_gate) to ever pass
    # anyway -- no point calling something a "portrait candidate" that
    # biometric comparison would immediately reject.
    min_size = max(MIN_FACE_SIZE, MIN_SIZE_FRACTION * short_side)
    best_row, best_score = None, -1.0
    for row in faces:
        x, y, fw, fh, conf = row[0], row[1], row[2], row[3], row[-1]
        if conf < MIN_CONFIDENCE or min(fw, fh) < min_size:
            continue
        # ID portraits sit in a corner/side column, not dead centre (which
        # on an ID card or marksheet is more often a seal, logo, or block of
        # body text) -- prefer larger, more confident, and off-centre faces.
        cx = x + fw / 2
        center_bias = abs(cx - w / 2) / (w / 2)
        area_frac = (fw * fh) / (w * h)
        score = conf + 0.5 * area_frac + 0.2 * center_bias
        if score > best_score:
            best_score, best_row = score, row
    return best_row


def bbox_xyxy(face_row: np.ndarray, image_shape: tuple[int, int]) -> tuple[int, int, int, int]:
    """face_row's bbox, clamped to the image bounds, as (x0, y0, x1, y1)."""
    h, w = image_shape[:2]
    x, y, fw, fh = face_row[:4].astype(int)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(w, x + fw), min(h, y + fh)
    return x0, y0, x1, y1
