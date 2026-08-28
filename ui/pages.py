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
from core.realdoc import loader
from core.realdoc.pipeline import screen_real_document
from core.risk import traffic_light
from core.rules.engine import load_policy
from core.types import Severity
from ui import actions, screens

_LIGHT_CLASS = {"GREEN": "green", "AMBER": "amber", "RED": "red"}


def render_landing() -> None:
    """The front page: what this project is, before any live data.

    Deliberately the app's default screen. Opening straight into the
    operating console gave a first-time viewer (a judge, a reviewer) no
    way to learn the thesis before being shown a table of case IDs. This
    page is read once; every other screen is operated repeatedly.
    """
    st.markdown(screens.hero_html(), unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bsx-tier-head'>The trust ladder</div>", unsafe_allow_html=True)
        st.caption("Four tiers, evaluated in this order. A tier's authority is fixed by the "
                    "architecture, not by how confident a model happens to be.")
        st.write("")
        st.markdown(screens.tier_grid_html(), unsafe_allow_html=True)

    st.write("")
    with st.container():
        st.markdown("<div class='bsx-tier-head'>Start here</div>", unsafe_allow_html=True)
        st.caption("Six controlled attack vectors are wired to the real pipeline. Each one forges a "
                    "document, screens it end to end, and writes a hash-chained case.")
        st.write("")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Open screening command", type="primary", use_container_width=True,
                          icon=":material/dashboard:", key="landing_to_dash"):
                st.session_state.page = "dashboard"
                st.rerun()
        with c2:
            if st.button("Screen a document", use_container_width=True,
                          icon=":material/person_search:", key="landing_to_capture"):
                st.session_state.page = "capture"
                st.rerun()

    st.write("")
    with st.container():
        st.markdown("<div class='bsx-tier-head'>What this is not</div>", unsafe_allow_html=True)
        st.write("")
        st.markdown(screens.honesty_html(), unsafe_allow_html=True)


def render_dashboard() -> None:
    chain_ok, _ = ledger_module.verify_chain()
    records = ledger_module.read_all()

    st.markdown(screens.topbar_html(
        "Screening command",
        "Every case below ran through the full Trust Ladder against a real generated document. "
        "Nothing on this screen is staged.",
        eyebrow="PS 26188 · Ministry of Home Affairs · Sashastra Seema Bal",
        chain_ok=chain_ok), unsafe_allow_html=True)

    high_review = sum(1 for r in records if r.get("band") in ("HIGH", "CRITICAL"))
    critical = sum(1 for r in records if r.get("band") == "CRITICAL")
    st.markdown(screens.metric_strip_html([
        screens.metric_cell_html("Cases logged", str(len(records)), "this session"),
        screens.metric_cell_html("Requires review", str(high_review), f"{critical} critical",
                                   tone="red" if high_review else ""),
        screens.status_cell_html("System status", [(actions.pki_loaded(), "Signing PKI"),
                                                     (chain_ok, "Ledger chain")]),
    ]), unsafe_allow_html=True)

    st.write("")
    with st.container(key="attack_wall_card"):
        st.markdown(
            "<div class='bsx-tier-head'>Controlled attack simulation "
            "<span style='font-family:var(--font-mono);font-size:0.74rem;color:var(--text-3);"
            "border:1px solid var(--line);border-radius:2px;padding:0.2rem 0.5rem;letter-spacing:0.12em;'>"
            "DEMO ENVIRONMENT</span></div>", unsafe_allow_html=True)
        st.caption("Each button forges a real document, runs the full pipeline, and writes a hash-chained case. "
                    "Hover colour previews the severity that vector should produce.")
        st.write("")
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
                        st.session_state.page = "case"
                        st.rerun()

    st.write("")
    with st.container():
        st.markdown("<div class='bsx-tier-head'>Recent cases</div>", unsafe_allow_html=True)
        st.markdown("<div class='bsx-scroll-x'>" + screens.recent_cases_table_html(records) + "</div>",
                     unsafe_allow_html=True)


