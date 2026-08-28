"""One CSS injection, applied once at app startup.

AESTHETIC DIRECTION -- "Aperture", executed as an INSTRUMENT READOUT rather
than a web dashboard:

  * ONE thing dominates each screen (the verdict numeral, the document,
    the ladder). Everything else is a hairline-ruled list, not a box.
  * Boxes are near-eliminated. Sections are divided by a hairline rule and
    a mono caps label -- an instrument panel division. Only two elements
    are still drawn as objects: the verdict block and finding cards,
    because those are the two things an officer acts on.
  * Enormous type-scale contrast: 11px caps labels against a 5.5rem
    numeral. Scale contrast IS the hierarchy.

COLOUR DISCIPLINE -- the neutral ramp is graphite with a deliberate blue
bias (never a pure grey, which reads as unconsidered). The interactive
accent is a desaturated cold steel, NOT a saturated brand colour. That is
the central decision: GREEN / AMBER / RED are the only saturated hues
anywhere in the interface, so the only thing that can shout on screen is a
verdict. The app has no brand colour of its own -- the active case's
verdict colour is the page's colour, and it changes per case.

MOTION -- every curve and duration below comes from a published table
(emilkowalski/skills `animate`), never approximated:
    --ease-out     cubic-bezier(0.23, 1, 0.32, 1)     entrances, UI
    --ease-in-out  cubic-bezier(0.77, 0, 0.175, 1)    on-screen movement
UI durations stay in the 150-250ms band; entrances stagger 55ms. Only
`transform` and `opacity` are animated (never width/height/top/left, never
`transition: all`), hover motion is gated behind a real pointer, and
prefers-reduced-motion gets a GENTLER variant -- opacity without
translation -- rather than motion switched off entirely.

Each screen carries its own motion, tied to what that screen means:
    Command     metrics rise in sequence  -- a panel powering up
    Screening   the active step lifts     -- where you are in the flow
    Case file   verdict lands, then the ladder resolves tier by tier,
                and the dial's arc draws to the score
    Audit       the chain draws downward  -- links landing in order

TYPE -- Bricolage Grotesque (display, tight tracking at large sizes),
Hanken Grotesk (body/labels), JetBrains Mono for every technical readout.
The mono is a functional choice, not a mood one: MRZ lines, hashes, case
IDs and scores are scanned character-by-character, so it survives any
change of visual direction.
"""

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap">

<style>
:root{
  /* graphite with a deliberate blue bias -- never a neutral grey */
  --bg:#0a0c0f;
  --surface-lowest:#070909;
  --surface-low:#101419;
  --surface:#141920;
  --surface-high:#171c23;
  --surface-highest:#1e242c;
  --line:#232a33;
  --line-soft:#171d24;
  --outline:#3a444f;
  --text:#e6eaee;
  --text-2:#a8b2bd;
  --text-3:#6b7683;
  /* cold steel: interactive states only. deliberately desaturated so it
     can never compete with a verdict colour for attention. */
  --primary:#8fa6c0;
  --on-primary:#0a0c0f;
  --secondary-container:#1b232c;
  --on-secondary-container:#c3d0de;
  /* the only saturated hues in the entire interface */
  --green:#46b98a;  --green-dim:#2c7a5b;  --green-bg:rgba(70,185,138,.09);
  --amber:#d9a441;  --amber-dim:#8f6b21;  --amber-bg:rgba(217,164,65,.09);
  --red:#e05252;    --red-dim:#8f2f2f;    --red-bg:rgba(224,82,82,.09);
  --error:#ffb4ab;  --error-container:#93000a;
  --radius-sm:2px;
  --radius:3px;
  --radius-lg:4px;
  --font-head:'Bricolage Grotesque', system-ui, sans-serif;
  --font-body:'Hanken Grotesk', system-ui, sans-serif;
  --font-mono:'JetBrains Mono', ui-monospace, monospace;
  --shadow:none;
  /* motion tokens -- published values, never approximated */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --dur-fast: 150ms;
  --dur: 200ms;
  --dur-slow: 260ms;
  --stagger: 55ms;
}

/* ---- Streamlit chrome ----------------------------------------------
   The header is NOT hidden with visibility:hidden. It used to be, and
   that removed the only control that re-opens a collapsed sidebar --
   collapsing it stranded you with no way back. The header is kept
   visible and zero-height; only the individual controls we don't want
   (Deploy, main menu, toolbar) are removed, so whichever element this
   Streamlit version uses to re-expand the sidebar survives. Both known
   testids for that control are force-shown and restyled below.        */
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important;
  visibility: visible !important; pointer-events: none; }
header[data-testid="stHeader"] * { pointer-events: auto; }
/* stToolbar is NOT display:none -- the re-open control is a DESCENDANT of
   it, and display:none on an ancestor removes the whole subtree from
   rendering no matter what position/visibility the child declares. That
   exact mistake is what stranded a collapsed sidebar with no way back.
   Hide the toolbar's own unwanted children individually instead. */
[data-testid="stToolbar"] { display: flex !important; background: transparent !important;
  height: 0 !important; padding: 0 !important; }
[data-testid="stMainMenuButton"], [data-testid="stBaseButton-header"],
[data-testid="stBaseButton-headerNoPadding"], [data-testid="stStatusWidget"],
[data-testid="stToolbarActions"], [data-testid="stDecoration"], #MainMenu, footer { display: none !important; }

/* the re-open control: always reachable, never chrome-coloured. Styled on
   the element itself AND on a nested button, because the control is a
   <button> directly in some Streamlit versions and a wrapper in others. */
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] {
  display: flex !important; visibility: visible !important; opacity: 1 !important;
  pointer-events: auto !important; align-items: center !important; justify-content: center !important;
  position: fixed !important; top: 14px !important; left: 14px !important; z-index: 999999 !important;
  width: 40px !important; height: 40px !important; min-width: 40px !important;
  background: var(--surface-high) !important; border: 1px solid var(--outline) !important;
  border-radius: var(--radius) !important; color: var(--text) !important;
  transition: border-color var(--dur-fast) var(--ease-out), background-color var(--dur-fast) var(--ease-out);
}
[data-testid="stExpandSidebarButton"] button, [data-testid="stSidebarCollapsedControl"] button {
  background: transparent !important; border: none !important; color: var(--text) !important;
  width: 100% !important; height: 100% !important;
}
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"] {
  font-size: 22px !important; width: 22px !important; height: 22px !important; color: var(--text) !important; }
