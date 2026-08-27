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
