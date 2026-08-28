"""Render functions for the BorderShield console. Kept separate from
app.py's orchestration (session state, ledger writes) so each piece is
independently readable: a render function takes data and returns markup,
it never reaches into st.session_state or the filesystem itself.
"""
from __future__ import annotations

from core.crypto import ledger as ledger_module
from core.risk import traffic_light
from core.types import Band, Tier, Verdict

_TIER_ORDER = [Tier.CRYPTO, Tier.RULES, Tier.FORENSICS, Tier.BIOMETRIC]
_TIER_LABEL = {
    Tier.CRYPTO: "T0 · Cryptographic proof",
    Tier.RULES: "T1 · Deterministic structure",
    Tier.FORENSICS: "T2 · Forensic ML (advisory)",
    Tier.BIOMETRIC: "T2 · Biometric (advisory)",
}
_SEVERITY_ICON = {"pass": "✓", "fail": "✕", "weak": "⚠"}


def crypto_note(verdict: Verdict) -> str | None:
    if not verdict.crypto_override:
        return None
    return ("<div class='bsx-crypto-note'><b>Decided by cryptography, not a model.</b> "
            "This verdict was forced by a signature/manifest failure in the T0 tier. "
            "No forensic or biometric score was consulted for this decision.</div>")


# ============================================================ new screens ===
# Everything below backs the 5-screen sidebar console (ui/pages.py). Same
# contract as above: pure functions, data in, markup out, never touch
# session_state or the filesystem.

_BAND_HEX = {"LOW": "#4caf7d", "MEDIUM": "#d89b3c", "HIGH": "#d89b3c", "CRITICAL": "#d9564c"}
_LIGHT_CLASS = {"GREEN": "green", "AMBER": "amber", "RED": "red"}
_LIGHT_PILL_TEXT = {"GREEN": "CLEARED", "AMBER": "REVIEW", "RED": "CRITICAL"}


def sidebar_brand_html() -> str:
    """The concentric-circle mark is the aperture motif at its smallest --
    the same decorative element that appears on page heads, reused as the
    product's own mark so the identity and the ornament are one thing."""
    return ("<div class='bsx-sidebar-brand'>"
            "<div class='mark' aria-hidden='true'></div>"
            "<div class='name'>BorderShield AI</div>"
            "<div class='sub'>Screening Console</div>"
            "</div>")


def topbar_html(title: str, subtitle: str = "", case_chip: str = "", chain_ok: bool | None = None,
                 eyebrow: str = "") -> str:
    chip_html = f"<span class='case-chip'>{case_chip}</span>" if case_chip else ""
    chain_html = ""
    if chain_ok is not None:
        cls, txt = ("ok", "Ledger intact") if chain_ok else ("broken", "Chain broken")
        chain_html = f"<span class='bsx-chain-pill {cls}'>{txt}</span>"
    sub_html = f"<div class='sub'>{subtitle}</div>" if subtitle else ""
    eyebrow_html = f"<div class='eyebrow'>{eyebrow}</div>" if eyebrow else ""
    return (
        "<div class='bsx-topbar'>"
        "<div class='bsx-aperture-ring' aria-hidden='true'></div>"
        f"<div>{eyebrow_html}<div class='title'>{title}</div>{sub_html}</div>"
        f"<div class='meta'>{chip_html}{chain_html}</div>"
        "</div>"
    )


def hero_html() -> str:
    """The front page's opening statement. Every claim here is the
    project's own documented position (README, docs/01-RESEARCH.md) --
    nothing is a marketing number, and no metric appears that isn't
    produced live elsewhere in the console."""
    return """
    <div class="bsx-hero">
      <div class="bsx-orb" aria-hidden="true">
        <span class="halo"></span>
        <span class="bezel"></span>
        <span class="ticks"></span>
        <span class="scan"></span>
        <span class="orbit orbit-a"></span>
        <span class="orbit orbit-b"></span>
        <span class="orbit orbit-c"></span>
        <span class="sphere"></span>
      </div>
      <div class="bsx-hero-eyebrow">PS 26188 &middot; Ministry of Home Affairs &middot; Sashastra Seema Bal</div>
      <h1 class="bsx-hero-title">BorderShield<span class="dim"> AI</span></h1>
      <p class="bsx-hero-thesis">Everyone else builds a classifier.<br>
        We build a <em>trust hierarchy</em>.</p>
      <p class="bsx-hero-lede">An identity and document screening console for border control.
        Cryptography decides first. Deterministic rules decide second. Machine learning only
        ever advises &mdash; and is structurally incapable of condemning a document on its own.
        That rule is enforced in <code>core/risk.py</code>, not just asserted in a pitch.</p>
      <div class="bsx-hero-rule"></div>
    </div>
    """


