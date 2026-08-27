"""One CSS injection, applied once at app startup. Aesthetic direction:
a forensic/security-operations console, not a consumer app -- dark,
high-contrast, technical typography. Deliberately the same visual
identity as the project's own strategy dossier (docs/, published as an
artifact): Archivo for chrome, Source Serif 4 for longer text, IBM Plex
Mono for every data readout -- the same mono family family the MRZ/VIZ
fields in the actual documents are rendered in, so the console and the
documents it inspects share one visual language.

Semantic colour (the GREEN/AMBER/RED verdict) is kept strictly separate
from the brand accent (teal) -- see dataviz principles: traffic-light
colour means one thing only, and never doubles as decoration.
"""

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap">

<style>
:root{
  --ground:#0B1119;
  --surface:#121A24;
  --surface-2:#1A2432;
  --line:#28323F;
  --line-soft:#1E2833;
  --text:#E7EDF3;
  --text-2:#9FACB9;
  --text-3:#6C7A88;
  --accent:#4FC7D9;
  --accent-soft:#12333A;
  --accent-line:#2B5C66;
  --green:#2FA968;
  --green-bg:#12271D;
  --amber:#D9A441;
  --amber-bg:#2B2211;
  --red:#E2564F;
  --red-bg:#2E1614;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 12px 32px -18px rgba(0,0,0,.9);
}

/* ---- kill default Streamlit chrome ---- */
#MainMenu, footer, header[data-testid="stHeader"] {visibility:hidden; height:0;}
.stDeployButton {display:none;}
div[data-testid="stDecoration"] {display:none;}
div[data-testid="stToolbar"] {display:none;}

/* ---- base ---- */
html, body, [class*="css"] {
  font-family: "Source Serif 4", Georgia, serif;
}
.stApp {
  background: var(--ground);
  color: var(--text);
}
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: Archivo, "Helvetica Neue", Arial, sans-serif !important;
  letter-spacing: -0.01em;
  color: var(--text) !important;
}
p, span, div, label {
  color: var(--text);
}
code, .stCode, .stJson, pre {
  font-family: "IBM Plex Mono", ui-monospace, monospace !important;
}
[data-testid="stCaptionContainer"] { color: var(--text-2) !important; }
[data-testid="stExpander"] { border-color: var(--line) !important; background: var(--surface); border-radius: 8px; }
hr { border-color: var(--line-soft) !important; }

/* ---- masthead ---- */
.bsx-eyebrow {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.35rem;
}
.bsx-title {
  font-family: Archivo, sans-serif;
  font-weight: 700;
  font-size: 2.1rem;
  letter-spacing: -0.02em;
  color: var(--text);
  margin: 0 0 0.35rem 0;
}
.bsx-sub {
  color: var(--text-2);
  font-size: 0.98rem;
  max-width: 62rem;
  line-height: 1.5;
}

/* ---- attack wall buttons ---- */
div[data-testid="column"] .stButton > button {
  width: 100%;
  min-height: 5.6rem;
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  font-family: Archivo, sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  letter-spacing: -0.005em;
  transition: border-color 0.15s ease, transform 0.1s ease, background 0.15s ease;
  box-shadow: var(--shadow);
  white-space: pre-line;
  line-height: 1.4;
}
div[data-testid="column"] .stButton > button:hover {
  border-color: var(--accent) !important;
  background: var(--accent-soft) !important;
  transform: translateY(-1px);
}
div[data-testid="column"] .stButton > button:active {
  transform: translateY(0);
}
div[data-testid="column"] .stButton > button p {
  font-family: Archivo, sans-serif !important;
  font-weight: 600 !important;
}

/* ---- verdict badge ---- */
.bsx-badge {
  border-radius: 10px;
  padding: 1.4rem 1.2rem;
  text-align: center;
  margin-bottom: 1rem;
  border: 1px solid;
  animation: bsx-fade-in 0.3s ease;
}
.bsx-badge .light {
  font-family: Archivo, sans-serif;
  font-size: 2.4rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  line-height: 1.1;
}
.bsx-badge .meta {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.85rem;
  margin-top: 0.3rem;
  opacity: 0.85;
}
.bsx-badge.green { background: var(--green-bg); border-color: var(--green); color: var(--green); }
.bsx-badge.amber { background: var(--amber-bg); border-color: var(--amber); color: var(--amber); }
.bsx-badge.red   { background: var(--red-bg);   border-color: var(--red);   color: var(--red); }

@keyframes bsx-fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ---- crypto-override callout ---- */
.bsx-crypto-note {
  border: 1px solid var(--accent-line);
  background: var(--accent-soft);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  font-size: 0.9rem;
  color: var(--text);
  margin-bottom: 1rem;
}
.bsx-crypto-note b { color: var(--accent); }

/* ---- tier sections ---- */
.bsx-tier-head {
  font-family: "IBM Plex Mono", monospace;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-3);
  margin: 1.1rem 0 0.4rem 0;
  padding-bottom: 0.3rem;
  border-bottom: 1px dotted var(--line);
}
.bsx-signal {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  border-left: 3px solid transparent;
  margin-bottom: 0.2rem;
  font-size: 0.9rem;
}
.bsx-signal.pass { border-left-color: var(--green); }
.bsx-signal.fail { border-left-color: var(--red); background: rgba(226,86,79,0.07); }
.bsx-signal.weak { border-left-color: var(--text-3); opacity: 0.75; }
.bsx-signal .check {
  font-family: "IBM Plex Mono", monospace;
  font-weight: 600;
  font-size: 0.82rem;
  color: var(--text);
}
.bsx-signal .msg { color: var(--text-2); }

/* ---- ledger table ---- */
.bsx-ledger-row {
  display: grid;
  grid-template-columns: 6rem 6rem 5rem 1fr 10rem;
  gap: 0.6rem;
  padding: 0.5rem 0.7rem;
  border-bottom: 1px solid var(--line-soft);
  font-family: "IBM Plex Mono", monospace;
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
.bsx-ledger-broken { color: var(--red); font-family: "IBM Plex Mono", monospace; font-weight: 600; }
.bsx-ledger-ok { color: var(--green); font-family: "IBM Plex Mono", monospace; font-weight: 600; }
</style>
"""


def inject() -> None:
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
