"""BorderShield AI -- Streamlit console entry point.

Five screens (Command Dashboard, New Screening, Evidence Analysis, Risk
Decision, Investigation), navigated via a fixed sidebar, matching the
Stitch reference design (reference/stitch_bordershield_ai_interface_design/).
Every screen's logic lives in ui/pages.py; this file only wires page
config, session state, and the sidebar nav that switches between them.

Every Attack Wall button (ui/pages.py::render_dashboard) maps to a real,
generated attack (synth/forge.py) run through the actual Trust Ladder
pipeline (core/pipeline.py) -- nothing is staged or faked for the demo.
"""
from __future__ import annotations

import streamlit as st

from ui import actions, pages, screens
from ui.style import inject

st.set_page_config(page_title="BorderShield AI", page_icon="\U0001f6e1️", layout="wide")
inject()

if not actions.GENUINE.exists():
    st.error("No documents found. Run `python -m synth.passport`, `python -m synth.forge`, "
             "and `python -m synth.sign` first.")
    st.stop()

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

_NAV_ITEMS = [
    ("dashboard", "Command Dashboard", "dashboard"),
    ("capture", "New Screening", "person_search"),
    ("evidence", "Evidence Analysis", "assignment_ind"),
    ("risk", "Risk Decision", "assessment"),
    ("investigation", "Investigation", "qr_code_2"),
]

with st.sidebar:
    st.markdown(screens.sidebar_brand_html(), unsafe_allow_html=True)
    if st.button("New Entry Scan", icon=":material/add:", use_container_width=True, key="nav_new_entry"):
        st.session_state.page = "capture"
        st.rerun()
    st.write("")
    for page_id, label, icon in _NAV_ITEMS:
        with st.container(key=f"navbtn_{page_id}"):
            if st.button(label, icon=f":material/{icon}:", use_container_width=True, key=f"navbtn_btn_{page_id}"):
                st.session_state.page = page_id
                st.rerun()

# Highlights whichever nav item is active this rerun. Scoped to a stable,
# self-assigned container key (st.container(key=...)) rather than any of
# Streamlit's own internal button/testid attributes -- those are a version
# implementation detail and have already renamed across releases.
st.markdown(
    f"<style>.st-key-navbtn_{st.session_state.page} button {{ background:var(--secondary-container) !important; "
    f"color:var(--on-secondary-container) !important; font-weight:600 !important; }}</style>",
    unsafe_allow_html=True,
)

_PAGES = {
    "dashboard": pages.render_dashboard,
    "capture": pages.render_capture,
    "evidence": pages.render_evidence,
    "risk": pages.render_risk,
    "investigation": pages.render_investigation,
}
_PAGES.get(st.session_state.page, pages.render_dashboard)()