def tier_grid_html() -> str:
    """The Trust Ladder stated as architecture. Same four tiers the case
    file resolves live -- shown here as the design, there as the result."""
    tiers = [
        ("T0", "Cryptographic proof", "Decisive both ways", "var(--green)",
         "A signed manifest over the document's fields, portrait and MRZ. Change one pixel of "
         "the portrait and verification fails — no model is consulted."),
        ("T1", "Deterministic structure", "Decisive against only", "var(--primary)",
         "ICAO check digits, cross-zone consistency between the printed fields and the MRZ, and "
         "versioned YAML rules. It can condemn a document; it cannot clear one."),
        ("T2", "Forensic analysis", "Advisory — capped at HIGH", "var(--amber)",
         "Portrait-region statistics, noise residual and recapture signatures. Raises a document "
         "for a human to look at. Never reaches CRITICAL alone."),
        ("T2", "Biometric match", "Advisory — capped at HIGH", "var(--amber)",
         "1:1 face comparison against the document portrait, behind a quality gate. A bad capture "
         "returns REVIEW with no similarity score at all."),
    ]
    cards = "".join(
        f"<div class='bsx-tiercard' style='--tc:{colour};'>"
        f"<div class='code'>{code}</div><div class='name'>{name}</div>"
        f"<div class='role'>{role}</div><div class='desc'>{desc}</div></div>"
        for code, name, role, colour, desc in tiers)
    return f"<div class='bsx-tier-grid'>{cards}</div>"


def honesty_html() -> str:
    """Stated on the front page deliberately. The project's own research
    notes treat volunteering these as a credibility gain -- a reviewer who
    discovers them in Q&A reads them as a weakness instead."""
    items = [
        ("Synthetic documents", "Every metric in this console comes from <b>our own generated UTO "
         "specimen</b> — a fictional ICAO example state, permanently watermarked. No real travel "
         "document is used anywhere in this build."),
        ("Demo signing authority", "The cryptography is real: X.509 chain, ECDSA P-256 signatures. "
         "The <b>trust anchor is ours</b>, not a government's. This is not ICAO Passive Authentication "
         "and not the PKD."),
        ("Hash chain, not blockchain", "The audit trail is an append-only hash-chained file. Real "
         "tamper-evidence for in-place edits, with a <b>documented limitation</b> against "
         "tail-truncation."),
    ]
    return ("<div class='bsx-honesty'>" + "".join(
        f"<div class='bsx-honesty-item'><div class='k'>{k}</div><div class='v'>{v}</div></div>"
        for k, v in items) + "</div>")


def step_head_html(number: int, label: str, state: str = "") -> str:
    """A numbered step marker for the intake flow. `state` is "" (pending),
    "active" (this is where you are) or "done" (satisfied). Screening is
    genuinely sequential -- a document, then optionally a face -- so the
    intake screen says where you are rather than presenting two
    interchangeable upload boxes."""
    return (f"<div class='bsx-step {state}'><div class='bsx-step-num'>{number}</div>"
             f"<div class='bsx-step-label'>{label}</div><div class='bsx-step-rule'></div></div>")


def metric_cell_html(label: str, value: str, sublabel: str = "", tone: str = "") -> str:
    tone_cls = f" tone-{tone}" if tone else ""
    sub_html = f"<span class='sub'>{sublabel}</span>" if sublabel else ""
    return (f"<div class='bsx-metric'><div class='label'>{label}</div>"
             f"<div class='value{tone_cls}'>{value}{sub_html}</div></div>")


