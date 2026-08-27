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


def masthead() -> str:
    return (
        "<div class='bsx-eyebrow'>PS 26188 &middot; Ministry of Home Affairs &middot; Sashastra Seema Bal</div>"
        "<div class='bsx-title'>BorderShield AI</div>"
        "<div class='bsx-sub'>Cryptography decides first, deterministic rules decide second, "
        "machine learning only advises. Every document below is a synthetic UTO demo specimen "
        "(permanently watermarked) &mdash; no real travel document is used in this build.</div>"
    )


def verdict_badge(verdict: Verdict) -> str:
    light = traffic_light(verdict.band)
    css_class = {"GREEN": "green", "AMBER": "amber", "RED": "red"}[light]
    return (
        f"<div class='bsx-badge {css_class}'>"
        f"<div class='light'>{light}</div>"
        f"<div class='meta'>{verdict.band.value} &middot; score {verdict.score}/100</div>"
        f"</div>"
    )


def crypto_note(verdict: Verdict) -> str | None:
    if not verdict.crypto_override:
        return None
    return ("<div class='bsx-crypto-note'><b>Decided by cryptography, not a model.</b> "
            "This verdict was forced by a signature/manifest failure in the T0 tier. "
            "No forensic or biometric score was consulted for this decision.</div>")


def evidence_by_tier(verdict: Verdict) -> str:
    by_tier: dict[Tier, list] = {t: [] for t in _TIER_ORDER}
    for s in verdict.signals:
        by_tier.setdefault(s.tier, []).append(s)

    html = []
    for tier in _TIER_ORDER:
        signals = by_tier.get(tier) or []
        if not signals:
            continue
        html.append(f"<div class='bsx-tier-head'>{_TIER_LABEL[tier]}</div>")
        for s in signals:
            icon = _SEVERITY_ICON[s.severity.value]
            html.append(
                f"<div class='bsx-signal {s.severity.value}'>"
                f"<span>{icon}</span>"
                f"<div><div class='check'>{s.check}</div><div class='msg'>{s.message}</div></div>"
                f"</div>"
            )
    return "".join(html)


def ledger_table(records: list[dict], limit: int = 12) -> str:
    if not records:
        return "<p style='color:var(--text-3);font-family:\"IBM Plex Mono\",monospace;font-size:0.85rem;'>No cases screened yet this session.</p>"

    rows = ["<div class='bsx-ledger-row head'><div>CASE</div><div>BAND</div><div>SCORE</div>"
            "<div>ATTACK</div><div>HASH</div></div>"]
    for r in reversed(records[-limit:]):
        band = r.get("band", "?")
        light = {"LOW": "GREEN", "MEDIUM": "AMBER", "HIGH": "AMBER", "CRITICAL": "RED"}.get(band, band)
        short_hash = r.get("this_hash", "")[:10]
        rows.append(
            f"<div class='bsx-ledger-row'>"
            f"<div>{r.get('case_id', '?')}</div>"
            f"<div class='band-{light}'>{light}</div>"
            f"<div>{r.get('score', '?')}</div>"
            f"<div>{r.get('attack_label') or 'genuine'}</div>"
            f"<div class='hash'>{short_hash}&hellip;</div>"
            f"</div>"
        )
    return "".join(rows)


def chain_status(path=None) -> str:
    ok, broken_at = ledger_module.verify_chain(path)
    if ok:
        return "<span class='bsx-ledger-ok'>&#10003; chain intact</span>"
    return f"<span class='bsx-ledger-broken'>&#10007; CHAIN INTEGRITY FAILED at record {broken_at}</span>"