@media (hover: hover) and (pointer: fine) {
  [data-testid="stExpandSidebarButton"]:hover, [data-testid="stSidebarCollapsedControl"]:hover {
    background: var(--surface-highest) !important; border-color: var(--primary) !important; }
}

.block-container { padding-top:2.4rem !important; padding-bottom:5rem !important;
  padding-left:3rem !important; padding-right:3rem !important; max-width:1560px !important; }

/* ---- base ----
   The ground is not a flat fill. Two fixed layers sit behind everything:
   a faint engineering grid (the graticule of an instrument face) and a
   single cold pool of light in the upper left, which gives the page a
   light source and stops large empty regions reading as dead space. Both
   are far below text contrast and never sit over a verdict colour. */
html, body, [class*="css"] { font-family: var(--font-body); }
.stApp { background: var(--bg); color: var(--text); }
.stApp::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    linear-gradient(to right, rgba(143,166,192,.028) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(143,166,192,.028) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(120% 90% at 18% 0%, #000 0%, transparent 72%);
  -webkit-mask-image: radial-gradient(120% 90% at 18% 0%, #000 0%, transparent 72%);
}
.stApp::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background: radial-gradient(90% 60% at 12% -8%, rgba(143,166,192,.075), transparent 62%);
}
section[data-testid="stSidebar"], .block-container, header[data-testid="stHeader"] { position: relative; z-index: 1; }
h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: var(--font-head) !important; letter-spacing: -0.02em; color: var(--text) !important;
}
p, span, div, label { color: var(--text); }
code, .stCode, .stJson, pre { font-family: var(--font-mono) !important; }
[data-testid="stCaptionContainer"] { color: var(--text-3) !important; font-size:0.94rem; max-width:76ch; line-height:1.6; }
hr { border-color: var(--line-soft) !important; }

/* THE core structural override: st.container(border=True) paints a full
   rounded card, and a page of identical cards gives every element equal
   weight. Under this direction a container is a hairline TOP rule with
   its content hanging off it. */
div[data-testid="stVerticalBlockBorderWrapper"] {
  border: none !important; border-top: 1px solid var(--line) !important;
  border-radius: 0 !important; background: transparent !important;
  padding: 1.15rem 0 1.6rem 0 !important;
}
[data-testid="stExpander"] { border: none !important; border-top: 1px solid var(--line-soft) !important;
  border-radius: 0 !important; background: transparent; }
[data-testid="stExpander"] summary { font-family: var(--font-body); font-size: 0.82rem; color: var(--text-2); }

/* ====================== MOTION ======================================
   Entrances only: transform + opacity, 200-260ms, published curves,
   55ms stagger. Nothing loops, nothing autoplays, nothing blocks input. */
@keyframes bsx-rise { from { opacity:0; transform: translate3d(0,10px,0); } to { opacity:1; transform:none; } }
@keyframes bsx-fade { from { opacity:0; } to { opacity:1; } }
@keyframes bsx-land { from { opacity:0; transform: translate3d(0,14px,0) scale(.985); } to { opacity:1; transform:none; } }
@keyframes bsx-slide-in { from { opacity:0; transform: translate3d(-10px,0,0); } to { opacity:1; transform:none; } }
@keyframes bsx-draw { to { stroke-dashoffset: var(--dash-end, 0); } }
@keyframes bsx-pulse-once { 0%,100% { opacity:1; } 45% { opacity:.35; } }

/* PAGE-LEVEL: deliberately NOT a stagger.
   Switching pages is a constant action during operation, and Streamlit
   already costs a server round-trip per nav click. A per-block cascade
   ran up to 275ms of delay on top of that, so every navigation felt
   laggy and the content appeared to dribble in. The published guidance is
   explicit that a frequently-repeated action should not carry animation
   at all -- so navigation gets one 110ms opacity fade on the whole page
   and nothing else. Choreography is spent only where it is seen once
   per case (the verdict reveal), never on the path between screens. */
.block-container > div > div > div[data-testid="stVerticalBlock"] {
  animation: bsx-fade 110ms linear;
}

/* Gentler, not absent: keep the fade, drop the translation. */
@media (prefers-reduced-motion: reduce) {
  .block-container > div > div > div[data-testid="stVerticalBlock"] > div,
  .bsx-verdict, .bsx-verdict-num, .bsx-spine-row, .bsx-metric, .bsx-timeline-item, .bsx-finding {
    animation-name: bsx-fade !important;
  }
  .bsx-ring svg .bsx-arc { animation: none !important; stroke-dashoffset: var(--dash-end, 0) !important; }
  .bsx-decided { animation: none !important; }
}

/* ---- sidebar: a quiet rail. Navigation, not a feature. ---- */
section[data-testid="stSidebar"] {
  width: 268px !important; min-width: 268px !important; max-width: 268px !important;
  background: var(--surface-lowest); border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div { width: 268px; padding-top: 1.4rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.15rem; }
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] { border-top: none !important; padding: 0 !important; }
/* Streamlit's own collapse chevron is hover-only and zero-sized by
   default, so the control that hides the rail is itself undiscoverable.
   Forced to a permanent 32px target: a control with a destructive-feeling
   outcome (the whole nav disappears) should never be a hidden affordance. */
[data-testid="stSidebarCollapseButton"] {
  display: flex !important; align-items: center; justify-content: center;
  visibility: visible !important; opacity: 1 !important;
  width: 32px !important; height: 32px !important; }
[data-testid="stSidebarCollapseButton"] button {
  display: flex !important; align-items: center; justify-content: center;
  visibility: visible !important; opacity: 1 !important;
  width: 32px !important; height: 32px !important; min-height: 32px !important;
  color: var(--text-3) !important; background: transparent !important; border: none !important;
  transition: color var(--dur-fast) var(--ease-out); }
@media (hover: hover) and (pointer: fine) {
  [data-testid="stSidebarCollapseButton"] button:hover { color: var(--text) !important; }
}
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
  font-size: 20px !important; width: 20px !important; height: 20px !important; }

.bsx-sidebar-brand { padding: 0 1.1rem 1.3rem 1.1rem; margin-bottom: 0.9rem; border-bottom: 1px solid var(--line); }
.bsx-sidebar-brand .mark { width: 28px; height: 28px; border-radius: 50%; border: 1px solid var(--outline);
  position: relative; margin-bottom: 0.65rem; }
.bsx-sidebar-brand .mark::before { content:""; position:absolute; inset:6px; border-radius:50%; border:1px solid var(--outline); }
.bsx-sidebar-brand .mark::after { content:""; position:absolute; inset:11px; border-radius:50%; background: var(--primary); }
.bsx-sidebar-brand .name { font-family: var(--font-head); font-weight: 700; font-size: 1.18rem;
  color: var(--text); letter-spacing: -0.01em; line-height:1.15; }