def status_cell_html(label: str, dots: list[tuple[bool, str]]) -> str:
    chips = "".join(
        f"<span class='bsx-status-dot'><span class='dot {'ok' if ok else 'bad'}'></span>{txt}</span>"
        for ok, txt in dots)
    return (f"<div class='bsx-metric'><div class='label'>{label}</div>"
             f"<div class='bsx-pill-row'>{chips}</div></div>")


def metric_strip_html(cells: list[str]) -> str:
    """Takes already-rendered cells (metric_cell_html / status_cell_html)
    and rules them into ONE strip. Three separate bordered cards gave three
    unrelated numbers equal visual weight and read as dashboard filler; a
    single strip divided by hairlines reads as one instrument panel."""
    return f"<div class='bsx-metric-strip'>{''.join(cells)}</div>"


def recent_cases_table_html(records: list[dict], limit: int = 8) -> str:
    if not records:
        return ("<p style='color:var(--text-3);font-family:var(--font-mono);font-size:0.85rem;'>"
                 "No cases screened yet.</p>")
    rows = []
    for r in reversed(records[-limit:]):
        band = r.get("band", "?")
        light = {"LOW": "GREEN", "MEDIUM": "AMBER", "HIGH": "AMBER", "CRITICAL": "RED"}.get(band, "AMBER")
        cls = _LIGHT_CLASS[light]
        score = r.get("score", 0)
        ts = r.get("timestamp", "")
        time_txt = ts[11:19] + " UTC" if len(ts) >= 19 else "--"
        rows.append(
            "<tr class='case-row' style='--row-accent:var(--" + cls + ");'>"
            f"<td class='case-id'>{r.get('case_id', '?')}</td>"
            f"<td>{r.get('document', 'UTO Passport')}</td>"
            "<td>"
            f"<div class='bsx-risk-bar-track'><div class='bsx-risk-bar-fill' "
            f"style='width:{score}%;background:var(--{cls});'></div></div>"
            f"<span style='font-size:0.68rem;color:var(--text-3);'>{score}% {band}</span>"
            "</td>"
            f"<td>{r.get('finding', 'No findings')}</td>"
            f"<td style='color:var(--text-3);'>{time_txt}</td>"
            f"<td><span class='bsx-pill {cls}'>{_LIGHT_PILL_TEXT[light]}</span></td>"
            "</tr>"
        )
    return (
        "<table class='bsx-table'><thead><tr>"
        "<th>Case</th><th>Document</th><th>Risk</th><th>Finding</th><th>Time</th><th>Status</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


_TIER_SEQ_LABEL = {
    Tier.CRYPTO: "Cryptographic Integrity",
    Tier.RULES: "Document Structure & Rules",
    Tier.FORENSICS: "Forensic Analysis",
    Tier.BIOMETRIC: "Biometric Verification",
}


_TIER_CODE = {Tier.CRYPTO: "T0", Tier.RULES: "T1", Tier.FORENSICS: "T2", Tier.BIOMETRIC: "T2"}
_TIER_ROLE = {
    Tier.CRYPTO: "Decisive both ways",
    Tier.RULES: "Decisive against only",
    Tier.FORENSICS: "Advisory — capped at HIGH",
    Tier.BIOMETRIC: "Advisory — capped at HIGH",
}


def verification_sequence_html(verdict: Verdict) -> str:
    """The Trust Ladder drawn as a vertical spine, with the tier that
    actually decided the verdict called out.

    This is the project's whole thesis (cryptography decides first, rules
    second, ML only advises) so it gets drawn as real structure rather
    than listed as four equal rows: the connecting spine makes the
    ordering visible, and the DECIDED HERE marker answers the first
    question any reviewer asks -- which layer produced this verdict?
    """
    from core.types import Severity

    # The deciding tier is the FIRST tier in ladder order carrying a FAIL:
    # _TIER_ORDER is already priority-ordered, and core/risk.py resolves
    # conflicts the same way (crypto overrides everything beneath it).
    deciding = next(
        (t for t in _TIER_ORDER
         if any(s.tier == t and s.severity == Severity.FAIL for s in verdict.signals)),
        None,
    )

    rows = []
    for tier in _TIER_ORDER:
        sigs = [s for s in verdict.signals if s.tier == tier]
        fails = [s for s in sigs if s.severity == Severity.FAIL]
        passes = [s for s in sigs if s.severity == Severity.PASS]
        if fails:
            status, cls, icon = "Fail", "fail", "✕"
        elif passes:
            status, cls, icon = "Pass", "pass", "✓"
        else:
            status, cls, icon = "N/A", "na", "–"

        if fails:
            detail = fails[0].message
        elif passes:
            detail = _TIER_ROLE[tier]
        else:
            detail = "Not applicable to this document"

        marker = "<span class='bsx-decided'>Decided here</span>" if tier == deciding else ""
        rows.append(
            f"<div class='bsx-spine-row {cls}'>"
            f"<div class='bsx-spine-tier'>{_TIER_CODE[tier]}</div>"
            f"<div class='bsx-spine-dot {cls}'>{icon}</div>"
            f"<div><div class='bsx-spine-name'>{_TIER_SEQ_LABEL[tier]}{marker}</div>"
            f"<div class='bsx-spine-detail'>{detail}</div></div>"
            f"<div class='bsx-spine-status'>{status}</div>"
            f"</div>"
        )
    return f"<div class='bsx-spine'>{''.join(rows)}</div>"


def _finding_heading(check: str) -> str:
    if check.startswith("crosszone_"):
        return f"Visual field ≠ MRZ: {check[len('crosszone_'):].replace('_', ' ')}"
    if check.startswith("mrz_checksum_"):
        return "MRZ checksum failure"
    if check == "manifest_match":
        return "Signed record modified since intake"
    if check in ("signature_valid", "signature_chain"):
        return "Cryptographic signature invalid"
    if check == "photo_region_anomaly":
        return "Portrait region anomaly"
    if check == "noise_residual_anomaly":
        return "Retouching artifact detected"
    if check == "recapture_anomaly":
        return "Screen / print recapture signature"
    if check == "face_verification":
        return "Biometric mismatch"
    return check.replace("_", " ").title()


def finding_cards_html(verdict: Verdict) -> str:
    """Renders every FAILED signal as a detail card. Only uses detail dict
    keys each check actually documents/tests (crosszone: viz/mrz; manifest:
    changed_fields; face: similarity/threshold) -- never guesses a key a
    detector doesn't promise. Portrait vs. live-capture image comparison is
    NOT rendered here (needs real image bytes) -- see ui/pages.py, which
    renders that via st.image next to this card."""
    from core.types import Severity
    cards = []
    for s in verdict.signals:
        if s.severity != Severity.FAIL:
            continue
        heading = _finding_heading(s.check)
        body = f"<p>{s.message}</p>"
        if s.check.startswith("crosszone_") and "viz" in s.detail and "mrz" in s.detail:
            body += (
                "<div class='bsx-compare-grid'>"
                f"<div class='bsx-compare-cell'><div class='k'>PRINTED (VIZ)</div>{s.detail['viz']}</div>"
                f"<div class='bsx-compare-cell bad'><div class='k'>MRZ ENCODED</div>{s.detail['mrz']}</div>"
                "</div>"
            )
        elif s.check == "manifest_match" and s.detail.get("changed_fields"):
            fields = ", ".join(s.detail["changed_fields"])
            body += f"<div class='bsx-compare-cell bad'><div class='k'>CHANGED SINCE SIGNING</div>{fields}</div>"
        elif s.check == "face_verification" and "similarity" in s.detail:
            body += (
                "<div class='bsx-compare-grid'>"
                f"<div class='bsx-compare-cell bad'><div class='k'>SIMILARITY</div>{s.detail['similarity']:.3f}</div>"
                f"<div class='bsx-compare-cell'><div class='k'>THRESHOLD</div>{s.detail['threshold']:.3f}</div>"
                "</div>"
            )
        cards.append(
            f"<div class='bsx-finding'><div class='bsx-finding-head'>{heading}</div>"
            f"<div class='bsx-finding-body'>{body}</div></div>"
        )
    if not cards:
        return "<p style='color:var(--text-3);font-size:0.85rem;'>No findings -- every tier passed.</p>"
    return "".join(cards)


def _dial_svg(pct: int, hex_color: str, center_value: str, center_label: str,
               aria: str = "") -> str:
    """An instrument dial, not a progress ring: a graduated scale with a
    tick every 5 units (major every 20) and a hairline arc, rather than a
    thick rounded bar. Reads as a measurement taken off a scale, not a
    task-completion meter. The arc draws on entry (ui/style.py .bsx-arc)
    so the value is arrived at rather than asserted."""
    import math
    pct = max(0, min(100, pct))
    score = pct
    cx = cy = 105
    r_arc = 78
    # 270-degree sweep, opening at the bottom -- an instrument face, not a
    # closed circle, so the scale has a visible start and end.
    start_deg, sweep_deg = 135.0, 270.0

    def polar(radius: float, deg: float) -> tuple[float, float]:
        rad = math.radians(deg)
        return cx + radius * math.cos(rad), cy + radius * math.sin(rad)

    def arc_path(radius: float, frac: float) -> str:
        end_deg = start_deg + sweep_deg * frac
        x0, y0 = polar(radius, start_deg)
        x1, y1 = polar(radius, end_deg)
        large = 1 if sweep_deg * frac > 180 else 0
        return f"M {x0:.2f} {y0:.2f} A {radius} {radius} 0 {large} 1 {x1:.2f} {y1:.2f}"

    ticks = []
    for v in range(0, 101, 5):
        deg = start_deg + sweep_deg * (v / 100)
        major = v % 20 == 0
        r_in = r_arc - (11 if major else 6)
        x0, y0 = polar(r_in, deg)
        x1, y1 = polar(r_arc - 2, deg)
        stroke = "var(--outline)" if major else "var(--line)"
        ticks.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
                      f'stroke="{stroke}" stroke-width="1"/>')

    nx, ny = polar(r_arc, start_deg + sweep_deg * (score / 100))
    label = aria or f"{center_value} {center_label}"
    return f"""
    <div class="bsx-ring-wrap"><div class="bsx-ring">
      <svg viewBox="0 0 210 210" role="img" aria-label="{label}">
        <path d="{arc_path(r_arc, 1.0)}" fill="none" stroke="var(--line)" stroke-width="1.5"/>
        {''.join(ticks)}
        <path class="bsx-arc" d="{arc_path(r_arc, score / 100)}" fill="none" stroke="{hex_color}"
              stroke-width="3" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"
              style="--dash-end:0;"/>
        <circle cx="{nx:.2f}" cy="{ny:.2f}" r="4.5" fill="{hex_color}"
                style="animation: bsx-fade 200ms var(--ease-out) 700ms backwards;"/>
      </svg>
      <div class="bsx-ring-score"><div class="n">{center_value}</div><div class="d">{center_label}</div></div>
    </div></div>
    """


