"""Orchestrates one document through the Trust Ladder: MRZ read + checksum
signals, cross-zone comparison, policy rules, fusion. Cryptographic (T0)
and forensic/biometric (T2) signals are added by callers that have them
(core/crypto/manifest.py, core/forensics/*, core/face/*) -- this function
is the T1-only backbone every screening runs through first.
"""
from __future__ import annotations

import uuid
from pathlib import Path

import cv2

from core import crosszone
from core.fields import MRZ_BAND_BBOX
from core.mrz import decode_fields, mrz_signals, read_td3
from core.rules import engine as rules_engine
from core.rules.engine import load_policy
from core.risk import fuse
from core.types import Case, Verdict


def screen_document(image_path: str | Path, crypto_valid: bool | None = None,
                     extra_signals: list | None = None) -> tuple[Verdict, dict]:
    """Returns (verdict, context) where context carries the decoded MRZ
    fields and both raw lines, for the UI to display."""
    gray = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise FileNotFoundError(f"could not read image: {image_path}")

    policy = load_policy()
    line1, line2, _ = read_td3(gray, MRZ_BAND_BBOX)
    fields = decode_fields(line1, line2)

    signals = []
    signals += mrz_signals(line2, policy=policy)
    signals += crosszone.compare(gray, MRZ_BAND_BBOX, policy=policy)
    signals += rules_engine.evaluate(fields, policy=policy)
    signals += extra_signals or []

    verdict = fuse(signals, crypto_valid=crypto_valid, policy=policy)
    context = {"line1": line1, "line2": line2, "fields": fields, "gray": gray}
    return verdict, context


def make_case(image_path: str | Path, attack_label: str | None = None, **kwargs) -> Case:
    verdict, _ = screen_document(image_path, **kwargs)
    return Case(case_id=str(uuid.uuid4())[:8], source_image=str(image_path),
                attack_label=attack_label, verdict=verdict)


if __name__ == "__main__":
    import sys
    from core.risk import traffic_light

    path = sys.argv[1] if len(sys.argv) > 1 else "data/documents/demo_0001.png"
    verdict, ctx = screen_document(path)
    print(f"{path}")
    print(f"  verdict: {traffic_light(verdict.band)} ({verdict.band.value}), score={verdict.score}")
    print(f"  action:  {verdict.action}")
    for s in verdict.signals:
        mark = "PASS" if s.severity.value == "pass" else "FAIL"
        print(f"    [{mark}] {s.check:28s} {s.message}")
