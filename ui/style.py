"""One CSS injection, applied once at app startup. Aesthetic direction:
Institutional Tech -- government-grade authority + high-performance
computation, matched to the Stitch reference design
(reference/stitch_bordershield_ai_interface_design/, DESIGN.md). Dark,
high-density, tonal-layering-not-shadows, sharp 2-4px radii. IBM Plex Sans
for headlines, Inter for body/labels, JetBrains Mono for every technical
readout (MRZ, hashes, case IDs, scores) -- the same convention the
reference's own DESIGN.md specifies.

Semantic colour (GREEN/AMBER/RED) stays strictly tied to verdict severity
via core.risk.traffic_light -- never doubled as decoration. Note this
project's OWN mapping (LOW=GREEN, MEDIUM/HIGH=AMBER, CRITICAL=RED) differs
from the reference mockup's ad-hoc styling, which paints some HIGH rows
red/"BLOCKED": core/risk.py deliberately caps forensic/biometric-only
findings at HIGH so they can never look like an accusation. The colours
here follow risk.py, not the mockup's illustrative rows.
"""

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap">

<style>
:root{
  --bg:#0b141c;
  --surface-lowest:#060f16;
  --surface-low:#141c24;
  --surface:#182028;
  --surface-high:#222b33;
  --surface-highest:#2d363e;
  --outline:#909094;
  --line:#45474a;
  --line-soft:#2d363e;
  --text:#dae3ee;
  --text-2:#c6c6ca;
  --text-3:#7a8390;
  --primary:#c7c6c9;
  --on-primary:#1b1c1e;
  --secondary-container:#42474f;
  --on-secondary-container:#b1b5bf;
  --green:#22c55e;   --green-dim:#15803d; --green-bg:rgba(34,197,94,.10);
  --amber:#f59e0b;   --amber-dim:#b45309; --amber-bg:rgba(245,158,11,.10);
  --red:#ef4444;     --red-dim:#b91c1c;   --red-bg:rgba(239,68,68,.10);
  --error:#ffb4ab;   --error-container:#93000a;
  --radius-sm:2px;
  --radius:4px;
  --radius-lg:8px;
  --font-head:'IBM Plex Sans', system-ui, sans-serif;
  --font-body:'Inter', system-ui, sans-serif;
  --font-mono:'JetBrains Mono', ui-monospace, monospace;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 12px 32px -18px rgba(0,0,0,.9);
}

/* ---- kill default Streamlit chrome ---- */
#MainMenu, footer, header[data-testid="stHeader"] {visibility:hidden; height:0;}
.stDeployButton {display:none;}
div[data-testid="stDecoration"] {display:none;}
div[data-testid="stToolbar"] {display:none;}
.block-container {padding-top:1.5rem !important; padding-bottom:2rem !important; max-width:100% !important;}

/* ---- base ---- */
html, body, [class*="css"] { font-family: var(--font-body); }
.stApp { background: var(--bg); color: var(--text); }
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font-head) !important;
  letter-spacing: -0.01em;
  color: var(--text) !important;
}
p, span, div, label { color: var(--text); }
code, .stCode, .stJson, pre { font-family: var(--font-mono) !important; }
[data-testid="stCaptionContainer"] { color: var(--text-3) !important; }
[data-testid="stExpander"] { border-color: var(--line) !important; background: var(--surface-low); border-radius: var(--radius-lg); }
hr { border-color: var(--line-soft) !important; }

