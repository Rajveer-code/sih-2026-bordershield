"""BorderShield AI -- Streamlit entry point.

Day-2 scope: one working screen proving the hard gate live -- pick a
document, run it through the real Trust Ladder pipeline (core/pipeline.py),
see the verdict and every signal that produced it. The five-screen
structure and the Attack Wall button row (docs/05-EXECUTION.md) land as
the sprint continues; this is deliberately not that yet.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import PATHS
from core.pipeline import screen_document
from core.risk import traffic_light
from core.types import Band, Severity

st.set_page_config(page_title="BorderShield AI", page_icon="\U0001f6c2", layout="wide")

_BADGE_COLOR = {"GREEN": "#1e8e3e", "AMBER": "#b8860b", "RED": "#c62828"}


def _discover_documents() -> dict[str, Path]:
    docs = {f"GENUINE  —  {p.stem}": p for p in sorted(PATHS["documents"].glob("*.png"))}
    docs.update({f"FORGED   —  {p.stem}": p for p in sorted(PATHS["forged"].glob("forged_*.png"))})
    return docs


st.title("BorderShield AI")
st.caption(
    "Prototype for PS 26188 — AI-Based Fake Identity & Document Screening. "
    "Every document below is a synthetic UTO demo specimen (permanently watermarked); "
    "no real travel document is used in this build."
)

documents = _discover_documents()
if not documents:
    st.error("No documents found. Run `python -m synth.passport` and `python -m synth.forge` first.")
    st.stop()

choice = st.selectbox("Select a document to screen", list(documents.keys()))
path = documents[choice]

col_doc, col_verdict = st.columns([1, 1.2])

with col_doc:
    st.image(str(path), caption=path.name, use_container_width=True)

with col_verdict:
    with st.spinner("Running the Trust Ladder..."):
        verdict, ctx = screen_document(path)

    light = traffic_light(verdict.band)
    color = _BADGE_COLOR[light]
    st.markdown(
        f"<div style='padding:1.2rem;border-radius:0.5rem;background:{color};"
        f"color:white;text-align:center;margin-bottom:1rem'>"
        f"<div style='font-size:2.2rem;font-weight:700'>{light}</div>"
        f"<div style='font-size:1rem'>{verdict.band.value} &middot; score {verdict.score}/100</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.subheader("Recommended action")
    st.write(verdict.action)
    if verdict.crypto_override:
        st.info("This verdict was forced by a cryptographic signature failure -- "
                "no model was consulted for this decision.")

    st.subheader("Trust Ladder evidence")
    for s in verdict.signals:
        icon = {Severity.PASS: "✅", Severity.FAIL: "❌", Severity.WEAK: "⚠️"}[s.severity]
        st.markdown(f"{icon} **{s.check}** ({s.tier.value})  \n{s.message}")

st.divider()
with st.expander("Decoded MRZ (read from pixels, not from generation metadata)"):
    st.code(f"{ctx['line1']}\n{ctx['line2']}", language=None)
    st.json(ctx["fields"].model_dump(mode="json"))