def risk_contributions_html(signals: list) -> str:
    from core.types import Severity
    fails = [s for s in signals if s.severity == Severity.FAIL and s.weight > 0]
    if not fails:
        rows = "<p style='color:var(--text-3);font-size:0.85rem;'>No weighted findings.</p>"
    else:
        rows = "".join(
            f"<div class='bsx-contrib-row'><span>{_finding_heading(s.check)}</span>"
            f"<span class='amt'>+{s.weight}</span></div>"
            for s in sorted(fails, key=lambda s: -s.weight)
        )
    total = sum(s.weight for s in fails)
    return (
        f"{rows}<div class='bsx-contrib-total'><span>Total score</span><span class='amt'>{total}</span></div>"
    )


def verdict_hero_html(verdict: Verdict, risk_bands: list | None = None) -> str:
    """The single element allowed to dominate a screen.

    An officer's first question is "what do I do with this person", so the
    action -- not the score -- is set in display type; the numeral is
    large because it must be readable at a glance from outside arm's
    reach, and the band colour is the only saturated thing on the page.
    The scale rail below places the score against the REAL policy.yaml
    cutoffs, never illustrative ones.
    """
    from core.types import Severity
    light = traffic_light(verdict.band)
    cls = _LIGHT_CLASS[light]
    fails = [s for s in verdict.signals if s.severity == Severity.FAIL]

    if verdict.crypto_override:
        why = ("<b>Decided by cryptography, not by a model.</b> A signature or manifest check failed at "
                "tier T0. No forensic or biometric score contributed to this verdict.")
    elif fails:
        why = f"<b>{len(fails)} finding{'s' if len(fails) != 1 else ''}</b> across the Trust Ladder. {fails[0].message}"
    else:
        why = "Every applicable check passed. No findings across any tier of the Trust Ladder."

    rail = risk_scale_rail_html(verdict.score, risk_bands) if risk_bands else ""

    return f"""
    <div class="bsx-verdict" style="--vc:var(--{cls});">
      <div class="bsx-verdict-grid">
        <div>
          <div class="bsx-verdict-num">{verdict.score}</div>
          <div class="bsx-verdict-den">of 100</div>
        </div>
        <div class="bsx-verdict-body">
          <div class="bsx-verdict-band">{verdict.band.value} risk</div>
          <div class="bsx-verdict-action">{verdict.action}</div>
          <div class="bsx-verdict-why">{why}</div>
        </div>
      </div>
      {rail}
    </div>
    """


