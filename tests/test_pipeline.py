"""End-to-end pipeline acceptance tests: the actual Attack Wall, run
through core.pipeline.screen_document exactly as the Streamlit app and the
CLI both call it. This is deliberately an integration test, not a unit
test -- it is what caught the real risk_bands boundary bug (a single
25-point forensic FAIL landed on the LOW/MEDIUM boundary and reported
"no action required"), because the isolated calibration scripts run
against each detector never exercised the fused verdict at all.

Requires: python -m synth.passport && python -m synth.forge to have been
run first (both write into data/, which is gitignored).
"""
import pytest

from config import PATHS
from core.pipeline import screen_document
from core.types import Band

GENUINE = PATHS["documents"] / "demo_0001.png"
ATTACK_A = PATHS["forged"] / "forged_demo_0001_A.png"
ATTACK_B = PATHS["forged"] / "forged_demo_0001_B.png"
ATTACK_C = PATHS["forged"] / "forged_demo_0001_C.png"

pytestmark = pytest.mark.skipif(
    not GENUINE.exists(), reason="run `python -m synth.passport && python -m synth.forge` first"
)


def test_genuine_document_is_low():
    verdict, _ = screen_document(GENUINE)
    assert verdict.band == Band.LOW
    assert verdict.score == 0


def test_dob_forgery_is_critical_via_crosszone():
    verdict, _ = screen_document(ATTACK_A)
    assert verdict.band == Band.CRITICAL
    failed_checks = {s.check for s in verdict.signals if s.severity.value == "fail"}
    assert "crosszone_date_of_birth" in failed_checks


def test_portrait_replacement_is_amber_not_red():
    """Forensics-only evidence (no rules/crosszone violation) must never
    reach CRITICAL -- this is the fusion invariant from core/risk.py,
    exercised here against a real attack rather than a synthetic Signal."""
    verdict, _ = screen_document(ATTACK_B)
    assert verdict.band in (Band.MEDIUM, Band.HIGH)
    assert verdict.band != Band.CRITICAL
    failed_checks = {s.check for s in verdict.signals if s.severity.value == "fail"}
    assert "photo_region_anomaly" in failed_checks


def test_screen_recapture_is_amber_not_red():
    verdict, _ = screen_document(ATTACK_C)
    assert verdict.band in (Band.MEDIUM, Band.HIGH)
    assert verdict.band != Band.CRITICAL
    failed_checks = {s.check for s in verdict.signals if s.severity.value == "fail"}
    assert "recapture_anomaly" in failed_checks


def test_no_verdict_signal_is_ever_an_accusation():
    accusatory = ["fraud", "criminal", "fake", "liar", "guilty"]
    for path in (GENUINE, ATTACK_A, ATTACK_B, ATTACK_C):
        verdict, _ = screen_document(path)
        lowered = verdict.action.lower()
        assert not any(w in lowered for w in accusatory), (path, verdict.action)