.bsx-sidebar-brand .sub { font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-3);
  text-transform: uppercase; letter-spacing: 0.14em; margin-top: 0.3rem; }

section[data-testid="stSidebar"] .stButton > button {
  width: 100%; display: flex !important; justify-content: flex-start !important; align-items: center;
  gap: 0.7rem; text-align: left;
  background: transparent; border: none; border-left: 2px solid transparent; color: var(--text-3);
  font-family: var(--font-body); font-size: 1rem; font-weight: 500;
  padding: 0.72rem 1.1rem; border-radius: 0; min-height: 0;
  transition: color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out),
              background-color var(--dur-fast) var(--ease-out);
}
/* icons were 16px and unreadable -- the single most-reported legibility
   problem with the previous rail */
section[data-testid="stSidebar"] .stButton > button [data-testid="stIconMaterial"] {
  font-size: 21px !important; width: 21px !important; height: 21px !important;
}
section[data-testid="stSidebar"] .stButton > button p { font-family: inherit !important; font-size: inherit !important; text-align: left; }
@media (hover: hover) and (pointer: fine) {
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--surface-low); color: var(--text); border-left-color: var(--outline); }
}
.bsx-nav-note { font-size: 0.84rem; line-height:1.5; color: var(--text-3); padding: 0.95rem 1.1rem 0 1.1rem;
  margin-top: 1rem; border-top: 1px solid var(--line-soft); }
.bsx-nav-footer { border-top: 1px solid var(--line); margin-top: 0.6rem; padding-top: 0.5rem; }

/* ---- the recurring aperture motif. Decorative only, aria-hidden at
   every use site, information-free by design. ---- */
.bsx-aperture-ring { position: absolute; top: -18px; right: 0; width: 92px; height: 92px;
  border-radius: 50%; border: 1px solid var(--line); pointer-events: none; opacity:.75; }
.bsx-aperture-ring::before { content: ""; position: absolute; inset: 15px; border-radius: 50%; border: 1px solid var(--line); }
.bsx-aperture-ring::after { content: ""; position: absolute; inset: 34px; border-radius: 50%; border: 1px solid var(--line-soft); }

:focus-visible { outline: none !important; box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--primary) !important; }

/* ---- page head ---- */
.bsx-topbar { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem;
  padding-bottom: 1.5rem; margin-bottom: 0.4rem; flex-wrap: wrap; position: relative; }
.bsx-topbar .eyebrow { font-family: var(--font-mono); font-size: 0.79rem; text-transform: uppercase;
  letter-spacing: 0.18em; color: var(--text-3); margin-bottom: 0.6rem; }
.bsx-topbar .title { font-family: var(--font-head); font-weight: 700; font-size: 2.5rem;
  color: var(--text); letter-spacing: -0.035em; line-height: 1; text-wrap: balance; }
.bsx-topbar .sub { font-family: var(--font-body); font-size: 1.05rem; color: var(--text-3);
  margin-top: 0.7rem; max-width: 62ch; line-height: 1.5; }
.bsx-topbar .case-chip { font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-2);
  letter-spacing: 0.04em; border: 1px solid var(--line); border-radius: var(--radius); padding: 0.28rem 0.6rem; }
.bsx-topbar .meta { display:flex; align-items:center; gap:0.5rem; padding-bottom: 0.3rem; }
.bsx-chain-pill { font-family: var(--font-mono); font-size: 0.79rem; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; border-radius: var(--radius-sm); padding: 0.3rem 0.6rem; border: 1px solid; }
.bsx-chain-pill.ok { color: var(--green); border-color: var(--green-dim); background: var(--green-bg); }
.bsx-chain-pill.broken { color: var(--red); border-color: var(--red-dim); background: var(--red-bg); }

/* ---- section label: the only divider this design uses ---- */
.bsx-tier-head {
  font-family: var(--font-mono); font-size: 0.79rem; font-weight: 500; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--text-3); margin: 0 0 1rem 0; padding: 0; border: none;
  display: flex; align-items: center; gap: 0.7rem;
}
.bsx-tier-head::after { content:""; flex:1; height:1px; background: var(--line-soft); }

/* ===================== COMMAND: the metric strip =====================
   One ruled strip, not N cards. Cells power up left-to-right. */
.bsx-metric-strip { display:grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.bsx-metric { padding: 1.3rem 1.6rem 1.35rem 0; border-right: 1px solid var(--line-soft);
  animation: bsx-rise var(--dur) var(--ease-out) backwards; }
.bsx-metric:nth-child(1) { animation-delay: 0ms; }
.bsx-metric:nth-child(2) { animation-delay: 40ms; }
.bsx-metric:nth-child(3) { animation-delay: 80ms; }
.bsx-metric:last-child { border-right: none; }
.bsx-metric .label { font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--text-3); }
.bsx-metric .value { font-family: var(--font-mono); font-weight: 600; font-size: 2.5rem; color: var(--text);
  line-height: 1; margin-top: 0.65rem; font-variant-numeric: tabular-nums; letter-spacing:-0.03em; }
.bsx-metric .value.tone-red { color: var(--red); }
.bsx-metric .sub { font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-3);
  text-transform: uppercase; letter-spacing:0.1em; margin-left: 0.5rem; }

/* legacy .bsx-stat kept for un-migrated call sites, restyled to match */
.bsx-stat { background: transparent; border: none; border-top: 1px solid var(--line); padding: 1.1rem 0; height:100%; }
.bsx-stat .label { font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.16em;
  text-transform: uppercase; color: var(--text-3); }
.bsx-stat .value { font-family: var(--font-mono); font-size: 1.9rem; color: var(--text); line-height: 1;
  margin-top: 0.55rem; font-variant-numeric: tabular-nums; }
.bsx-stat .value.tone-red { color: var(--red); }
.bsx-stat .sub { font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-3);
  text-transform: uppercase; margin-left: 0.45rem; letter-spacing:0.08em; }

.bsx-pill-row { display:flex; gap:0.45rem; flex-wrap:wrap; margin-top:0.6rem; }
.bsx-status-dot { display:inline-flex; align-items:center; gap:0.45rem; font-family: var(--font-mono);
  font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-2);
  background: transparent; border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 0.25rem 0.55rem; }
.bsx-status-dot .dot { width: 5px; height: 5px; border-radius: 50%; }
.bsx-status-dot .dot.ok { background: var(--green); }
.bsx-status-dot .dot.bad { background: var(--red); }
.bsx-status-dot .dot.na { background: var(--text-3); }

