"""The 5 screens of the console, one function each. These orchestrate:
they call ui/screens.py for markup and ui/actions.py for logic, and they
freely touch st.session_state/widgets themselves -- a different, wider
contract than ui/screens.py's pure-render one. app.py just dispatches to
whichever of these the sidebar nav selected.

Real Streamlit widgets (buttons, uploaders, images) are never nested
inside raw HTML injected via a separate st.markdown call -- an unclosed
`<div>` from one st.markdown does not actually wrap a later, sibling
st.button in the rendered DOM, it only looks that way in the source. Any
box that needs a widget inside it uses st.container(border=True) instead,
which really does parent its children.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import streamlit as st
from PIL import Image

from config import DOC_SIZE, PATHS
from core.crypto import ledger as ledger_module
from core.face.pipeline import verify as face_verify
from core.fields import PORTRAIT_BBOX
from core.forensics.heatmap import overlay
from core.risk import traffic_light
from core.rules.engine import load_policy
from core.types import Severity
from ui import actions, screens

_LIGHT_CLASS = {"GREEN": "green", "AMBER": "amber", "RED": "red"}


def render_dashboard() -> None:
    chain_ok, _ = ledger_module.verify_chain()
    records = ledger_module.read_all()

    col_title, col_cta = st.columns([3, 1])
    with col_title:
        st.markdown(screens.topbar_html(
            "Border Screening Command",
            "Identity verification and document integrity monitoring.",
            chain_ok=chain_ok), unsafe_allow_html=True)
    with col_cta:
        st.write("")
        if st.button("Start New Screening", type="primary", icon=":material/play_arrow:",
                      use_container_width=True, key="dash_new_screening"):
            st.session_state.page = "capture"
            st.rerun()

    high_review = sum(1 for r in records if r.get("band") in ("HIGH", "CRITICAL"))
    critical = sum(1 for r in records if r.get("band") == "CRITICAL")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(screens.stat_card_html("Active Cases", str(len(records)), "logged this session"),
                     unsafe_allow_html=True)
    with c2:
        st.markdown(screens.stat_card_html("Requires Review", str(high_review), f"{critical} critical",
                                             tone="red" if high_review else ""), unsafe_allow_html=True)
    with c3:
        st.markdown(screens.system_status_card_html(pki_ok=actions.pki_loaded(), chain_ok=chain_ok),
                     unsafe_allow_html=True)

    st.write("")
    with st.container(border=True, key="attack_wall_card"):
        st.markdown(
            "<div style='display:flex;justify-content:space-between;align-items:center;'>"
            "<span class='bsx-tier-head' style='margin-top:0;border-bottom:none;'>Controlled Attack Simulation</span>"
            "<span style='font-family:var(--font-mono);font-size:0.62rem;color:var(--text-3);"
            "border:1px solid var(--line);border-radius:2px;padding:0.15rem 0.5rem;'>DEMO ENVIRONMENT</span>"
            "</div>", unsafe_allow_html=True)
        st.caption("Select an attack vector to run it through the full Trust Ladder pipeline and log a real case.")
        cols = st.columns(6)
        specs = [
            ("atk_genuine", "GENUINE", "verified", None, "The untouched synthetic document. Every tier should pass."),
            ("atk_dob", "CHANGE DOB", "edit_calendar", "A",
             "VIZ date of birth edited; MRZ left untouched. Caught by cross-zone consistency."),
            ("atk_photo", "REPLACE PHOTO", "add_photo_alternate", "B",
             "Portrait swapped, feathered seam. Caught by forensics AND crypto impersonation check."),
            ("atk_recapture", "SCREEN RECAPTURE", "screenshot_monitor", "C",
             "Simulated screen/print recapture. Forensics-only -- must route to AMBER, never RED."),
            ("atk_face", "FACE MISMATCH", "face_retouching_off", "FACE", None),
            ("atk_sig", "BREAK SIGNATURE", "draw", "SIG",
             "Hand-tamper an already-signed manifest. Signature fails -- CRITICAL, no model consulted."),
        ]
        for col, (key, label, icon, code, help_text) in zip(cols, specs):
            with col:
                with st.container(key=key):
                    if code == "FACE":
                        st.button(label, icon=f":material/{icon}:", use_container_width=True, disabled=True,
                                   help="Blocked: needs a SECOND, different person's real photo. One real "
                                        "identity is on file in data/portraits/ (live face MATCH already "
                                        "verified working via New Screening) -- a genuine mismatch demo needs "
                                        "someone else's photo too, not just this one person's.")
                    elif st.button(label, icon=f":material/{icon}:", use_container_width=True, help=help_text):
                        if code is None:
                            actions.run_and_log(actions.GENUINE, None)
                        elif code == "SIG":
                            actions.break_signature_attack()
                        else:
                            actions.run_and_log(actions.ATTACKS[code], code)
                        st.session_state.page = "evidence"
                        st.rerun()

    st.write("")
    with st.container(border=True):
        st.markdown(
            "<div style='display:flex;justify-content:space-between;align-items:center;'>"
            "<span class='bsx-tier-head' style='margin-top:0;border-bottom:none;'>Recent Cases</span></div>",
            unsafe_allow_html=True)
        st.markdown(screens.recent_cases_table_html(records), unsafe_allow_html=True)


def render_capture() -> None:
    chain_ok, _ = ledger_module.verify_chain()
    st.markdown(screens.topbar_html("New Screening", "Present a document and, optionally, a live face capture.",
                                     chain_ok=chain_ok), unsafe_allow_html=True)
    st.caption(
        "This pipeline reads the UTO demo template's exact 1000×700 layout, not arbitrary real-world "
        "documents -- general document detection/OCR is out of scope for this prototype. Edit one of the "
        "Attack Wall PNGs yourself (crop a field, paste a different photo) and upload it here."
    )
    col_doc, col_face = st.columns(2, gap="large")
    with col_doc:
        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Document Capture</div>", unsafe_allow_html=True)
            uploaded_doc = st.file_uploader("Upload an edited UTO document (PNG, 1000×700)", type=["png"])
    with col_face:
        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Live Identity Capture</div>", unsafe_allow_html=True)
            live_capture = st.camera_input("Live face capture (optional -- for face verification)")
            if live_capture is None:
                live_capture = st.file_uploader("...or upload a face photo instead", type=["png", "jpg", "jpeg"],
                                                  key="face_upload")

    doc_ok, face_present = uploaded_doc is not None, live_capture is not None
    st.markdown(
        "<div class='bsx-card' style='margin-top:0.8rem;'><div class='bsx-card-body' "
        "style='display:flex;gap:1.5rem;flex-wrap:wrap;'>"
        f"<span class='bsx-status-dot'><span class='dot {'ok' if doc_ok else 'bad'}'></span>"
        f"Document: {uploaded_doc.name if doc_ok else 'None'}</span>"
        f"<span class='bsx-status-dot'><span class='dot {'ok' if face_present else 'bad'}'></span>"
        f"Live capture: {'provided' if face_present else 'none'}</span>"
        "</div></div>", unsafe_allow_html=True)

    if doc_ok:
        doc_img = Image.open(uploaded_doc).convert("RGB")
        if doc_img.size != DOC_SIZE:
            st.error(f"Expected a {DOC_SIZE[0]}×{DOC_SIZE[1]} image (the UTO template's own canvas size), "
                      f"got {doc_img.size[0]}×{doc_img.size[1]}. This pipeline reads fixed pixel coordinates, "
                      f"not an arbitrary layout.")
        elif st.button("Screen this document", type="primary", icon=":material/play_arrow:"):
            custom_path = PATHS["documents"] / "_uploaded_custom.png"
            doc_img.save(custom_path)
            face_signal, live_bgr = None, None
            if face_present:
                live_bgr = actions.cv2_bgr_from_upload(live_capture)
                doc_bgr = actions.cv2_bgr_from_upload(uploaded_doc)
                face_signal = face_verify(doc_bgr, live_bgr)
            actions.run_and_log(custom_path, "CUSTOM", extra_signals=[face_signal] if face_signal else None)
            if live_bgr is not None:
                st.session_state.last_live_face_bgr = live_bgr
            st.session_state.page = "evidence"
            st.rerun()


def render_evidence() -> None:
    actions.ensure_active_case()
    verdict, ctx = st.session_state.last_verdict, st.session_state.last_ctx
    path, case_id = st.session_state.active_path, st.session_state.case_id
    chain_ok, _ = ledger_module.verify_chain()

    st.markdown(screens.topbar_html("Evidence Analysis", case_chip=f"CASE-ID: {case_id}", chain_ok=chain_ok),
                unsafe_allow_html=True)

    col_doc, col_right = st.columns([1.3, 1], gap="large")
    with col_doc:
        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Document Evidence</div>", unsafe_allow_html=True)
            has_findings = any(s.severity == Severity.FAIL for s in verdict.signals)
            if has_findings:
                st.image(overlay(str(path), verdict), caption=f"{Path(path).name} — flagged regions boxed",
                           use_container_width=True)
            else:
                st.image(str(path), caption=Path(path).name, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Verification Sequence</div>", unsafe_allow_html=True)
            st.markdown(screens.verification_sequence_html(verdict), unsafe_allow_html=True)

        st.markdown(screens.finding_cards_html(verdict), unsafe_allow_html=True)

        portrait_checks = {"photo_region_anomaly", "manifest_match", "face_verification"}
        if any(s.severity == Severity.FAIL and s.check in portrait_checks for s in verdict.signals):
            with st.container(border=True):
                st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Portrait Comparison</div>", unsafe_allow_html=True)
                cp1, cp2 = st.columns(2)
                x0, y0, x1, y1 = PORTRAIT_BBOX
                with cp1:
                    st.image(ctx["gray"][y0:y1, x0:x1], caption="Document portrait", channels="GRAY",
                               use_container_width=True)
                with cp2:
                    live = st.session_state.get("last_live_face_bgr")
                    if live is not None:
                        st.image(cv2.cvtColor(live, cv2.COLOR_BGR2RGB), caption="Live capture (this session)",
                                   use_container_width=True)
                    else:
                        st.info("No live capture on file for this case.")

        st.markdown(screens.verdict_footer_html(verdict), unsafe_allow_html=True)
        note = screens.crypto_note(verdict)
        if note:
            st.markdown(note, unsafe_allow_html=True)


def render_risk() -> None:
    actions.ensure_active_case()
    verdict, case_id = st.session_state.last_verdict, st.session_state.case_id
    chain_ok, _ = ledger_module.verify_chain()
    policy = load_policy()
    light = traffic_light(verdict.band)
    cls = _LIGHT_CLASS[light]

    st.markdown(screens.topbar_html("Risk Decision Summary", case_chip=f"CASE-ID: {case_id}", chain_ok=chain_ok),
                unsafe_allow_html=True)

    col_main, col_side = st.columns([2, 1], gap="large")
    with col_main:
        with st.container(border=True):
            c1, c2 = st.columns([1, 1.4])
            with c1:
                st.markdown(screens.risk_ring_svg(verdict.score, verdict.band), unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;margin-top:0.5rem;'>"
                             f"<span class='bsx-pill {cls}'>{verdict.band.value} RISK</span></div>",
                             unsafe_allow_html=True)
            with c2:
                override_note = (" Forced by cryptographic proof of tampering — no forensic or biometric "
                                   "model was consulted for this decision." if verdict.crypto_override else "")
                st.markdown(
                    f"<div style='font-family:var(--font-head);font-weight:700;font-size:1.35rem;"
                    f"color:var(--{cls});text-transform:uppercase;margin-bottom:0.6rem;letter-spacing:-0.01em;'>"
                    f"{verdict.action}</div>"
                    f"<p style='color:var(--text-2);'>Fused from {len(verdict.signals)} signals across the Trust "
                    f"Ladder's tiers.{override_note}</p>", unsafe_allow_html=True)
            st.markdown(screens.risk_distribution_scale_html(verdict.score, policy["risk_bands"]),
                         unsafe_allow_html=True)
    with col_side:
        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Risk Contributions</div>", unsafe_allow_html=True)
            st.markdown(screens.risk_contributions_html(verdict.signals), unsafe_allow_html=True)


def render_investigation() -> None:
    records = ledger_module.read_all()
    ok, broken_at = ledger_module.verify_chain()

    st.markdown(screens.topbar_html("Investigation", "Audit trail and case review.", chain_ok=ok),
                unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1], gap="large")
    with col_left:
        if "last_verdict" in st.session_state:
            verdict, ctx = st.session_state.last_verdict, st.session_state.last_ctx
            fields = ctx["fields"]
            with st.container(border=True):
                st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Case Summary</div>", unsafe_allow_html=True)
                cs1, cs2 = st.columns(2)
                with cs1:
                    st.markdown(
                        f"<div style='font-family:var(--font-mono);font-size:0.83rem;color:var(--text-2);'>"
                        f"Doc No: {fields.passport_number}<br>Nationality: {fields.nationality}<br>"
                        f"Expiry: {fields.date_of_expiry}</div>", unsafe_allow_html=True)
                with cs2:
                    n_fails = sum(1 for s in verdict.signals if s.severity == Severity.FAIL)
                    st.markdown(
                        f"<div style='font-size:0.85rem;color:var(--text);'>{actions.top_finding(verdict)}</div>"
                        f"<div style='font-size:0.75rem;color:var(--text-3);margin-top:0.3rem;'>"
                        f"{n_fails} finding(s) across the Trust Ladder.</div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Decoded MRZ</div>", unsafe_allow_html=True)
                st.code(f"{ctx['line1']}\n{ctx['line2']}", language=None)
                mrz_checks = [s for s in verdict.signals if s.check.startswith("mrz_checksum_")]
                chips = "".join(
                    f"<span class='bsx-pill {'green' if s.severity == Severity.PASS else 'red'}' "
                    f"style='margin-right:0.4rem;margin-top:0.4rem;display:inline-block;'>"
                    f"{s.check[len('mrz_checksum_'):].upper()}: {s.severity.value.upper()}</span>"
                    for s in mrz_checks
                )
                st.markdown(chips, unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Portrait Evidence</div>", unsafe_allow_html=True)
                pc1, pc2 = st.columns(2)
                x0, y0, x1, y1 = PORTRAIT_BBOX
                with pc1:
                    st.image(ctx["gray"][y0:y1, x0:x1], caption="Document portrait", channels="GRAY",
                               use_container_width=True)
                with pc2:
                    live = st.session_state.get("last_live_face_bgr")
                    if live is not None:
                        st.image(cv2.cvtColor(live, cv2.COLOR_BGR2RGB), caption="Live capture (this session)",
                                   use_container_width=True)
                    else:
                        st.info("No live capture on file for this case.")
        else:
            st.info("No active case yet -- run an Attack Wall scenario or a new screening first.")

    with col_right:
        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Integrity Status</div>", unsafe_allow_html=True)
            pill_cls, pill_txt = ("ok", "AUDIT LEDGER — INTACT") if ok else ("broken", f"CHAIN BROKEN AT RECORD {broken_at}")
            st.markdown(f"<span class='bsx-chain-pill {pill_cls}'>{pill_txt}</span>", unsafe_allow_html=True)
            st.write("")
            if st.button("Verify chain", icon=":material/verified_user:", use_container_width=True, key="verify_chain_btn"):
                st.rerun()

        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Audit Trail</div>", unsafe_allow_html=True)
            st.markdown(screens.audit_timeline_html(records), unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<div class='bsx-tier-head' style='margin-top:0;'>Demo Utilities</div>", unsafe_allow_html=True)
            st.caption("Demonstrate tamper-evidence: rewrite a past verdict by hand, then re-verify the chain.")
            if st.button("Simulate tampering with a past case", use_container_width=True, key="tamper_btn"):
                if not actions.simulate_tamper():
                    st.warning("Screen at least one document first.")
                else:
                    st.rerun()
            if st.button("Reset ledger (demo utility)", use_container_width=True, key="reset_ledger_btn"):
                actions.reset_ledger()
                st.rerun()