def case_report(case_id: str, doc_name: str, verdict: Verdict, attack_label: str | None) -> str:
    """A compact, printable-style summary of the CURRENTLY ACTIVE case --
    complements ledger_table's list of every past case with the one
    someone is looking at right now. Only failing signals are listed
    (a clean case has nothing to report beyond the verdict itself)."""
    light = traffic_light(verdict.band)
    css_class = {"GREEN": "green", "AMBER": "amber", "RED": "red"}[light]
    findings = [s for s in verdict.signals if s.severity.value == "fail"]

    findings_html = (
        "<ul style='margin:0.3rem 0 0 1.1rem;padding:0;color:var(--text-2);'>"
        + "".join(f"<li>{s.message}</li>" for s in findings)
        + "</ul>"
    ) if findings else "<p style='color:var(--text-3);margin:0.3rem 0 0 0;'>No findings.</p>"

    return f"""
    <div style="border:1px solid var(--line);border-radius:8px;padding:1.1rem 1.3rem;background:var(--surface);">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;letter-spacing:0.1em;
                  text-transform:uppercase;color:var(--text-3);margin-bottom:0.5rem;">
        Case {case_id}
      </div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:0.5rem;">
        <div><b>Document:</b> {doc_name} {f'&middot; attack {attack_label}' if attack_label else ''}</div>
        <div class="band-{light}" style="font-family:'IBM Plex Mono',monospace;font-weight:700;">
          {verdict.score}/100 &middot; {light}
        </div>
      </div>
      <div style="margin-top:0.4rem;"><b>Classification:</b> {verdict.band.value}</div>
      <div style="margin-top:0.4rem;"><b>Findings:</b>{findings_html}</div>
      <div style="margin-top:0.6rem;"><b>Recommended action:</b> {verdict.action}</div>
    </div>
    """


# ============================================================ new screens ===
# Everything below backs the 5-screen sidebar console (ui/pages.py). Same
# contract as above: pure functions, data in, markup out, never touch
# session_state or the filesystem.

_BAND_HEX = {"LOW": "#22c55e", "MEDIUM": "#f59e0b", "HIGH": "#f59e0b", "CRITICAL": "#ef4444"}
_LIGHT_CLASS = {"GREEN": "green", "AMBER": "amber", "RED": "red"}
_LIGHT_PILL_TEXT = {"GREEN": "CLEARED", "AMBER": "REVIEW", "RED": "CRITICAL"}


def sidebar_brand_html() -> str:
    return ("<div class='bsx-sidebar-brand'>"
            "<div class='name'>BORDERSHIELD AI</div>"
            "<div class='sub'>Screening Console</div>"
            "</div>")


def topbar_html(title: str, subtitle: str = "", case_chip: str = "", chain_ok: bool | None = None) -> str:
    chip_html = f"<span class='case-chip'>{case_chip}</span>" if case_chip else ""
    chain_html = ""
    if chain_ok is not None:
        cls, txt = ("ok", "LEDGER INTACT") if chain_ok else ("broken", "CHAIN BROKEN")
        chain_html = f"<span class='bsx-chain-pill {cls}'>{txt}</span>"
    sub_html = f"<div class='sub'>{subtitle}</div>" if subtitle else ""
    return (
        "<div class='bsx-topbar'>"
        f"<div><div class='title'>{title}</div>{sub_html}</div>"
        f"<div class='meta'>{chip_html}{chain_html}</div>"
        "</div>"
    )


def stat_card_html(label: str, value: str, sublabel: str = "", tone: str = "") -> str:
    tone_cls = f" tone-{tone}" if tone else ""
    sub_html = f"<span class='sub'>{sublabel}</span>" if sublabel else ""
    return (
        f"<div class='bsx-stat'><div class='label'>{label}</div>"
        f"<div class='value{tone_cls}'>{value}{sub_html}</div></div>"
    )


def system_status_card_html(pki_ok: bool, chain_ok: bool) -> str:
    def dot(ok: bool, label: str) -> str:
        cls = "ok" if ok else "bad"
        return f"<span class='bsx-status-dot'><span class='dot {cls}'></span>{label}</span>"
    return (
        "<div class='bsx-stat'><div class='label'>System Status</div>"
        f"<div class='bsx-pill-row'>{dot(pki_ok, 'Signing PKI')}{dot(chain_ok, 'Ledger chain')}</div></div>"
    )


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