/* ---- sidebar: fixed 240px, matches DESIGN.md spacing.sidebar-width ---- */
section[data-testid="stSidebar"] {
  width: 240px !important; min-width: 240px !important; max-width: 240px !important;
  background: var(--surface-lowest);
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div { width: 240px; padding-top: 1rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.3rem; }
.bsx-sidebar-brand { padding: 0 0.5rem 1.1rem 0.5rem; border-bottom: 1px solid var(--line); margin-bottom: 0.8rem; }
.bsx-sidebar-brand .name { font-family: var(--font-head); font-weight: 700; font-size: 1.05rem; color: var(--text); letter-spacing: 0.01em; }
.bsx-sidebar-brand .sub { font-family: var(--font-body); font-size: 0.7rem; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.15rem; }

section[data-testid="stSidebar"] .stButton > button {
  width: 100%; display: flex !important; justify-content: flex-start !important; text-align: left;
  background: transparent; border: 1px solid transparent; color: var(--text-2);
  font-family: var(--font-mono); font-size: 0.83rem; font-weight: 400;
  padding: 0.5rem 0.65rem; border-radius: var(--radius); min-height: 0;
}
section[data-testid="stSidebar"] .stButton > button p { font-family: inherit !important; font-size: inherit !important; text-align: left; }
section[data-testid="stSidebar"] .stButton > button:hover { background: var(--surface-high); color: var(--text); border-color: transparent; }
section[data-testid="stSidebar"] .stButton > button:focus:not(:active) { border-color: var(--line); }
.bsx-nav-footer { border-top: 1px solid var(--line); margin-top: 0.6rem; padding-top: 0.5rem; }

/* per-instance active-nav / CTA overrides are injected inline per rerun -- see ui/pages.py */

/* ---- top bar ---- */
.bsx-topbar { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem;
  border-bottom: 1px solid var(--line); padding-bottom: 0.9rem; margin-bottom: 1.1rem; flex-wrap: wrap; }
.bsx-topbar .title { font-family: var(--font-head); font-weight: 600; font-size: 1.5rem; color: var(--text); letter-spacing: -0.01em; }
.bsx-topbar .sub { font-family: var(--font-body); font-size: 0.85rem; color: var(--text-3); margin-top: 0.2rem; }
.bsx-topbar .case-chip { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-2);
  border: 1px solid var(--line); border-radius: var(--radius); padding: 0.2rem 0.55rem; margin-right: 0.5rem; }
.bsx-topbar .meta { display:flex; align-items:center; gap:0.6rem; }
.bsx-chain-pill { font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
  border-radius: var(--radius-sm); padding: 0.2rem 0.5rem; border: 1px solid; }
.bsx-chain-pill.ok { color: var(--green); border-color: var(--green-dim); background: var(--green-bg); }
.bsx-chain-pill.broken { color: var(--red); border-color: var(--red-dim); background: var(--red-bg); }

/* ---- generic card ---- */
.bsx-card { background: var(--surface-low); border: 1px solid var(--line); border-radius: var(--radius-lg); }
.bsx-card-head { padding: 0.6rem 1rem; border-bottom: 1px solid var(--line); background: var(--surface);
  font-family: var(--font-head); font-size: 0.78rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--text-2); display:flex; justify-content:space-between; align-items:center; }
.bsx-card-body { padding: 1rem; }

/* ---- stat cards (dashboard) ---- */
.bsx-stat { background: var(--surface-low); border: 1px solid var(--line); border-radius: var(--radius-lg);
  padding: 0.9rem 1rem; height: 100%; }
.bsx-stat .label { font-family: var(--font-body); font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--text-3); }
.bsx-stat .value { font-family: var(--font-mono); font-size: 1.9rem; color: var(--text); line-height: 1; margin-top: 0.5rem; }
.bsx-stat .value.tone-red { color: var(--red); }
.bsx-stat .sub { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-3); text-transform: uppercase; margin-left: 0.4rem; }
.bsx-pill-row { display:flex; gap:0.4rem; flex-wrap:wrap; margin-top:0.5rem; }
.bsx-status-dot { display:inline-flex; align-items:center; gap:0.4rem; font-family: var(--font-mono); font-size: 0.68rem;
  text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-2); background: var(--surface-highest);
  border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 0.2rem 0.5rem; }
.bsx-status-dot .dot { width: 6px; height: 6px; border-radius: 50%; }
.bsx-status-dot .dot.ok { background: var(--green); }
.bsx-status-dot .dot.bad { background: var(--red); }