def render_capture() -> None:
    chain_ok, _ = ledger_module.verify_chain()
    st.markdown(screens.topbar_html(
        "New screening", "Present a document and, optionally, the face of the person carrying it.",
        eyebrow="Intake", chain_ok=chain_ok), unsafe_allow_html=True)

    # index=0 only seeds the very first render; the dashboard's mode buttons
    # (render_dashboard) set st.session_state.screening_mode_radio directly
    # before rerunning, which Streamlit adopts over `index` on every render
    # after the key already exists.
    mode = st.radio("Screening mode", ["Demo Document", "Real Document"], index=0,
                     horizontal=True, label_visibility="collapsed", key="screening_mode_radio")

    if mode == "Real Document":
        _render_real_document_capture()
        return

    st.caption(
        "This pipeline reads the UTO demo template's exact 1000×700 layout, not arbitrary real-world "
        "documents -- general document detection/OCR is out of scope for this prototype. Edit one of the "
        "Attack Wall PNGs yourself (crop a field, paste a different photo) and upload it here, or switch to "
        "Real Document above for an arbitrary upload."
    )
    col_doc, col_face = st.columns(2, gap="large")
    with col_doc:
        with st.container():
            st.markdown(screens.step_head_html(1, "Document", "active"), unsafe_allow_html=True)
            uploaded_doc = st.file_uploader("Upload an edited UTO document (PNG, 1000×700)", type=["png"])
    with col_face:
        with st.container():
            st.markdown(screens.step_head_html(
                2, "Live identity — optional",
                "active" if uploaded_doc is not None else ""), unsafe_allow_html=True)
            live_capture = st.camera_input("Live face capture (optional -- for face verification)")
            if live_capture is None:
                live_capture = st.file_uploader("...or upload a face photo instead", type=["png", "jpg", "jpeg"],
                                                  key="face_upload")

    doc_ok, face_present = uploaded_doc is not None, live_capture is not None
    st.markdown(
        "<div class='bsx-pill-row' style='border-top:1px solid var(--line);padding-top:1rem;margin-top:1.4rem;'>"
        f"<span class='bsx-status-dot'><span class='dot {'ok' if doc_ok else 'bad'}'></span>"
        f"Document: {uploaded_doc.name if doc_ok else 'none'}</span>"
        f"<span class='bsx-status-dot'><span class='dot {'ok' if face_present else 'bad'}'></span>"
        f"Live capture: {'provided' if face_present else 'none'}</span>"
        "</div>", unsafe_allow_html=True)

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
            st.session_state.page = "case"
            st.rerun()