def risk_scale_rail_html(score: int, risk_bands: list) -> str:
    """risk_bands: policy['risk_bands'] -- [lo, hi, name, action] rows, the
    real cutoffs from policy.yaml. The active band's label is the only one
    at full contrast."""
    active = next((name for lo, hi, name, _ in risk_bands if lo <= score <= hi), None)
    marker_color = _BAND_HEX.get(active, "#6b7683")
    ticks = "".join(f"<div class='bsx-scale-tick' style='left:{hi}%;'></div>"
                     for lo, hi, _, _ in risk_bands[:-1])
    marker = (f"<div class='bsx-scale-marker' style='left:{max(1, min(99, score))}%;"
               f"background:{marker_color};color:{marker_color};'></div>")
    labels = "".join(
        f"<span class='{'on' if name == active else ''}'>{name} {lo}&ndash;{hi}</span>"
        for lo, hi, name, _ in risk_bands
    )
    return (f"<div class='bsx-scale-track'>{ticks}{marker}</div>"
             f"<div class='bsx-scale-labels'>{labels}</div>")


def audit_timeline_html(records: list[dict], limit: int = 8) -> str:
    if not records:
        return "<p style='color:var(--text-3);font-size:0.85rem;'>No events logged yet.</p>"
    items = []
    for i, r in enumerate(reversed(records[-limit:])):
        head_cls = " head" if i == 0 else ""
        ts = r.get("timestamp", "--")
        title = f"Case {r.get('case_id', '?')} screened — {r.get('band', '?')} ({r.get('score', '?')}/100)"
        this_hash = r.get("this_hash", "")
        items.append(
            f"<div class='bsx-timeline-item{head_cls}'><div class='bsx-timeline-dot'></div>"
            f"<div class='bsx-timeline-ts'>{ts}</div>"
            f"<div class='bsx-timeline-title'>{title}</div>"
            f"<div class='bsx-timeline-hash'>HASH: {this_hash[:24]}&hellip;</div></div>"
        )
    return f"<div class='bsx-timeline'>{''.join(items)}</div>"


