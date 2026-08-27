"""Interactive/session-state glue shared by app.py (sidebar, dispatch) and
ui/pages.py (screen orchestration). Unlike ui/screens.py's pure render
functions, everything here freely touches st.session_state and the
filesystem -- that split is deliberate so the two files can be reasoned
about differently: screens.py answers "what does this look like", this
module answers "what actually happens".
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from config import PATHS
from core.crypto import ledger
from core.pipeline import screen_document
from core.types import Severity

GENUINE = PATHS["documents"] / "demo_0001.png"
ATTACKS = {
    "A": PATHS["forged"] / "forged_demo_0001_A.png",
    "B": PATHS["forged"] / "forged_demo_0001_B.png",
    "C": PATHS["forged"] / "forged_demo_0001_C.png",
}

_DOCUMENT_LABEL = {
    None: "UTO Passport — Genuine",
    "A": "UTO Passport — DOB edited",
    "B": "UTO Passport — Portrait replaced",
    "C": "UTO Passport — Screen recapture",
    "SIG": "UTO Passport — Signature tampered",
}


def cv2_bgr_from_upload(uploaded_file) -> np.ndarray:
    """A Streamlit UploadedFile/camera capture, decoded straight to a BGR
    array in memory -- never written to disk. There is no reason to
    persist a live face capture, and every reason not to: it is exactly
    the kind of biometric data the project's own privacy stance
    (docs/02-STRATEGY.md) says never to store beyond the moment it's used."""
    pil_img = Image.open(uploaded_file).convert("RGB")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def top_finding(verdict) -> str:
    fails = [s for s in verdict.signals if s.severity == Severity.FAIL]
    if not fails:
        return "No findings — genuine document"
    return max(fails, key=lambda s: s.weight).message


def ensure_active_case() -> None:
    """Evidence/Risk screens show whatever is "active" -- on cold start
    that's the genuine document, previewed but never logged (case_id
    stays the sentinel "PREVIEW"), same rule app.py always used: opening
    or refreshing a screen is not a screening event an officer performed."""
    if "last_verdict" not in st.session_state:
        verdict, ctx = screen_document(GENUINE)
        st.session_state.active_path = GENUINE
        st.session_state.active_label = None
        st.session_state.last_verdict = verdict
        st.session_state.last_ctx = ctx
        st.session_state.case_id = "PREVIEW"


def _finalize(path: Path, attack_label: str | None, verdict, ctx) -> None:
    st.session_state.pop("last_live_face_bgr", None)  # stale unless this case's own capture re-sets it
    st.session_state.active_path = path
    st.session_state.active_label = attack_label
    st.session_state.last_verdict = verdict
    st.session_state.last_ctx = ctx
    st.session_state.case_id = str(uuid.uuid4())[:8]
    ledger.append({
        "case_id": st.session_state.case_id,
        "source_image": Path(path).name,
        "document": _DOCUMENT_LABEL.get(attack_label, "UTO Passport — Custom upload"),
        "attack_label": attack_label,
        "band": verdict.band.value,
        "score": verdict.score,
        "finding": top_finding(verdict),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    })


def run_and_log(path: Path, attack_label: str | None, extra_signals: list | None = None,
                 crypto_signal=None) -> tuple:
    verdict, ctx = screen_document(path, crypto_signal=crypto_signal, extra_signals=extra_signals)
    _finalize(path, attack_label, verdict, ctx)
    return verdict, ctx


def break_signature_attack() -> tuple:
    """The flagship crypto demo: hand-tamper an already-signed manifest
    (flip one hash) on the otherwise-untouched genuine document. The
    signature no longer verifies over the mutated manifest bytes ->
    signature_valid FAILs -> core/risk.py's crypto_override forces
    CRITICAL with NO forensic or biometric model consulted for that
    decision. Same scenario as
    tests/test_crypto.py::test_hand_edited_manifest_fails_signature_check,
    wired to the Attack Wall instead of only covered by a unit test."""
    from core.crypto.manifest import sign_document, verify_document
    from core.crypto.pki import load_or_create_pki
    csca_cert, dsc_key, dsc_cert = load_or_create_pki()
    sod = sign_document(GENUINE, dsc_key, dsc_cert)
    tampered = json.loads(json.dumps(sod))
    tampered["manifest"]["portrait_sha256"] = "0" * 64
    crypto_signal = verify_document(GENUINE, tampered, csca_cert)
    return run_and_log(GENUINE, "SIG", crypto_signal=crypto_signal)


def reset_ledger() -> None:
    path_l = PATHS["results"] / "ledger.jsonl"
    path_l.unlink(missing_ok=True)
    for key in ("last_verdict", "last_ctx"):
        st.session_state.pop(key, None)
    st.session_state.active_path = GENUINE
    st.session_state.active_label = None


def simulate_tamper() -> bool:
    """Rewrites the oldest ledger record's band by hand -- demonstrates
    tamper-evidence, not tamper-prevention. Returns False if there is
    nothing logged yet to tamper with."""
    records = ledger.read_all()
    if len(records) < 1:
        return False
    path_l = PATHS["results"] / "ledger.jsonl"
    lines = path_l.read_text(encoding="utf-8").splitlines()
    record = json.loads(lines[0])
    record["band"] = "LOW"
    lines[0] = json.dumps(record, sort_keys=True)
    path_l.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def pki_loaded() -> bool:
    """File-existence check only -- deliberately does NOT call
    load_or_create_pki(), which would CREATE the keys as a side effect of
    merely checking whether they already exist."""
    pki_dir = PATHS["pki"]
    return all((pki_dir / name).exists() for name in
               ("csca_key.pem", "csca_cert.pem", "dsc_key.pem", "dsc_cert.pem"))