def _render_real_document_capture() -> None:
    """Mode B: an arbitrary uploaded document, screened by
    core.realdoc.pipeline -- capability-aware, never assumes the UTO
    template. Nothing here is written to disk: uploads are decoded straight
    to in-memory arrays (same privacy stance as actions.cv2_bgr_from_upload
    for live captures) and the result lives only in st.session_state for
    this session, never appended to the demo ledger -- see PLAN_realdoc.md
    for why real, potentially personal documents are kept out of the
    hash-chained audit trail that Mode A's synthetic cases use."""
    st.caption(
        "Upload any identity document or educational record. Every check below only runs when the "
        "document actually supports it -- a marksheet with no photo will correctly show biometric "
        "comparison as NOT APPLICABLE rather than a fabricated result. PDF is rendered from its first "
        "page only (core/realdoc/loader.py); a multi-page scan needs its relevant page split out first."
    )
    col_doc, col_face = st.columns(2, gap="large")
    with col_doc:
        with st.container():
            st.markdown(screens.step_head_html(1, "Document", "active"), unsafe_allow_html=True)
            doc_file = st.file_uploader("Upload a document (PNG, JPG, JPEG, PDF)", type=["png", "jpg", "jpeg", "pdf"],
                                          key="realdoc_upload")
            manual_bbox = None
            if doc_file is not None:
                doc_bgr = loader.load_bgr(doc_file.getvalue(), filename_hint=doc_file.name)
                h, w = doc_bgr.shape[:2]
                st.image(cv2.cvtColor(doc_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
                st.caption(f"{w}×{h}px · {doc_file.type or 'unknown type'} · original preserved, not resized")
                with st.expander("Portrait detection uncertain? Manually specify the region"):
                    st.caption("Only needed if automatic detection misses the portrait or picks the wrong "
                                "region -- this changes WHERE forensics/face comparison look, it can't make "
                                "a genuinely blurry printed photo sharper.")
                    use_manual = st.checkbox("Use a manually specified region instead of auto-detection",
                                               key="realdoc_manual_toggle")
                    if use_manual:
                        mc1, mc2, mc3, mc4 = st.columns(4)
                        x0 = mc1.number_input("x0", 0, w, 0, key="realdoc_mx0")
                        y0 = mc2.number_input("y0", 0, h, 0, key="realdoc_my0")
                        x1 = mc3.number_input("x1", 0, w, w, key="realdoc_mx1")
                        y1 = mc4.number_input("y1", 0, h, h, key="realdoc_my1")
                        if x1 > x0 and y1 > y0:
                            manual_bbox = (int(x0), int(y0), int(x1), int(y1))
                            st.image(cv2.cvtColor(doc_bgr[int(y0):int(y1), int(x0):int(x1)], cv2.COLOR_BGR2RGB),
                                       caption="Preview of the manually selected region", width=200)
                        else:
                            st.warning("x1/y1 must be greater than x0/y0.")
    with col_face:
        with st.container():
            st.markdown(screens.step_head_html(
                2, "Person verification photo",
                "active" if doc_file is not None else ""), unsafe_allow_html=True)
            person_capture = st.camera_input("Live camera", key="realdoc_camera")
            if person_capture is None:
                person_capture = st.file_uploader("...or upload a face photo", type=["png", "jpg", "jpeg"],
                                                    key="realdoc_face_upload")
            person_bgr = actions.cv2_bgr_from_upload(person_capture) if person_capture is not None else None
            if person_bgr is not None:
                st.image(cv2.cvtColor(person_bgr, cv2.COLOR_BGR2RGB), use_container_width=True, width=220)

    if doc_file is None:
        return
    if st.button("Screen this document", type="primary", icon=":material/play_arrow:", key="realdoc_screen_btn"):
        with st.spinner("Running OCR, classification, forensics and biometric comparison..."):
            verdict, ctx = screen_real_document(doc_bgr, person_bgr=person_bgr, manual_portrait_bbox=manual_bbox)
        st.session_state.realdoc_verdict = verdict
        st.session_state.realdoc_ctx = ctx
        st.session_state.realdoc_doc_bgr = doc_bgr
        st.session_state.realdoc_person_bgr = person_bgr
        st.rerun()

    if "realdoc_verdict" not in st.session_state:
        return
    verdict, ctx = st.session_state.realdoc_verdict, st.session_state.realdoc_ctx
    st.write("")
    st.markdown(f"<div class='bsx-tier-head'>Result — {ctx['doc_type']}</div>"
                 f"<p style='color:var(--text-3);font-size:0.8rem;margin-top:-0.5rem;'>{ctx['doc_type_note']}</p>",
                 unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bsx-tier-head'>Document Capabilities</div>", unsafe_allow_html=True)
        st.markdown(screens.realdoc_capability_panel_html(ctx["capabilities"]), unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        with st.container():
            st.markdown("<div class='bsx-tier-head'>Verification Ladder</div>", unsafe_allow_html=True)
            st.markdown(screens.realdoc_ladder_html(verdict.steps), unsafe_allow_html=True)
        if ctx["portrait_bbox"] is not None:
            with st.container():
                title = "Biometric Comparison" + (" (manually specified region)" if ctx.get("portrait_manual") else "")
                st.markdown(f"<div class='bsx-tier-head'>{title}</div>", unsafe_allow_html=True)
                x0, y0, x1, y1 = ctx["portrait_bbox"]
                cp1, cp2 = st.columns(2)
                with cp1:
                    st.image(cv2.cvtColor(st.session_state.realdoc_doc_bgr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB),
                               caption="Document portrait", use_container_width=True)
                with cp2:
                    if st.session_state.realdoc_person_bgr is not None:
                        st.image(cv2.cvtColor(st.session_state.realdoc_person_bgr, cv2.COLOR_BGR2RGB),
                                   caption="Presented person", use_container_width=True)
                    else:
                        st.info("No person photo provided for this case.")
                face_sig = next((s for s in verdict.signals if s.check == "face_verification"), None)
                if face_sig and "similarity" in face_sig.detail:
                    st.caption(f"Similarity {face_sig.detail['similarity']:.3f} "
                                f"(threshold {face_sig.detail['threshold']:.3f}) — {face_sig.message}")
    with col_b:
        with st.container():
            st.markdown("<div class='bsx-tier-head'>OCR / Field Extraction</div>", unsafe_allow_html=True)
            if ctx["capabilities"]["OCR"]:
                st.markdown(screens.realdoc_fields_table_html(ctx["fields"]), unsafe_allow_html=True)
            else:
                st.info("No readable text detected on this document.")
        if ctx["mrz"].detected:
            with st.container():
                st.markdown("<div class='bsx-tier-head'>MRZ</div>", unsafe_allow_html=True)
                if ctx["mrz"].status == "INSUFFICIENT_QUALITY":
                    st.warning("An MRZ-shaped region was found but couldn't be read with enough confidence "
                                "to trust (scan resolution/skew) — not treated as a checksum failure.")
                else:
                    label = "VALID" if ctx["mrz"].status == "DETECTED_VALID" else "INVALID"
                    st.caption(f"DETECTED + {label}")
                    st.code(f"{ctx['mrz'].line1}\n{ctx['mrz'].line2}", language=None)
                    chips = "".join(
                        f"<span class='bsx-pill {'green' if c.ok else 'red'}' style='margin-right:0.4rem;margin-top:0.4rem;display:inline-block;'>"
                        f"{c.field.upper()}: {'OK' if c.ok else 'FAIL'}</span>" for c in ctx["mrz"].checks)
                    st.markdown(chips, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='bsx-tier-head'>Detected Evidence</div>", unsafe_allow_html=True)
        st.markdown(screens.realdoc_evidence_html(verdict.signals), unsafe_allow_html=True)

    conf_col, _ = st.columns([1, 2])
    with conf_col:
        st.markdown(screens.realdoc_confidence_dial_html(verdict.steps), unsafe_allow_html=True)

    st.markdown(screens.realdoc_verdict_card_html(verdict), unsafe_allow_html=True)


def render_case() -> None:
    """ONE case, ONE page.

    This screen replaces the previous Evidence Analysis / Risk Decision /
    Investigation trio. Those split a single case across three navigation
    destinations, so answering "what is wrong with this document" meant
    clicking between pages and holding the verdict in your head -- and, as
    reported during real-document testing, they silently showed a stale
    unrelated case when the officer was working in Real Document mode.
    A case is one object; it now reads top to bottom as one document:
    verdict, then the ladder that produced it, then the evidence behind
    each finding.
    """
    actions.ensure_active_case()
    verdict, ctx = st.session_state.last_verdict, st.session_state.last_ctx
    path, case_id = st.session_state.active_path, st.session_state.case_id
    chain_ok, _ = ledger_module.verify_chain()
    policy = load_policy()

    st.markdown(screens.topbar_html(
        "Case file", eyebrow=f"Case {case_id} · {Path(path).name}",
        case_chip=f"CASE-ID: {case_id}", chain_ok=chain_ok), unsafe_allow_html=True)

    # 1. THE VERDICT -- the answer first, before any of the evidence that
    #    produced it. An officer reads this and nothing else in the common case.
    st.markdown(screens.verdict_hero_html(verdict, policy["risk_bands"]), unsafe_allow_html=True)
    note = screens.crypto_note(verdict)
    if note:
        st.markdown(note, unsafe_allow_html=True)

    st.write("")
    col_doc, col_right = st.columns([1.15, 1], gap="large")

    # 2. THE EVIDENCE -- the document as presented, flagged.
    with col_doc:
        with st.container():
            st.markdown("<div class='bsx-tier-head'>Document as presented</div>", unsafe_allow_html=True)
            has_findings = any(s.severity == Severity.FAIL for s in verdict.signals)
            if has_findings:
                st.image(overlay(str(path), verdict), caption="Flagged regions boxed", use_container_width=True)
            else:
                st.image(str(path), caption=Path(path).name, use_container_width=True)

        portrait_checks = {"photo_region_anomaly", "manifest_match", "face_verification"}
        if any(s.severity == Severity.FAIL and s.check in portrait_checks for s in verdict.signals):
            with st.container():
                st.markdown("<div class='bsx-tier-head'>Portrait comparison</div>", unsafe_allow_html=True)
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

    # 3. THE REASONING -- which tier decided, and why.
    with col_right:
        with st.container():
            st.markdown("<div class='bsx-tier-head'>Trust ladder</div>", unsafe_allow_html=True)
            st.markdown(screens.verification_sequence_html(verdict), unsafe_allow_html=True)

        if any(s.severity == Severity.FAIL for s in verdict.signals):
            with st.container():
                st.markdown("<div class='bsx-tier-head'>Findings</div>", unsafe_allow_html=True)
                st.markdown(screens.finding_cards_html(verdict), unsafe_allow_html=True)

            with st.container():
                st.markdown("<div class='bsx-tier-head'>Score contributions</div>", unsafe_allow_html=True)
                st.markdown(screens.risk_contributions_html(verdict.signals), unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='bsx-tier-head'>Machine-readable zone</div>", unsafe_allow_html=True)
            st.code(f"{ctx['line1']}\n{ctx['line2']}", language=None)
            mrz_checks = [s for s in verdict.signals if s.check.startswith("mrz_checksum_")]
            st.markdown("".join(
                f"<span class='bsx-pill {'green' if s.severity == Severity.PASS else 'red'}' "
                f"style='margin-right:0.35rem;margin-top:0.4rem;display:inline-block;'>"
                f"{s.check[len('mrz_checksum_'):].replace('_', ' ')}</span>"
                for s in mrz_checks), unsafe_allow_html=True)

        fields = ctx["fields"]
        with st.container():
            st.markdown("<div class='bsx-tier-head'>Extracted identity</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='bsx-datalist'>"
                f"<div class='bsx-datarow'><span class='bsx-field-name'>Document no</span>"
                f"<span class='bsx-field-value'>{fields.passport_number}</span></div>"
                f"<div class='bsx-datarow'><span class='bsx-field-name'>Nationality</span>"
                f"<span class='bsx-field-value'>{fields.nationality}</span></div>"
                f"<div class='bsx-datarow'><span class='bsx-field-name'>Expiry</span>"
                f"<span class='bsx-field-value'>{fields.date_of_expiry}</span></div>"
                "</div>", unsafe_allow_html=True)


def render_audit() -> None:
    """The ledger across ALL cases -- deliberately a separate destination
    from the case file, because its subject is the audit chain itself,
    not any one screening."""
    records = ledger_module.read_all()
    ok, broken_at = ledger_module.verify_chain()

    st.markdown(screens.topbar_html(
        "Audit trail",
        "Every screening appends a hash-chained record. Editing any past record in place breaks the "
        "chain at exactly that index and the verifier names it.",
        eyebrow="Tamper-evident ledger", chain_ok=ok), unsafe_allow_html=True)

    col_left, col_right = st.columns([1.3, 1], gap="large")
    with col_left:
        with st.container():
            st.markdown("<div class='bsx-tier-head'>Chain events</div>", unsafe_allow_html=True)
            st.markdown(screens.audit_timeline_html(records, limit=12), unsafe_allow_html=True)

    with col_right:
        with st.container():
            st.markdown("<div class='bsx-tier-head'>Integrity status</div>", unsafe_allow_html=True)
            pill_cls, pill_txt = ("ok", "Audit ledger — intact") if ok else ("broken", f"Chain broken at record {broken_at}")
            st.markdown(f"<span class='bsx-chain-pill {pill_cls}'>{pill_txt}</span>", unsafe_allow_html=True)
            st.write("")
            if st.button("Re-verify chain", icon=":material/verified_user:", use_container_width=True,
                          key="verify_chain_btn"):
                st.rerun()

        with st.container():
            st.markdown("<div class='bsx-tier-head'>Demo utilities</div>", unsafe_allow_html=True)
            st.caption("Rewrite a past verdict by hand, then re-verify: the chain should name the broken record.")
            if st.button("Simulate tampering with a past case", use_container_width=True, key="tamper_btn"):
                if not actions.simulate_tamper():
                    st.warning("Screen at least one document first.")
                else:
                    st.rerun()
            if st.button("Reset ledger", use_container_width=True, key="reset_ledger_btn"):
                actions.reset_ledger()
                st.rerun()


# Back-compat: older session_state may still hold one of the three retired
# page ids. app.py maps them onto the merged screens above.
def render_evidence() -> None:
    render_case()


def render_risk() -> None:
    render_case()


def render_investigation() -> None:
    render_audit()