/* ---- attack wall: hover colour previews the severity to expect ---- */
.st-key-atk_dob button, .st-key-atk_photo button, .st-key-atk_sig button,
.st-key-atk_recapture button, .st-key-atk_face button, .st-key-atk_genuine button {
  transition: color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out),
              background-color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out);
}
@media (hover: hover) and (pointer: fine) {
  .st-key-atk_dob button:hover, .st-key-atk_photo button:hover, .st-key-atk_sig button:hover {
    color: var(--amber) !important; border-color: var(--amber-dim) !important;
    background: var(--amber-bg) !important; transform: translate3d(0,-2px,0); }
  .st-key-atk_recapture button:hover, .st-key-atk_face button:hover {
    color: var(--red) !important; border-color: var(--red-dim) !important;
    background: var(--red-bg) !important; transform: translate3d(0,-2px,0); }
  .st-key-atk_genuine button:hover {
    color: var(--green) !important; border-color: var(--green-dim) !important;
    background: var(--green-bg) !important; transform: translate3d(0,-2px,0); }
}
.st-key-atk_dob button:active, .st-key-atk_photo button:active, .st-key-atk_sig button:active,
.st-key-atk_recapture button:active, .st-key-atk_face button:active, .st-key-atk_genuine button:active {
  transform: translate3d(0,0,0) scale(.985); }

div[data-testid="column"] .stButton > button, div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button {
  width: 100%; background: var(--surface-low) !important; color: var(--text-2) !important;
  border: 1px solid var(--line) !important; border-radius: var(--radius) !important;
  font-family: var(--font-mono) !important; font-weight: 500 !important; font-size: 0.82rem !important;
  letter-spacing: 0.13em; text-transform: uppercase; padding: 1.1rem 0.7rem !important;
  min-height: 78px !important; height: auto !important; line-height: 1.35 !important;
  transition: border-color var(--dur-fast) var(--ease-out), background-color var(--dur-fast) var(--ease-out),
              color var(--dur-fast) var(--ease-out), transform var(--dur-fast) var(--ease-out); box-shadow: none;
}
div[data-testid="column"] .stButton > button [data-testid="stIconMaterial"] { font-size: 19px !important; }
@media (hover: hover) and (pointer: fine) {
  div[data-testid="column"] .stButton > button:hover,
  div[data-testid="stVerticalBlockBorderWrapper"] .stButton > button:hover {
    border-color: var(--outline) !important; color: var(--text) !important; }
}
div[data-testid="column"] .stButton > button p { font-family: inherit !important; font-weight: inherit !important; letter-spacing: inherit; }
button[kind="primary"] { background: var(--primary) !important; color: var(--on-primary) !important;
  border: 1px solid var(--primary) !important; font-weight: 600 !important; }
button[kind="primary"]:hover { filter: brightness(1.1); }

/* ============ NEW SCREENING: an explicit two-step flow ============== */
.bsx-step { display:flex; align-items:center; gap:0.85rem; margin-bottom: 0.9rem; }
.bsx-step-num { width:26px; height:26px; border-radius:50%; border:1px solid var(--line); flex-shrink:0;
  display:flex; align-items:center; justify-content:center; font-family: var(--font-mono);
  font-size:0.7rem; color: var(--text-3); background: var(--surface);
  transition: color var(--dur) var(--ease-out), border-color var(--dur) var(--ease-out); }
.bsx-step.done .bsx-step-num { color: var(--green); border-color: var(--green-dim); background: var(--green-bg); }
.bsx-step.active .bsx-step-num { color: var(--primary); border-color: var(--primary); }
.bsx-step-label { font-family: var(--font-mono); font-size: 0.79rem; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--text-3); }
.bsx-step.active .bsx-step-label, .bsx-step.done .bsx-step-label { color: var(--text-2); }
.bsx-step-rule { flex:1; height:1px; background: var(--line-soft); }

/* ================ CASE FILE: the verdict block ======================
   The one element allowed to dominate a screen. It lands as a unit, then
   the numeral settles a beat later -- the score is the payload. */
.bsx-verdict { position: relative; padding: 2rem 2.2rem 1.7rem 2.2rem; border: 1px solid var(--line);
  border-radius: var(--radius-lg); background: var(--surface-low); overflow: hidden;
  animation: bsx-land var(--dur) var(--ease-out) backwards; }
.bsx-verdict::before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background: var(--vc, var(--text-3)); }
.bsx-verdict-grid { display:flex; align-items:flex-start; gap:2.6rem; flex-wrap:wrap; }
.bsx-verdict-num { font-family: var(--font-mono); font-weight: 700; font-size: 5.5rem; line-height: .82;
  color: var(--vc, var(--text)); font-variant-numeric: tabular-nums; letter-spacing: -0.05em;
  animation: bsx-rise var(--dur) var(--ease-out) 70ms backwards; }
.bsx-verdict-den { font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-3);
  letter-spacing: 0.16em; text-transform: uppercase; margin-top: 0.7rem; }
.bsx-verdict-body { flex:1; min-width: 260px; }
.bsx-verdict-band { display:inline-block; font-family: var(--font-mono); font-size: 0.79rem; font-weight: 600;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--vc); border:1px solid var(--vc);
  border-radius: var(--radius-sm); padding: 0.22rem 0.55rem; margin-bottom: 0.85rem; }
.bsx-verdict-action { font-family: var(--font-head); font-weight: 700; font-size: 1.9rem; line-height: 1.08;
  letter-spacing: -0.03em; color: var(--vc); text-wrap: balance; }
.bsx-verdict-why { font-size: 1.02rem; color: var(--text-2); margin-top: 0.75rem; line-height: 1.55; max-width: 58ch; }
.bsx-verdict-why b { color: var(--text); font-weight: 600; }

/* risk scale rail */
.bsx-scale-track { position: relative; width:100%; height:2px; background: var(--line); margin: 1.9rem 0 0.7rem 0; }
.bsx-scale-tick { position:absolute; top:-3px; width:1px; height:8px; background: var(--line); }
.bsx-scale-marker { position:absolute; top:-5px; width:2px; height:12px; transform: translateX(-50%);
  animation: bsx-fade var(--dur) var(--ease-out) 150ms backwards; }
.bsx-scale-marker::after { content:""; position:absolute; left:50%; top:-5px; transform:translateX(-50%);
  border-left:4px solid transparent; border-right:4px solid transparent; border-top:5px solid currentColor; }
