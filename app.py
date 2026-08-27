"""BorderShield AI -- Streamlit console.

The Attack Wall: one click runs a document end-to-end through the real
Trust Ladder pipeline (core/pipeline.py) and writes a case to the
hash-chained ledger (core/crypto/ledger.py). Every button here maps to a
real, generated attack (synth/forge.py) -- nothing is staged or faked for
the demo.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from config import DOC_SIZE, PATHS
from core.crypto import ledger
from core.face.pipeline import verify as face_verify
from core.forensics.heatmap import overlay
from core.pipeline import screen_document
from core.types import Severity
from ui import screens
from ui.style import inject

st.set_page_config(page_title="BorderShield AI", page_icon="\U0001f6c2", layout="wide")
inject()

GENUINE = PATHS["documents"] / "demo_0001.png"
ATTACKS = {
    "A": PATHS["forged"] / "forged_demo_0001_A.png",
    "B": PATHS["forged"] / "forged_demo_0001_B.png",
    "C": PATHS["forged"] / "forged_demo_0001_C.png",
}

if not GENUINE.exists():
    st.error("No documents found. Run `python -m synth.passport`, `python -m synth.forge`, "
             "and `python -m synth.sign` first.")
    st.stop()

if "active_path" not in st.session_state:
    st.session_state.active_path = GENUINE
    st.session_state.active_label = None

st.markdown(screens.masthead(), unsafe_allow_html=True)
st.write("")


def cv2_bgr_from_upload(uploaded_file) -> np.ndarray:
    """A Streamlit UploadedFile/camera capture, decoded straight to a BGR
    array in memory -- never written to disk. There is no reason to
    persist a live face capture, and every reason not to: it is exactly
    the kind of biometric data the project's own privacy stance
    (docs/02-STRATEGY.md) says never to store beyond the moment it's used."""
    pil_img = Image.open(uploaded_file).convert("RGB")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def _run_and_log(path: Path, attack_label: str | None, extra_signals: list | None = None) -> None:
    verdict, ctx = screen_document(path, extra_signals=extra_signals)
    st.session_state.active_path = path
    st.session_state.active_label = attack_label
    st.session_state.last_verdict = verdict
    st.session_state.last_ctx = ctx
    st.session_state.case_id = str(uuid.uuid4())[:8]
    ledger.append({
        "case_id": st.session_state.case_id,
        "source_image": path.name,
        "attack_label": attack_label,
        "band": verdict.band.value,
        "score": verdict.score,
    })


# ---------------------------------------------------------------- Attack Wall
st.markdown("<div class='bsx-tier-head' style='margin-top:0'>Attack Wall &mdash; one click, full pipeline</div>",
            unsafe_allow_html=True)
cols = st.columns(5)
with cols[0]:
    if st.button("\U0001f7e2\nGENUINE", use_container_width=True,
                  help="The untouched synthetic document. Every tier should pass."):
        _run_and_log(GENUINE, None)
with cols[1]:
    if st.button("\U0001f4dd\nCHANGE DOB", use_container_width=True,
                  help="VIZ date of birth edited; MRZ left untouched. Caught by cross-zone consistency."):
        _run_and_log(ATTACKS["A"], "A")
with cols[2]:
    if st.button("\U0001f5bc️\nREPLACE PHOTO", use_container_width=True,
                  help="Portrait swapped, feathered seam. Caught by forensics AND crypto impersonation check."):
        _run_and_log(ATTACKS["B"], "B")
with cols[3]:
    if st.button("\U0001f4f7\nSCREEN RECAPTURE", use_container_width=True,
                  help="Simulated screen/print recapture: moire, glare, real JPEG re-encode. "
                       "Forensics only -- must route to AMBER, never RED."):
        _run_and_log(ATTACKS["C"], "C")
with cols[4]:
    st.button("\U0001f464\nFACE MISMATCH", use_container_width=True, disabled=True,
               help="Blocked: needs two real, consenting portrait photos in data/portraits/. "
                    "YuNet correctly detects zero faces in the procedural placeholder -- "
                    "the module is built and unit-tested (tests/test_face.py), just not "
                    "demonstrable live yet.")

st.write("")

# --------------------------------------------------------------- Main display
# Renders whatever active_path currently is -- never a hardcoded document.
# An earlier version hardcoded GENUINE here, which was correct at the time
# this ran but became a real bug once Reset needed to touch active_path
# too: two code paths each assuming they were the one place that decided
# "what's on screen" is exactly how the image and the verdict fell out of
# sync in testing (Reset cleared the cached verdict but this block re-showed
# GENUINE regardless of what active_path said). One source of truth now.
#
# Recomputing here is NOT a screening event an officer performed, so it
# must never write a ledger entry -- only an explicit Attack Wall click
# does that (_run_and_log, above). Getting this wrong would mean the audit
# trail fills with noise every time someone merely opens or refreshes the
# page, or triggers an incidental rerun.
if "last_verdict" not in st.session_state:
    _verdict, _ctx = screen_document(st.session_state.active_path)
    st.session_state.last_verdict = _verdict
    st.session_state.last_ctx = _ctx
    st.session_state.case_id = "PREVIEW"  # never logged -- see the comment above

