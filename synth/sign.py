"""Sign every generated document and attack with the demo signing
authority, writing a .sod.json sidecar next to each. Run after
synth.passport and synth.forge.

Two modes per document, matching core/crypto/manifest.py's own
distinction (see its module docstring for the full reasoning):
  - "self": sign THIS exact image, then verify against that same
    signature at inspection time. Correctly finds nothing wrong for
    attacks that alter the original capture (DOB edit, screen recapture).
  - "impersonation": no sidecar is written for the forged image at all --
    at inspection time it gets checked against its source document's
    signature instead, simulating an attacker substituting a photo on a
    presented record they claim was already issued.
"""
from __future__ import annotations

import json

from config import PATHS
from core.crypto.manifest import sign_document, write_sod
from core.crypto.pki import load_or_create_pki


def sign_all() -> None:
    csca_cert, dsc_key, dsc_cert = load_or_create_pki()

    for png_path in sorted(PATHS["documents"].glob("*.png")):
        sod = sign_document(png_path, dsc_key, dsc_cert)
        write_sod(sod, png_path.with_suffix(".sod.json"))
        print(f"[self] signed {png_path.name}")

    for meta_path in sorted(PATHS["forged"].glob("forged_*.json")):
        meta = json.loads(meta_path.read_text())
        png_path = meta_path.with_suffix(".png")
        mode = meta.get("crypto_mode", "self")
        if mode == "self":
            sod = sign_document(png_path, dsc_key, dsc_cert)
            write_sod(sod, png_path.with_suffix(".sod.json"))
            print(f"[self] signed {png_path.name}")
        else:
            print(f"[impersonation] {png_path.name} left unsigned -- "
                  f"verified at inspection time against {meta['source_doc']}.sod.json")


if __name__ == "__main__":
    sign_all()