.bsx-scale-labels { display:flex; justify-content:space-between; font-family: var(--font-mono); font-size: 0.77rem;
  color: var(--text-3); letter-spacing: 0.08em; text-transform: uppercase; }
.bsx-scale-labels .on { color: var(--text); }

/* ---- the Trust Ladder spine: the project's thesis, drawn. Tiers
   resolve top-down in ladder order -- the order they actually run. ---- */
.bsx-spine { position: relative; }
.bsx-spine-row { position: relative; display: grid; grid-template-columns: 34px 26px 1fr auto;
  gap: 0 0.85rem; align-items: start; padding: 0.75rem 0;
  animation: bsx-slide-in var(--dur-fast) var(--ease-out) backwards; }
.bsx-spine-row:nth-child(1) { animation-delay: 90ms; }
.bsx-spine-row:nth-child(2) { animation-delay: 130ms; }
.bsx-spine-row:nth-child(3) { animation-delay: 170ms; }
.bsx-spine-row:nth-child(4) { animation-delay: 210ms; }
.bsx-spine-row::before { content:""; position:absolute; left:46px; top:26px; bottom:-8px; width:1px; background: var(--line); }
.bsx-spine-row:last-child::before { display:none; }
.bsx-spine-tier { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-3);
  letter-spacing: 0.1em; padding-top: 0.32rem; }
.bsx-spine-dot { width: 21px; height: 21px; border-radius: 50%; border: 1px solid var(--line);
  background: var(--surface); display:flex; align-items:center; justify-content:center;
  font-family: var(--font-mono); font-size: 0.66rem; color: var(--text-3); position: relative; z-index:1; }
.bsx-spine-dot.pass { color: var(--green); border-color: var(--green-dim); }
.bsx-spine-dot.fail { color: var(--red); border-color: var(--red); background: var(--red-bg); }
.bsx-spine-dot.review { color: var(--amber); border-color: var(--amber-dim); background: var(--amber-bg); }
.bsx-spine-dot.na { color: var(--text-3); border-color: var(--line-soft); background: transparent; }
.bsx-spine-name { font-family: var(--font-body); font-size: 1.05rem; font-weight: 500; color: var(--text); line-height:1.35; }
.bsx-spine-row.na .bsx-spine-name { color: var(--text-3); font-weight: 400; }
.bsx-spine-row.fail .bsx-spine-name { color: var(--red); font-weight: 600; }
.bsx-spine-detail { font-size: 0.92rem; color: var(--text-3); margin-top: 0.2rem; line-height:1.45; max-width: 52ch; }
.bsx-spine-status { font-family: var(--font-mono); font-size: 0.79rem; letter-spacing: 0.12em;
  color: var(--text-3); padding-top: 0.3rem; }
.bsx-spine-row.fail .bsx-spine-status { color: var(--red); }
.bsx-spine-row.pass .bsx-spine-status { color: var(--green); }
.bsx-spine-row.review .bsx-spine-status { color: var(--amber); }
/* fires once, after its row has landed: this is the answer to "which
   layer decided?", so it earns exactly one blink and never repeats */
.bsx-decided { display:inline-block; font-family: var(--font-mono); font-size: 0.73rem; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--red); border:1px solid var(--red-dim); background: var(--red-bg);
  border-radius: var(--radius-sm); padding: 0.1rem 0.4rem; margin-left: 0.5rem; vertical-align: 2px;
  animation: bsx-pulse-once 460ms var(--ease-in-out) 300ms 1 backwards; }

/* ---- hairline data list: replaces every boxed key/value table ---- */
.bsx-datalist { display:flex; flex-direction: column; }
.bsx-field-row, .bsx-datarow { display:flex; justify-content:space-between; align-items:baseline; gap:1rem;
  padding: 0.62rem 0; border-bottom: 1px solid var(--line-soft); }
.bsx-field-row:last-child, .bsx-datarow:last-child { border-bottom: none; }
.bsx-field-name { font-family: var(--font-mono); color: var(--text-3); font-size:0.78rem;
  text-transform:uppercase; letter-spacing:0.12em; white-space: nowrap; }
.bsx-field-value { font-family: var(--font-mono); color: var(--text); font-size: 0.96rem; text-align: right;
  font-variant-numeric: tabular-nums; }

/* ---- finding cards: the second and last element drawn as a box ---- */
.bsx-finding { border: 1px solid var(--line); border-left: 3px solid var(--red);
  background: var(--surface-low); border-radius: 0 var(--radius) var(--radius) 0;
  overflow: hidden; margin-bottom: 0.7rem;
  animation: bsx-rise var(--dur-fast) var(--ease-out) 120ms backwards; }
.bsx-finding-head { padding: 0.8rem 1.1rem 0.55rem 1.1rem; font-family: var(--font-body); font-size: 0.98rem;
  font-weight: 600; letter-spacing: -0.01em; color: var(--red); }
.bsx-finding-body { padding: 0 1rem 0.9rem 1rem; }
.bsx-finding-body p { color: var(--text-2); font-size: 0.95rem; margin: 0 0 0.7rem 0; line-height:1.55; }
.bsx-finding.advisory { border-left-color: var(--amber); }
.bsx-finding.advisory .bsx-finding-head { color: var(--amber); }
.bsx-compare-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;
  font-family: var(--font-mono); font-size: 0.9rem; }
.bsx-compare-cell { border: 1px solid var(--line); border-radius: var(--radius-sm); padding: 0.5rem 0.65rem;
  background: var(--surface); color: var(--text); }
.bsx-compare-cell.bad { border-color: var(--red-dim); background: var(--red-bg); color: var(--red); }
.bsx-compare-cell .k { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-3);
  letter-spacing:0.12em; text-transform:uppercase; margin-bottom: 0.3rem; }

/* ---- signals (compact list form) ---- */
.bsx-signal { display: flex; gap: 0.7rem; align-items: flex-start; padding: 0.5rem 0;
  border-bottom: 1px solid var(--line-soft); font-size: 0.96rem; }
.bsx-signal:last-child { border-bottom: none; }
.bsx-signal.pass .check { color: var(--green); }
.bsx-signal.fail .check { color: var(--red); }
.bsx-signal.weak { opacity: 0.6; }
.bsx-signal .check { font-family: var(--font-mono); font-weight: 500; font-size: 0.78rem; color: var(--text); }
.bsx-signal .msg { color: var(--text-3); font-size:0.82rem; }

/* ---- verification sequence (legacy class, styled to match the spine) ---- */
.bsx-vseq-row { display:flex; align-items:center; gap:0.8rem; padding: 0.55rem 0;
  border-bottom: 1px solid var(--line-soft); }