/* ---- attack wall ---- */
.st-key-atk_dob button, .st-key-atk_photo button, .st-key-atk_sig button { transition: color .15s, border-color .15s; }
.st-key-atk_dob button:hover, .st-key-atk_photo button:hover, .st-key-atk_sig button:hover { color: var(--amber) !important; border-color: var(--amber-dim) !important; }
.st-key-atk_recapture button, .st-key-atk_face button { transition: color .15s, border-color .15s; }
.st-key-atk_recapture button:hover, .st-key-atk_face button:hover { color: var(--red) !important; border-color: var(--red-dim) !important; }

/* ---- attack wall + generic buttons ---- */
div[data-testid="column"] .stButton > button, .bsx-card-body .stButton > button {
  width: 100%; background: var(--surface) !important; color: var(--text-2) !important;
  border: 1px solid var(--line) !important; border-radius: var(--radius) !important;
  font-family: var(--font-mono) !important; font-weight: 500 !important; font-size: 0.78rem !important;
  letter-spacing: 0.03em; text-transform: uppercase; padding: 0.6rem 0.5rem !important;
  transition: border-color 0.15s ease, background 0.15s ease; box-shadow: none;
}
div[data-testid="column"] .stButton > button:hover, .bsx-card-body .stButton > button:hover {
  border-color: var(--outline) !important; background: var(--surface-high) !important;
}
div[data-testid="column"] .stButton > button p, .bsx-card-body .stButton > button p { font-family: inherit !important; font-weight: inherit !important; }
button[kind="primary"] {
  background: var(--primary) !important; color: var(--on-primary) !important; border: 1px solid var(--primary) !important;
}
button[kind="primary"]:hover { filter: brightness(1.08); }

/* ---- verdict badge ---- */
.bsx-badge {
  border-radius: var(--radius-lg);
  padding: 1.4rem 1.2rem;
  text-align: center;
  margin-bottom: 1rem;
  border: 1px solid;
  animation: bsx-fade-in 0.3s ease;
}
.bsx-badge .light {
  font-family: var(--font-head);
  font-size: 2.4rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  line-height: 1.1;
}
.bsx-badge .meta {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  margin-top: 0.3rem;
  opacity: 0.85;
}
.bsx-badge.green { background: var(--green-bg); border-color: var(--green-dim); color: var(--green); }
.bsx-badge.amber { background: var(--amber-bg); border-color: var(--amber-dim); color: var(--amber); }
.bsx-badge.red   { background: var(--red-bg);   border-color: var(--red-dim);   color: var(--red); }

@keyframes bsx-fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ---- crypto-override callout ---- */
.bsx-crypto-note {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 0.85rem 1rem;
  font-size: 0.9rem;
  color: var(--text);
  margin-bottom: 1rem;
}
.bsx-crypto-note b { color: var(--primary); }

/* ---- tier sections ---- */
.bsx-tier-head {
  font-family: var(--font-body);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-3);
  margin: 1.1rem 0 0.4rem 0;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--line-soft);
}
.bsx-signal {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.45rem 0.6rem;
  border-radius: var(--radius);
  border-left: 3px solid transparent;
  margin-bottom: 0.2rem;
  font-size: 0.9rem;
}
.bsx-signal.pass { border-left-color: var(--green); }
.bsx-signal.fail { border-left-color: var(--red); background: var(--red-bg); }
.bsx-signal.weak { border-left-color: var(--text-3); opacity: 0.75; }
.bsx-signal .check {
  font-family: var(--font-mono);
  font-weight: 600;
  font-size: 0.82rem;
  color: var(--text);
}
.bsx-signal .msg { color: var(--text-2); }

/* ---- verification sequence (evidence screen) ---- */
.bsx-vseq { position: relative; }
.bsx-vseq-row { display:flex; align-items:center; gap:0.7rem; padding: 0.45rem 0; position:relative; }
.bsx-vseq-dot { width:22px; height:22px; border-radius:50%; border:1px solid; display:flex; align-items:center; justify-content:center;
  font-family: var(--font-mono); font-size:0.7rem; flex-shrink:0; }