verdict = st.session_state.last_verdict
ctx = st.session_state.last_ctx
path = st.session_state.active_path

col_doc, col_verdict = st.columns([1, 1.25], gap="large")

with col_doc:
    has_findings = any(s.severity == Severity.FAIL for s in verdict.signals)
    if has_findings:
        st.image(overlay(str(path), verdict), caption=f"{path.name} -- flagged regions boxed in red",
                  use_container_width=True)
    else:
        st.image(str(path), caption=path.name, use_container_width=True)

with col_verdict:
    st.markdown(screens.verdict_badge(verdict), unsafe_allow_html=True)
    note = screens.crypto_note(verdict)
    if note:
        st.markdown(note, unsafe_allow_html=True)
    st.markdown(f"**Recommended action:** {verdict.action}")
    st.markdown(screens.evidence_by_tier(verdict), unsafe_allow_html=True)

st.write("")
with st.expander("Case report", expanded=False):
    st.markdown(
        screens.case_report(st.session_state.case_id, path.name, verdict, st.session_state.active_label),
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------- Capture
st.markdown("<div class='bsx-tier-head' style='margin-top:0'>Capture &mdash; screen your own edit</div>",
            unsafe_allow_html=True)
st.caption(
    "This pipeline reads a fixed template (the UTO demo document's exact 1000×700 layout), not "
    "arbitrary real-world documents -- general document detection and OCR are explicitly out of scope "
    "for this prototype (see docs/06-VERIFY-QUEUE.md). Edit one of the Attack Wall PNGs yourself -- crop "
    "a field, paste a different photo, anything -- and upload it here to see how the system reacts."
)
col_up, col_face = st.columns(2, gap="large")

with col_up:
    uploaded_doc = st.file_uploader("Upload an edited UTO document (PNG, 1000×700)", type=["png"])

with col_face:
    live_capture = st.camera_input("Live face capture (optional -- for face verification)")
    if live_capture is None:
        live_capture = st.file_uploader("...or upload a face photo instead", type=["png", "jpg", "jpeg"],
                                          key="face_upload")

if uploaded_doc is not None:
    doc_img = Image.open(uploaded_doc).convert("RGB")
    if doc_img.size != DOC_SIZE:
        st.error(f"Expected a {DOC_SIZE[0]}×{DOC_SIZE[1]} image (the UTO template's own canvas size), "
                  f"got {doc_img.size[0]}×{doc_img.size[1]}. This pipeline reads fixed pixel "
                  f"coordinates, not an arbitrary layout -- see the note above.")
    elif st.button("Screen this document", type="primary"):
        custom_path = PATHS["documents"] / "_uploaded_custom.png"
        doc_img.save(custom_path)

        face_signal = None
        if live_capture is not None:
            live_bgr = cv2_bgr_from_upload(live_capture)
            doc_bgr = cv2_bgr_from_upload(uploaded_doc)
            face_signal = face_verify(doc_bgr, live_bgr)

        _run_and_log(custom_path, "CUSTOM", extra_signals=[face_signal] if face_signal else None)
        st.rerun()

st.divider()

# ------------------------------------------------------------------ Investigation
st.markdown("<div class='bsx-tier-head' style='margin-top:0'>Investigation &mdash; audit trail</div>",
            unsafe_allow_html=True)
col_ledger, col_actions = st.columns([2.2, 1], gap="large")

with col_ledger:
    records = ledger.read_all()
    st.markdown(screens.ledger_table(records), unsafe_allow_html=True)
    st.markdown(screens.chain_status(), unsafe_allow_html=True)

with col_actions:
    st.caption("Demonstrate tamper-evidence: rewrite a past verdict by hand, "
               "then re-verify the chain.")
    if st.button("Simulate tampering with a past case", use_container_width=True):
        records = ledger.read_all()
        if len(records) < 1:
            st.warning("Screen at least one document first.")
        else:
            path_l = PATHS["results"] / "ledger.jsonl"
            lines = path_l.read_text(encoding="utf-8").splitlines()
            idx = 0
            record = json.loads(lines[idx])
            record["band"] = "LOW"  # an attacker quietly clears a past CRITICAL case
            lines[idx] = json.dumps(record, sort_keys=True)
            path_l.write_text("\n".join(lines) + "\n", encoding="utf-8")
            st.rerun()

    if st.button("Reset ledger (demo utility)", use_container_width=True):
        path_l = PATHS["results"] / "ledger.jsonl"
        path_l.unlink(missing_ok=True)
        # Must reset active_path/active_label too, not just the cached
        # verdict -- found by actually clicking this in the browser: the
        # verdict fell back to GENUINE's while the displayed image stayed
        # on whatever attack was active, showing a mismatched pair.
        for key in ("last_verdict", "last_ctx"):
            st.session_state.pop(key, None)
        st.session_state.active_path = GENUINE
        st.session_state.active_label = None
        st.rerun()

st.divider()
with st.expander("Decoded MRZ (read from pixels, not from generation metadata)"):
    st.code(f"{ctx['line1']}\n{ctx['line2']}", language=None)
    st.json(ctx["fields"].model_dump(mode="json"))