.bsx-vseq-row:last-child { border-bottom:none; }
.bsx-vseq-dot { width:21px; height:21px; border-radius:50%; border:1px solid var(--line); display:flex;
  align-items:center; justify-content:center; font-family: var(--font-mono); font-size:0.66rem; flex-shrink:0;
  background: var(--surface); }
.bsx-vseq-dot.pass { color: var(--green); border-color: var(--green-dim); }
.bsx-vseq-dot.fail { color: var(--red); border-color: var(--red); background: var(--red-bg); }
.bsx-vseq-dot.na { color: var(--text-3); border-color: var(--line-soft); background: transparent; }
.bsx-vseq-dot.review { color: var(--amber); border-color: var(--amber-dim); background: var(--amber-bg); }
.bsx-vseq-label { flex:1; display:flex; justify-content:space-between; align-items:center;
  font-family: var(--font-body); font-size: 0.9rem; }
.bsx-vseq-label .status { font-family: var(--font-mono); font-size: 0.65rem; letter-spacing:0.12em;
  text-transform:uppercase; color: var(--text-3); }
.bsx-vseq-row.fail .bsx-vseq-label { color: var(--red); font-weight:600; }
.bsx-vseq-row.fail .status { color: var(--red); }
.bsx-vseq-row.na .bsx-vseq-label { color: var(--text-3); }
.bsx-vseq-row.review .bsx-vseq-label { color: var(--amber); font-weight:600; }
.bsx-vseq-row.review .status { color: var(--amber); }

/* ---- instrument dial: the arc DRAWS to the score, so the number is
   arrived at rather than asserted ---- */
.bsx-ring-wrap { display:flex; flex-direction:column; align-items:center; gap:0.9rem; }
.bsx-ring { position:relative; width:210px; height:210px; }
.bsx-ring svg { width:100%; height:100%; }
.bsx-ring .bsx-arc { animation: bsx-draw 460ms var(--ease-out) 60ms backwards; }
.bsx-ring-score { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
.bsx-ring-score .n { font-family: var(--font-mono); font-size: 3.4rem; font-weight:700; color: var(--text);
  line-height:1; font-variant-numeric: tabular-nums; letter-spacing:-0.04em; }
.bsx-ring-score .d { font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-3);
  text-transform:uppercase; letter-spacing:0.16em; margin-top:0.5rem; }

/* ---- risk contributions ---- */
.bsx-contrib-row { display:flex; justify-content:space-between; align-items:baseline; gap:1rem;
  padding: 0.62rem 0; border-bottom: 1px solid var(--line-soft); font-size: 0.96rem; color: var(--text-2); }
.bsx-contrib-row .amt { font-family: var(--font-mono); font-weight:600; color: var(--red); font-variant-numeric: tabular-nums; }
.bsx-contrib-total { display:flex; justify-content:space-between; align-items:baseline; margin-top:0.8rem;
  padding-top:0.8rem; border-top: 1px solid var(--line); font-family: var(--font-mono); font-size: 0.77rem;
  text-transform:uppercase; letter-spacing:0.16em; color: var(--text-3); }
.bsx-contrib-total .amt { font-family: var(--font-mono); font-size: 1.5rem; font-weight:700; color: var(--text);
  letter-spacing:-0.02em; font-variant-numeric: tabular-nums; }

/* ---- case table ---- */
.bsx-table { width: 100%; border-collapse: collapse; font-family: var(--font-body); font-size: 0.95rem; }
.bsx-table th { text-align:left; font-family: var(--font-mono); font-size: 0.76rem; font-weight:500;
  text-transform:uppercase; letter-spacing: 0.16em; color: var(--text-3); padding: 0 0.9rem 0.7rem 0;
  border-bottom: 1px solid var(--line); background: transparent; }
.bsx-table td { padding: 0.85rem 0.9rem 0.85rem 0; border-bottom: 1px solid var(--line-soft);
  vertical-align: middle; color: var(--text-2); }
.bsx-table tr:last-child td { border-bottom: none; }
.bsx-table tr.case-row td:first-child { border-left: 2px solid var(--row-accent, var(--line)); padding-left: 0.9rem; }
.bsx-table tr.case-row { transition: background-color var(--dur-fast) var(--ease-out); }
@media (hover: hover) and (pointer: fine) { .bsx-table tr.case-row:hover { background: var(--surface-low); } }
.bsx-table .case-id { color: var(--text); font-family: var(--font-mono); font-size:0.9rem; }
.bsx-table .finding-txt { color: var(--text-3); font-size: 0.9rem; line-height:1.45; }
.bsx-risk-bar-track { width: 100%; max-width: 90px; height: 2px; background: var(--line); margin-bottom: 0.4rem; }
.bsx-risk-bar-fill { height: 2px; }
.bsx-pill { display:inline-block; font-family: var(--font-mono); font-size: 0.75rem; font-weight:500;
  text-transform:uppercase; letter-spacing: 0.12em; padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm); border: 1px solid; }
.bsx-pill.green { color: var(--green); border-color: var(--green-dim); background: var(--green-bg); }
.bsx-pill.amber { color: var(--amber); border-color: var(--amber-dim); background: var(--amber-bg); }
.bsx-pill.red   { color: var(--red);   border-color: var(--red-dim);   background: var(--red-bg); }

/* ============ AUDIT: the chain draws downward, link by link ========= */
.bsx-timeline-item { position: relative; padding-left: 1.6rem; padding-bottom: 1.15rem;
  animation: bsx-rise var(--dur-fast) var(--ease-out) backwards; }
.bsx-timeline-item:nth-child(1) { animation-delay: 0ms; }
.bsx-timeline-item:nth-child(2) { animation-delay: 30ms; }
.bsx-timeline-item:nth-child(3) { animation-delay: 60ms; }
.bsx-timeline-item:nth-child(4) { animation-delay: 90ms; }
.bsx-timeline-item:nth-child(5) { animation-delay: 120ms; }
.bsx-timeline-item:nth-child(n+6) { animation-delay: 150ms; }
.bsx-timeline-item::before { content:""; position:absolute; left:4px; top:16px; bottom:-2px; width:1px; background: var(--line); }
.bsx-timeline-item:last-child::before { display:none; }
.bsx-timeline-dot { position:absolute; left:0; top:5px; width:9px; height:9px; border-radius:50%;
  background: var(--bg); border: 1px solid var(--outline); }