.bsx-vseq-dot.pass { color: var(--text-2); border-color: var(--line); background: var(--surface-highest); }
.bsx-vseq-dot.fail { color: var(--red); border-color: var(--red-dim); background: var(--red-bg); }
.bsx-vseq-dot.na { color: var(--text-3); border-color: var(--line-soft); background: transparent; }
.bsx-vseq-label { flex:1; display:flex; justify-content:space-between; align-items:center; font-family: var(--font-body); font-size: 0.9rem; }
.bsx-vseq-label .status { font-family: var(--font-mono); font-size: 0.72rem; text-transform:uppercase; }
.bsx-vseq-row.fail .bsx-vseq-label { color: var(--red); font-weight:600; }
.bsx-vseq-row.na .bsx-vseq-label { color: var(--text-3); }

/* ---- finding cards (evidence screen) ---- */
.bsx-finding { border: 1px solid var(--red-dim); background: var(--surface-low); border-radius: var(--radius-lg);
  overflow: hidden; margin-bottom: 0.8rem; position: relative; }
.bsx-finding::before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background: var(--red); }
.bsx-finding-head { padding: 0.6rem 0.9rem 0.6rem 1.1rem; background: var(--red-bg); border-bottom: 1px solid var(--line);
  font-family: var(--font-body); font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--red); }
.bsx-finding-body { padding: 0.85rem 1rem 0.85rem 1.2rem; }
.bsx-finding-body p { color: var(--text-2); font-size: 0.83rem; margin: 0 0 0.6rem 0; }
.bsx-compare-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-family: var(--font-mono); font-size: 0.78rem; }
.bsx-compare-cell { border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 0.45rem 0.6rem; background: var(--surface); }
.bsx-compare-cell.bad { border-color: var(--red-dim); background: var(--red-bg); color: var(--red); }
.bsx-compare-cell .k { font-size: 0.65rem; color: var(--text-3); margin-bottom: 0.2rem; }

