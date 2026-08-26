"""Evidence fusion: the Trust Ladder's decision rule, and the reason this
system is safe to deploy despite the field's published error rates (see
docs/01-RESEARCH.md -- the best industrial document-forgery detector
scores 26.52% EER on unseen documents).

This is NOT a single additive score banded into a verdict. Tier is
decisive, not just heavily weighted -- exactly the Trust Ladder principle
in docs/03-ARCHITECTURE.md:

  T0 crypto      -- decisive BOTH ways. Invalid signature forces CRITICAL
                    regardless of everything else; valid signature plus a
                    clean T1 is the strongest clearance this system gives.
  T1 rules       -- decisive AGAINST only. Any failure here (an MRZ
                    checksum, a cross-zone mismatch, an expiry violation)
                    forces CRITICAL on its own. A forger who gets the
                    pixels right but breaks a rule does not get partial
                    credit for the pixels.
  T2 forensics / -- ADVISORY ONLY. These signals still count -- they set
     biometric      the band among LOW/MEDIUM/HIGH -- but they can never
                    push a document past HIGH by themselves. A model can
                    raise a document for a human to look at; it can never
                    condemn one alone.

An earlier version of this module scored everything as one additive total
and banded it (the illustrative weights sketch in the plan). That fails
its own acceptance test: a single cross-zone mismatch (weight 25) lands
inside the LOW band (0-25) under plain addition, which is the opposite of
"decisive against". Tier-first branching, not a weight tuned to dodge a
boundary, is the actual fix.

The recommended-action text is never an accusation, at any band -- see
policy.yaml and the language rule in docs/02-STRATEGY.md.
"""
from __future__ import annotations

from core.rules.engine import load_policy
from core.types import Band, Severity, Signal, Tier, Verdict

_ADVISORY_TIERS = {Tier.FORENSICS, Tier.BIOMETRIC}
_DECISIVE_TIERS = {Tier.RULES}  # crypto handled separately via crypto_valid


def _band_for_score(score: int, policy: dict) -> tuple[Band, str]:
    for lo, hi, name, action in policy["risk_bands"]:
        if lo <= score <= hi:
            return Band(name), action
    return Band.HIGH, "Secondary inspection recommended"


def fuse(signals: list[Signal], crypto_valid: bool | None = None, policy: dict | None = None
          ) -> Verdict:
    """crypto_valid: None if no cryptographic tier was evaluated at all
    (e.g. no chip/signed manifest presented); True/False if it was."""
    policy = policy or load_policy()
    fails = [s for s in signals if s.severity == Severity.FAIL]
    raw_score = max(0, min(100, sum(s.weight for s in fails)))

    if crypto_valid is False:
        return Verdict(score=100, band=Band.CRITICAL,
                        action="Secondary inspection recommended",
                        signals=signals, crypto_override=True)

    decisive_failed = any(s.tier in _DECISIVE_TIERS for s in fails)
    if decisive_failed:
        return Verdict(score=max(raw_score, 76), band=Band.CRITICAL,
                        action="Secondary inspection recommended",
                        signals=signals, crypto_override=False)

    if crypto_valid is True:
        # cryptographic proof, and nothing decisive failed: the strongest
        # clearance this system gives.
        return Verdict(score=0, band=Band.LOW, action="No action required",
                        signals=signals, crypto_override=False)

    # Nothing decisive at all (no crypto tier, no rules failure): only
    # advisory (forensics/biometric) evidence remains. Band it normally,
    # but it is structurally incapable of reaching CRITICAL -- that band
    # is reserved for a decisive failure, never for a model's opinion.
    band, action = _band_for_score(raw_score, policy)
    if band == Band.CRITICAL:
        band, action = Band.HIGH, "Secondary inspection recommended"
    return Verdict(score=raw_score, band=band, action=action, signals=signals,
                    crypto_override=False)


_TRAFFIC_LIGHT = {Band.LOW: "GREEN", Band.MEDIUM: "AMBER", Band.HIGH: "AMBER", Band.CRITICAL: "RED"}


def traffic_light(band: Band) -> str:
    return _TRAFFIC_LIGHT[band]