.bsx-timeline-item.head .bsx-timeline-dot { border-color: var(--primary); background: var(--primary); }
.bsx-timeline-ts { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-3); letter-spacing:0.06em; }
.bsx-timeline-title { font-family: var(--font-body); font-size: 0.98rem; color: var(--text); margin-top:0.15rem; }
.bsx-timeline-hash { font-family: var(--font-mono); font-size: 0.76rem; color: var(--text-3);
  margin-top: 0.3rem; word-break: break-all; }

/* ---- misc / legacy ---- */
.bsx-crypto-note { border: 1px solid var(--line); border-left: 3px solid var(--primary);
  background: var(--surface-low); border-radius: var(--radius); padding: 0.9rem 1.1rem;
  font-size: 0.98rem; color: var(--text-2); margin-top: 1rem; line-height:1.6; }
.bsx-crypto-note b { color: var(--text); }
.bsx-badge { border-radius: var(--radius-lg); padding: 1.2rem; text-align: center; margin-bottom: 1rem; border: 1px solid; }
.bsx-badge .light { font-family: var(--font-head); font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; }
.bsx-badge .meta { font-family: var(--font-mono); font-size: 0.78rem; margin-top: 0.3rem; opacity: 0.8; }
.bsx-badge.green { background: var(--green-bg); border-color: var(--green-dim); color: var(--green); }
.bsx-badge.amber { background: var(--amber-bg); border-color: var(--amber-dim); color: var(--amber); }
.bsx-badge.red   { background: var(--red-bg);   border-color: var(--red-dim);   color: var(--red); }
.bsx-ledger-row { display: grid; grid-template-columns: 6rem 6rem 5rem 1fr 10rem; gap: 0.6rem;
  padding: 0.5rem 0; border-bottom: 1px solid var(--line-soft); font-family: var(--font-mono); font-size: 0.8rem; }
.bsx-ledger-row.head { color: var(--text-3); text-transform: uppercase; font-size: 0.62rem;
  letter-spacing: 0.16em; border-bottom: 1px solid var(--line); }
.bsx-ledger-row .band-GREEN, .bsx-ledger-row .band-LOW { color: var(--green); }
.bsx-ledger-row .band-AMBER, .bsx-ledger-row .band-MEDIUM, .bsx-ledger-row .band-HIGH { color: var(--amber); }
.bsx-ledger-row .band-RED, .bsx-ledger-row .band-CRITICAL { color: var(--red); }
.bsx-ledger-row .hash { color: var(--text-3); }
.bsx-ledger-broken { color: var(--red); font-family: var(--font-mono); font-weight: 600; }
.bsx-ledger-ok { color: var(--green); font-family: var(--font-mono); font-weight: 600; }
.bsx-cap-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:0.5rem; }

/* ===================== OVERVIEW: the front page =====================
   The only screen in the product that is READ rather than operated, so
   it is the only one allowed editorial scale: a display line large
   enough to state the thesis, generous measure, and no dense data at
   all. Everything else in the console earns its density; this page
   earns its whitespace. */
.bsx-hero { position: relative; padding: 3.4rem 0 3rem 0; }
.bsx-hero-eyebrow { font-family: var(--font-mono); font-size: 0.82rem; letter-spacing: 0.2em;
  text-transform: uppercase; color: var(--text-3); margin-bottom: 1.6rem;
  animation: bsx-rise var(--dur-slow) var(--ease-out) backwards; }
/* h1.bsx-hero-title, not .bsx-hero-title: Streamlit ships its own
   `h1 { font-size: 2.75rem }` which outranks a bare class selector and
   was flattening the display line to 44px. */
.bsx-hero h1.bsx-hero-title { font-family: var(--font-head) !important; font-weight: 800;
  font-size: clamp(3.2rem, 6.6vw, 6rem) !important; line-height: 0.92; letter-spacing: -0.045em;
  color: var(--text); margin: 0; padding: 0; text-wrap: balance;
  /* never let the display line run under the orb's 280px column */
  max-width: calc(100% - 330px);
  animation: bsx-rise var(--dur) var(--ease-out) 40ms backwards; }
.bsx-hero-title .dim { color: var(--text-3); }
.bsx-hero-thesis { font-family: var(--font-head); font-weight: 600;
  font-size: clamp(1.3rem, 2.3vw, 1.95rem); line-height: 1.28; letter-spacing: -0.02em;
  color: var(--text-2); max-width: 30ch; margin: 2rem 0 0 0; text-wrap: balance;
  animation: bsx-rise var(--dur) var(--ease-out) 80ms backwards; }
.bsx-hero-thesis em { font-style: normal; color: var(--text); }
.bsx-hero-lede { font-size: 1.12rem; line-height: 1.68; color: var(--text-3);
  max-width: 62ch; margin-top: 1.5rem;
  animation: bsx-rise var(--dur) var(--ease-out) 120ms backwards; }
.bsx-hero-rule { height: 1px; background: var(--line); margin: 3rem 0 0 0; }
/* ---- the orb: a holographic HUD element, CSS only ----
   No Three.js and no JS: st.markdown does not execute scripts, and
   decoration should not cost a WebGL context.

   The first attempt failed for a specific reason worth recording -- it
   was built from FLAT concentric circles plus a hard conic wedge, which
   reads as a dartboard with a broken pie slice, not a sphere. Depth is
   what makes an orb: three rings tilted in 3D on different axes read as
   ORBITS around a lit core, and the sweep is a soft radial falloff
   rather than a hard-edged wedge. Everything animates on transform and
   opacity only, so it all stays on the compositor.

   The orb gets its own blue (--orb), deliberately outside the semantic
   set: it can never be mistaken for GREEN/AMBER/RED, and it only ever
   appears on Overview, a page that shows no verdicts. */
@keyframes bsx-orbit-a { from { transform: rotateX(74deg) rotateZ(0deg); }   to { transform: rotateX(74deg) rotateZ(360deg); } }
@keyframes bsx-orbit-b { from { transform: rotateX(68deg) rotateY(58deg) rotateZ(360deg); } to { transform: rotateX(68deg) rotateY(58deg) rotateZ(0deg); } }
@keyframes bsx-orbit-c { from { transform: rotateX(70deg) rotateY(-56deg) rotateZ(0deg); } to { transform: rotateX(70deg) rotateY(-56deg) rotateZ(360deg); } }
@keyframes bsx-spin { to { transform: rotate(360deg); } }
@keyframes bsx-spin-rev { to { transform: rotate(-360deg); } }
@keyframes bsx-breathe { 0%, 100% { opacity: .72; transform: scale(1); } 50% { opacity: 1; transform: scale(1.06); } }