def verification_sequence_html(verdict: Verdict) -> str:
    from core.types import Severity
    rows = []
    for tier in _TIER_ORDER:
        sigs = [s for s in verdict.signals if s.tier == tier]
        fails = [s for s in sigs if s.severity == Severity.FAIL]
        passes = [s for s in sigs if s.severity == Severity.PASS]
        if fails:
            status, dot_cls = "FAIL", "fail"
        elif passes:
            status, dot_cls = "PASS", "pass"
        else:
            status, dot_cls = "N/A", "na"
        row_cls = {"fail": "fail", "pass": "", "na": "na"}[dot_cls]
        icon = {"fail": "✕", "pass": "✓", "na": "–"}[dot_cls]
        rows.append(
            f"<div class='bsx-vseq-row {row_cls}'>"
            f"<div class='bsx-vseq-dot {dot_cls}'>{icon}</div>"
            f"<div class='bsx-vseq-label'><span>{_TIER_SEQ_LABEL[tier]}</span>"
            f"<span class='status'>{status}</span></div></div>"
        )
    return f"<div class='bsx-vseq'>{''.join(rows)}</div>"


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


def risk_ring_svg(score: int, band) -> str:
    hex_color = _BAND_HEX.get(band.value if hasattr(band, "value") else band, "#909094")
    r, circumference = 78, 2 * 3.14159265 * 78
    offset = circumference * (1 - max(0, min(100, score)) / 100)
    return f"""
    <div class="bsx-ring-wrap"><div class="bsx-ring">
      <svg viewBox="0 0 180 180">
        <circle cx="90" cy="90" r="{r}" fill="none" stroke="var(--surface-highest)" stroke-width="6"/>
        <circle cx="90" cy="90" r="{r}" fill="none" stroke="{hex_color}" stroke-width="6"
                stroke-linecap="round" stroke-dasharray="{circumference:.1f}"
                stroke-dashoffset="{offset:.1f}"/>
      </svg>
      <div class="bsx-ring-score"><div class="n">{score}</div><div class="d">/ 100</div></div>
    </div></div>
    """


def risk_distribution_scale_html(score: int, risk_bands: list) -> str:
    """risk_bands: policy['risk_bands'] -- [lo, hi, name, action] rows,
    real cutoffs from policy.yaml, never the illustrative ones."""
    ticks = "".join(f"<div class='bsx-scale-tick' style='left:{hi}%;'></div>"
                     for lo, hi, _, _ in risk_bands[:-1])
    marker_color = _BAND_HEX.get(next((name for lo, hi, name, _ in risk_bands if lo <= score <= hi), "HIGH"))
    marker = f"<div class='bsx-scale-marker' style='left:{max(1, min(99, score))}%; background:{marker_color};'></div>"
    labels = "".join(
        f"<span>{name} ({lo})</span>" if lo == hi else f"<span>{name} ({lo}-{hi})</span>"
        for lo, hi, name, _ in risk_bands
    )
    return (
        f"<p class='bsx-tier-head' style='margin-top:0;'>Risk distribution scale</p>"
        f"<div class='bsx-scale-track'>{ticks}{marker}</div>"
        f"<div class='bsx-scale-labels'>{labels}</div>"
    )


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


def verdict_footer_html(verdict: Verdict) -> str:
    light = traffic_light(verdict.band)
    cls = _LIGHT_CLASS[light]
    return f"""
    <div class="bsx-card" style="margin-top:0.8rem;">
      <div class="bsx-card-body" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.8rem;">
        <div><div style="font-family:var(--font-body);font-size:0.68rem;font-weight:700;
             text-transform:uppercase;letter-spacing:0.07em;color:var(--text-3);">Risk Implication</div>
             <div style="font-family:var(--font-head);font-weight:700;color:var(--{cls});font-size:1.15rem;">{verdict.band.value}</div></div>
        <div style="text-align:right;"><div style="font-family:var(--font-body);font-size:0.68rem;font-weight:700;
             text-transform:uppercase;letter-spacing:0.07em;color:var(--text-3);">Confidence Score</div>
             <div style="font-family:var(--font-mono);font-size:1.3rem;color:var(--{cls});">{verdict.score}/100</div></div>
      </div>
      <div style="margin:0 1rem 1rem 1rem;padding:0.75rem 1rem;background:var(--{cls}-bg);
           border:1px solid var(--{cls}-dim);border-radius:var(--radius);color:var(--{cls});
           font-family:var(--font-body);font-weight:600;text-align:center;font-size:0.85rem;
           text-transform:uppercase;letter-spacing:0.03em;">{verdict.action}</div>
    </div>
    """


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