/* ---- risk ring + distribution scale ---- */
.bsx-ring-wrap { display:flex; flex-direction:column; align-items:center; gap:0.9rem; }
.bsx-ring { position:relative; width:180px; height:180px; }
.bsx-ring svg { width:100%; height:100%; transform: rotate(-90deg); }
.bsx-ring-score { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
.bsx-ring-score .n { font-family: var(--font-mono); font-size: 2.6rem; font-weight:700; color: var(--text); line-height:1; }
.bsx-ring-score .d { font-family: var(--font-body); font-size: 0.68rem; color: var(--text-3); text-transform:uppercase; letter-spacing:0.06em; margin-top:0.3rem; }
.bsx-scale-track { position: relative; width:100%; height:4px; background: var(--surface-highest); border-radius:2px; margin: 1.4rem 0 0.6rem 0; }
.bsx-scale-tick { position:absolute; top:-4px; width:1px; height:12px; background: var(--line); }
.bsx-scale-marker { position:absolute; top:-5px; width:6px; height:14px; border-radius:2px; transform: translateX(-50%); }
.bsx-scale-labels { display:flex; justify-content:space-between; font-family: var(--font-mono); font-size: 0.68rem;
  color: var(--text-3); font-weight:700; letter-spacing:0.02em; }

/* ---- risk contributions ---- */
.bsx-contrib-row { display:flex; justify-content:space-between; align-items:center; padding: 0.65rem 0;
  border-bottom: 1px solid var(--line-soft); font-size: 0.86rem; }
.bsx-contrib-row .amt { font-family: var(--font-mono); font-weight:700; color: var(--red); }
.bsx-contrib-total { display:flex; justify-content:space-between; align-items:center; margin-top:0.7rem; padding-top:0.7rem;
  border-top: 1px solid var(--line); font-family: var(--font-body); font-size: 0.7rem; text-transform:uppercase;
  letter-spacing:0.06em; color: var(--text-3); }
.bsx-contrib-total .amt { font-family: var(--font-mono); font-size: 1.2rem; font-weight:700; color: var(--text); }

/* ---- recent cases / ledger table ---- */
.bsx-table { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 0.82rem; }
.bsx-table th { text-align:left; font-family: var(--font-body); font-size: 0.66rem; font-weight:700; text-transform:uppercase;
  letter-spacing: 0.06em; color: var(--text-3); padding: 0.55rem 0.8rem; border-bottom: 1px solid var(--line); background: var(--surface); }
.bsx-table td { padding: 0.7rem 0.8rem; border-bottom: 1px solid var(--line-soft); vertical-align: middle; color: var(--text-2); }
.bsx-table tr.case-row td:first-child { border-left: 2px solid var(--row-accent, var(--line)); }
.bsx-table .case-id { color: var(--text); font-weight: 600; }
.bsx-risk-bar-track { width: 100%; height: 4px; background: var(--surface-highest); border-radius: 2px; margin-bottom: 0.3rem; }
.bsx-risk-bar-fill { height: 4px; border-radius: 2px; }
.bsx-pill { display:inline-block; font-family: var(--font-body); font-size: 0.66rem; font-weight:700; text-transform:uppercase;
  letter-spacing: 0.05em; padding: 0.22rem 0.55rem; border-radius: var(--radius-sm); border: 1px solid; }
.bsx-pill.green { color: var(--green); border-color: var(--green-dim); background: var(--green-bg); }
.bsx-pill.amber { color: var(--amber); border-color: var(--amber-dim); background: var(--amber-bg); }
.bsx-pill.red   { color: var(--red);   border-color: var(--red-dim);   background: var(--red-bg); }

/* ---- audit trail timeline ---- */
.bsx-timeline { position: relative; padding-left: 0; }
.bsx-timeline-item { position: relative; padding-left: 2rem; padding-bottom: 1.3rem; }
.bsx-timeline-item::before { content:""; position:absolute; left:10px; top:22px; bottom:-2px; width:1px; background: var(--line); }
.bsx-timeline-item:last-child::before { display:none; }
.bsx-timeline-dot { position:absolute; left:0; top:1px; width:21px; height:21px; border-radius:50%; background: var(--surface);
  border: 2px solid var(--line); display:flex; align-items:center; justify-content:center; }
.bsx-timeline-dot::after { content:""; width:6px; height:6px; border-radius:50%; background: var(--line); }
.bsx-timeline-item.head .bsx-timeline-dot { border-color: var(--primary); }
.bsx-timeline-item.head .bsx-timeline-dot::after { background: var(--primary); }
.bsx-timeline-ts { font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-3); margin-bottom: 0.15rem; }
.bsx-timeline-title { font-family: var(--font-body); font-size: 0.88rem; color: var(--text); }
.bsx-timeline-hash { font-family: var(--font-mono); font-size: 0.65rem; color: var(--text-3); background: var(--surface-lowest);
  border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 0.35rem 0.5rem; margin-top: 0.4rem; word-break: break-all; }

/* ---- ledger table (legacy, still used by chain_status) ---- */
.bsx-ledger-row {
  display: grid;
  grid-template-columns: 6rem 6rem 5rem 1fr 10rem;
  gap: 0.6rem;
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid var(--line-soft);
  font-family: var(--font-mono);
  font-size: 0.82rem;
  align-items: center;
}
.bsx-ledger-row.head {
  color: var(--text-3);
  text-transform: uppercase;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  border-bottom: 1px solid var(--line);
}
.bsx-ledger-row .band-GREEN, .bsx-ledger-row .band-LOW { color: var(--green); }
.bsx-ledger-row .band-AMBER, .bsx-ledger-row .band-MEDIUM, .bsx-ledger-row .band-HIGH { color: var(--amber); }
.bsx-ledger-row .band-RED, .bsx-ledger-row .band-CRITICAL { color: var(--red); }
.bsx-ledger-row .hash { color: var(--text-3); }
.bsx-ledger-broken { color: var(--red); font-family: var(--font-mono); font-weight: 600; }
.bsx-ledger-ok { color: var(--green); font-family: var(--font-mono); font-weight: 600; }
</style>
"""


def inject() -> None:
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