.bsx-orb { --orb: #6aa8ff;
  position: absolute; right: 10px; top: 0.6rem; width: 280px; height: 280px;
  pointer-events: auto; cursor: crosshair; perspective: 900px;
  transition: transform var(--dur) var(--ease-out);
  animation: bsx-fade 420ms var(--ease-out) 120ms backwards; }
.bsx-orb > * { position: absolute; inset: 0; border-radius: 50%; }

/* the lit sphere: off-centre highlight gives it a light source */
.bsx-orb .sphere { inset: 88px;
  background: radial-gradient(circle at 38% 32%,
      rgba(224,238,255,.95) 0%, var(--orb) 22%,
      rgba(58,108,190,.55) 52%, rgba(30,58,110,.18) 72%, transparent 78%);
  box-shadow: 0 0 46px rgba(106,168,255,.35), 0 0 110px rgba(106,168,255,.14);
  animation: bsx-breathe 4s var(--ease-in-out) infinite;
  transition: opacity var(--dur) var(--ease-out); }

/* three tilted orbital rings -- the depth cue the flat version lacked */
.bsx-orb .orbit { inset: 26px; border: 1px solid rgba(106,168,255,.42);
  border-top-color: rgba(190,220,255,.95); border-bottom-color: rgba(106,168,255,.12); }
.bsx-orb .orbit-a { animation: bsx-orbit-a 11s linear infinite; }
.bsx-orb .orbit-b { inset: 42px; animation: bsx-orbit-b 15s linear infinite; opacity: .8; }
.bsx-orb .orbit-c { inset: 58px; animation: bsx-orbit-c 19s linear infinite; opacity: .62; }

/* graduated bezel: real tick marks, masked to a thin annulus so they can
   never spill into the square bounding box the way the old crosshair
   lines did */
.bsx-orb .bezel { border: 1px solid rgba(106,168,255,.22); }
.bsx-orb .ticks {
  background: repeating-conic-gradient(from 0deg,
      rgba(106,168,255,.75) 0deg 0.5deg, transparent 0.5deg 6deg);
  -webkit-mask: radial-gradient(circle, transparent 0 45.5%, #000 45.5% 49.5%, transparent 49.5%);
  mask: radial-gradient(circle, transparent 0 45.5%, #000 45.5% 49.5%, transparent 49.5%);
  animation: bsx-spin 60s linear infinite; opacity: .7; }

/* soft scanning falloff -- a gradient that fades to nothing, never the
   hard-edged wedge that made the first version look broken */
.bsx-orb .scan { inset: 12px;
  background: conic-gradient(from 0deg,
      rgba(106,168,255,.30) 0deg, rgba(106,168,255,.10) 22deg,
      rgba(106,168,255,.02) 46deg, transparent 74deg, transparent 360deg);
  -webkit-mask: radial-gradient(circle, #000 0 48%, transparent 49%);
  mask: radial-gradient(circle, #000 0 48%, transparent 49%);
  animation: bsx-spin-rev 7s linear infinite;
  transition: opacity var(--dur) var(--ease-out); }

/* hover: transform + opacity only. Ring SPEED is deliberately unchanged
   -- retiming a running rotation makes it visibly jump mid-turn. */
.bsx-orb .halo { inset: -16px; border: 1px solid var(--orb); opacity: 0; transform: scale(.94);
  box-shadow: 0 0 30px rgba(106,168,255,.25);
  transition: opacity var(--dur) var(--ease-out), transform var(--dur) var(--ease-out); }
@media (hover: hover) and (pointer: fine) {
  .bsx-orb:hover { transform: scale(1.05); }
  .bsx-orb:hover .halo { opacity: .7; transform: scale(1); }
  .bsx-orb:hover .sphere { opacity: 1; }
  .bsx-orb:hover .scan { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .bsx-orb .orbit, .bsx-orb .ticks, .bsx-orb .scan, .bsx-orb .sphere { animation: none !important; }
  .bsx-orb .orbit-a { transform: rotateX(74deg); }
  .bsx-orb .orbit-b { transform: rotateX(68deg) rotateY(58deg); }
  .bsx-orb .orbit-c { transform: rotateX(70deg) rotateY(-56deg); }
  .bsx-orb:hover { transform: none; }
}
@media (max-width: 1180px) { .bsx-orb { display: none; } }

/* the four tiers, stated as the architecture rather than a live result */
.bsx-tier-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 0; }
.bsx-tiercard { padding: 1.6rem 1.7rem 1.7rem 0; border-top: 1px solid var(--line);
  border-right: 1px solid var(--line-soft); position: relative;
  animation: bsx-rise var(--dur) var(--ease-out) backwards; }
.bsx-tiercard:nth-child(1){animation-delay:0ms;} .bsx-tiercard:nth-child(2){animation-delay:40ms;}
.bsx-tiercard:nth-child(3){animation-delay:80ms;} .bsx-tiercard:nth-child(4){animation-delay:120ms;}
.bsx-tiercard:last-child { border-right: none; }
.bsx-tiercard::before { content:""; position:absolute; top:-1px; left:0; width:34px; height:2px; background: var(--tc, var(--outline)); }
.bsx-tiercard .code { font-family: var(--font-mono); font-size: 0.82rem; letter-spacing: 0.16em;
  color: var(--tc, var(--text-3)); }
.bsx-tiercard .name { font-family: var(--font-head); font-weight: 600; font-size: 1.22rem;
  letter-spacing: -0.02em; color: var(--text); margin-top: 0.7rem; line-height:1.2; }
.bsx-tiercard .role { font-family: var(--font-mono); font-size: 0.76rem; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--tc, var(--text-3)); margin-top: 0.55rem; }
.bsx-tiercard .desc { font-size: 0.98rem; line-height: 1.6; color: var(--text-3); margin-top: 0.85rem; max-width: 34ch; }

/* honest limitations, stated on the front page rather than discovered in Q&A */
.bsx-honesty { display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem 2.5rem; }
.bsx-honesty-item .k { font-family: var(--font-mono); font-size: 0.78rem; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--amber); margin-bottom: 0.6rem; }
.bsx-honesty-item .v { font-size: 1rem; line-height: 1.65; color: var(--text-3); max-width: 44ch; }
.bsx-honesty-item .v b { color: var(--text-2); font-weight: 600; }

/* wide content never scrolls the page body sideways */
.bsx-scroll-x { overflow-x: auto; }
[data-testid="stImage"] img { border-radius: var(--radius); }
</style>
"""


def inject() -> None:
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