# ------------------------------------------------------------------------
# Real Document Screening (Mode B) -- pure render functions, same contract
# as the rest of this file: data in, markup out, never touches session
# state or the filesystem. See core/realdoc/pipeline.py for the shapes
# these take (RealDocVerdict, LadderStep, ExtractedField, capabilities dict).
# ------------------------------------------------------------------------

def realdoc_capability_panel_html(capabilities: dict[str, bool]) -> str:
    """Every entry here is True/False for whether that layer applies to
    THIS document at all -- never a pass/fail verdict (that's the ladder's
    job). False therefore always renders neutral/grey ("NOT APPLICABLE"),
    the same way a genuinely inapplicable check should never look like a
    finding: a marksheet's MRZ being N/A is not evidence of anything."""
    chips = []
    for label, ok in capabilities.items():
        cls = "ok" if ok else "na"
        text = f"{label} ✓" if ok else f"{label} ○ NOT APPLICABLE"
        chips.append(f"<span class='bsx-status-dot'><span class='dot {cls}'></span>{text}</span>")
    return f"<div class='bsx-pill-row'>{''.join(chips)}</div>"


_LADDER_DOT = {"VERIFIED": ("pass", "✓", "VERIFIED"), "FAILED": ("fail", "✕", "FAILED"),
               "REVIEW": ("review", "!", "REVIEW"), "NOT_APPLICABLE": ("na", "–", "N/A")}


def realdoc_ladder_html(steps: list) -> str:
    rows = []
    for i, step in enumerate(steps, 1):
        dot_cls, icon, status_txt = _LADDER_DOT.get(step.status, ("na", "–", "N/A"))
        row_cls = {"pass": "", "fail": "fail", "review": "review", "na": "na"}[dot_cls]
        detail = f"<div style='font-size:0.72rem;color:var(--text-3);'>{step.detail}</div>" if step.detail else ""
        rows.append(
            f"<div class='bsx-vseq-row {row_cls}'>"
            f"<div class='bsx-vseq-dot {dot_cls}'>{icon}</div>"
            f"<div class='bsx-vseq-label' style='flex-direction:column;align-items:flex-start;gap:0.1rem;'>"
            f"<div style='display:flex;justify-content:space-between;width:100%;'>"
            f"<span>{i:02d} {step.name}</span><span class='status'>{status_txt}</span></div>"
            f"{detail}</div></div>"
        )
    return f"<div class='bsx-vseq'>{''.join(rows)}</div>"


def realdoc_fields_table_html(fields: dict) -> str:
    """fields: dict[str, core.realdoc.fields.ExtractedField]. Renders every
    field regardless of status -- EXTRACTED, UNCERTAIN and NOT_DETECTED are
    all shown, never silently dropped, so "we didn't find this" stays as
    visible as "we found this"."""
    status_cls = {"EXTRACTED": "green", "UNCERTAIN": "amber", "NOT_DETECTED": ""}
    rows = []
    for key, f in fields.items():
        label = key.replace("_", " ").upper()
        if f.status == "NOT_DETECTED":
            value_html = "<span style='color:var(--text-3);'>NOT DETECTED</span>"
        else:
            pill = f"<span class='bsx-pill {status_cls[f.status]}' style='margin-left:0.5rem;'>{f.status} · {f.confidence}</span>"
            value_html = f"<span class='bsx-field-value'>{f.value}</span>{pill}"
        rows.append(f"<div class='bsx-field-row'><span class='bsx-field-name'>{label}</span>{value_html}</div>")
    return "".join(rows)


def realdoc_evidence_html(signals: list) -> str:
    """Every signal that actually says something -- a real finding (FAIL)
    or an advisory note (a forensic WEAK carrying an "ADVISORY:" message,
    see core/realdoc/pipeline.py::_advisory_only) -- as one card each. A
    clean PASS with nothing to report is not shown: "no evidence" reads as
    an empty, explicitly-labelled list, not a wall of green checkmarks."""
    from core.types import Severity
    cards = []
    for s in signals:
        if s.severity == Severity.PASS:
            continue
        if s.severity == Severity.WEAK and not s.message.startswith("ADVISORY:"):
            continue  # e.g. "no face detected" -- not a finding about the document itself
        tone_cls = "red" if s.severity == Severity.FAIL else "amber"
        card_cls = "" if s.severity == Severity.FAIL else "advisory"
        label = "FINDING" if s.severity == Severity.FAIL else "ADVISORY"
        heading = s.check.replace("realdoc_", "").replace("_", " ").title()
        cards.append(
            f"<div class='bsx-finding {card_cls}'><div class='bsx-finding-head'>"
            f"<span class='bsx-pill {tone_cls}' style='margin-right:0.5rem;'>{label}</span>{heading}</div>"
            f"<div class='bsx-finding-body'><p>{s.message}</p></div></div>"
        )
    if not cards:
        return ("<p style='color:var(--text-3);font-size:0.85rem;'>No findings or advisories -- "
                "every applicable check passed cleanly.</p>")
    return "".join(cards)


def realdoc_confidence_dial_html(steps: list) -> str:
    """Evidence completeness as an instrument dial.

    Deliberately a DIFFERENT quantity from the risk score, and the reason
    the dial survives on this screen while the demo-document case file uses
    a numeral instead: a real document can score LOW simply because little
    was determinable, and that is not the same as scoring LOW because
    everything ran clean. Showing completeness on its own graduated scale
    keeps those two apart. Coloured by the accent, never by a semantic
    hue -- low confidence is not a finding against the document.
    """
    definitive = sum(1 for s in steps if s.status in ("VERIFIED", "FAILED"))
    applicable = sum(1 for s in steps if s.status != "NOT_APPLICABLE")
    pct = round(100 * definitive / applicable) if applicable else 0
    dial = _dial_svg(pct, "var(--primary)", f"{definitive}", f"of {applicable} checks")
    return (f"<div class='bsx-tier-head'>Evidence confidence</div>{dial}"
             f"<p style='color:var(--text-3);font-size:0.78rem;text-align:center;max-width:34ch;"
             f"margin:0.2rem auto 0;line-height:1.5;'>{pct}% of applicable checks reached a definitive "
             f"result. The rest were attempted but inconclusive.</p>")


def realdoc_confidence_html(steps: list) -> str:
    """A simple, honest completeness measure: how many of the ladder's
    steps reached a definitive VERIFIED/FAILED result versus how many
    were REVIEW (attempted, inconclusive) or NOT_APPLICABLE (correctly
    skipped). Distinct from the risk score -- a document can score LOW
    with low confidence (little was actually determinable) just as
    easily as with high confidence (everything ran clean)."""
    definitive = sum(1 for s in steps if s.status in ("VERIFIED", "FAILED"))
    applicable = sum(1 for s in steps if s.status != "NOT_APPLICABLE")
    pct = round(100 * definitive / applicable) if applicable else 0
    return (f"<div class='bsx-stat'><div class='label'>Evidence Confidence</div>"
            f"<div class='value'>{definitive}/{applicable}<span class='sub'>applicable checks reached a "
            f"definitive result ({pct}%)</span></div></div>")


_REALDOC_BAND_HEX = {"LOW": "#4caf7d", "MEDIUM": "#d89b3c", "HIGH": "#d89b3c", "REVIEW": "#878d93"}
_REALDOC_BAND_CLS = {"LOW": "green", "MEDIUM": "amber", "HIGH": "amber", "REVIEW": ""}


def realdoc_verdict_card_html(verdict) -> str:
    """Same verdict-hero language as Mode A (verdict_hero_html), so a real
    document and a demo document produce a visually identical decision --
    an officer never has to learn two result formats. REVIEW renders in
    neutral grey rather than a severity colour: "not enough was
    determinable" is not a finding against the document."""
    hex_color = _REALDOC_BAND_HEX.get(verdict.band, "#6b7683")
    label = f"{verdict.band} risk" if verdict.band != "REVIEW" else "Insufficient evidence"
    return f"""
    <div class="bsx-verdict" style="--vc:{hex_color};">
      <div class="bsx-verdict-grid">
        <div>
          <div class="bsx-verdict-num">{verdict.score}</div>
          <div class="bsx-verdict-den">of 100</div>
        </div>
        <div class="bsx-verdict-body">
          <div class="bsx-verdict-band">{label}</div>
          <div class="bsx-verdict-action">{verdict.action}</div>
          <div class="bsx-verdict-why">Decision support only. A real document cannot reach CRITICAL here
            &mdash; forensic thresholds are calibrated against the synthetic template, so on an arbitrary
            document they are advisory. Final determination remains with the authorized officer.</div>
        </div>
      </div>
    </div>
    """
