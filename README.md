# BorderShield AI — SIH 2026, PS 26188

**AI-Based Fake Identity & Document Screening System**
Ministry of Home Affairs · Sashastra Seema Bal (SSB) · Category: Software · Theme: Blockchain & Cybersecurity

**Status: working prototype.** All 5 console screens run end-to-end against real generated attacks; 81/81 tests passing. Read this file top to bottom before touching code — it's the fastest path to a running app.

## The one-line thesis

> **Everyone else builds a classifier. We build a trust hierarchy — cryptography decides first, deterministic rules decide second, machine learning only advises and can never condemn a document by itself.**

Three findings drive every design decision here (full sources in `docs/01-RESEARCH.md`):

1. The best industrial forgery detectors score ~26.5% EER on unseen documents. A verdict that depends on a CNN being right is not deployable — ours never does.
2. Generative AI struggles to forge non-Latin scripts convincingly ("Script-Dependent Generative Instability"). Out of scope for this build, but it's why Indian-script documents are a defensive asset, not just a harder case.
3. A model can raise a document for a human to look at. It can never, on its own, tell a human the person in front of them is a fraud. That rule is enforced in code (`core/risk.py`), not just in the pitch deck.

## Quickstart

```powershell
# 1. Environment
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt

# 2. Face-recognition models (OpenCV Zoo, Git-LFS-backed -- raw.githubusercontent.com
#    serves a useless ~130-byte pointer file for these, you need the media host):
mkdir models -Force
Invoke-WebRequest -Uri "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx" -OutFile "models\face_detection_yunet_2023mar.onnx"
Invoke-WebRequest -Uri "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx" -OutFile "models\face_recognition_sface_2021dec.onnx"

# 3. Generate the synthetic document corpus (genuine doc, 3 attacks, crypto signatures)
.\venv\Scripts\python.exe -m synth.passport
.\venv\Scripts\python.exe -m synth.forge
.\venv\Scripts\python.exe -m synth.sign

# 4. Verify the build
.\venv\Scripts\python.exe -m pytest tests/ -q      # expect 81 passed

# 5. Run the console
.\venv\Scripts\python.exe -m streamlit run app.py
```

Open `http://localhost:8501`. Dashboard → **Controlled Attack Simulation** → click any of the 6 buttons. Each one runs a real generated document through the full pipeline and logs a real, hash-chained case — nothing on screen is staged.

## What this is NOT

- **Not a general document scanner.** The pipeline reads one fixed 1000×700 layout (the UTO demo passport template it generates itself) at fixed pixel coordinates. It will not parse a real passport, Aadhaar, PAN, or DL photo — that's explicitly out of scope for this build (see `docs/06-VERIFY-QUEUE.md`). Don't feed it real ID scans expecting a result; it'll just misread the MRZ.
- **Not using real ICAO Passive Authentication or the PKD.** Crypto integrity is a real X.509 chain + real ECDSA signatures, but the trust anchor is our own demo signing authority, not a government's. Labelled everywhere it surfaces in the UI.
- **Not a blockchain.** The audit trail is a hash-chained JSONL file. Real tamper-evidence for in-place edits, honestly documented limitation against tail-truncation (`core/crypto/ledger.py` docstring).

## Architecture — the Trust Ladder

```
T0  Cryptographic signature   decisive BOTH ways   core/crypto/
T1  MRZ + rules + crosszone   decisive AGAINST only core/mrz.py, core/rules/, core/crosszone.py
T2  Forensics (advisory)      caps at HIGH, never CRITICAL alone   core/forensics/
T2  Biometric face match      caps at HIGH, never CRITICAL alone   core/face/
                     ↓
              core/risk.py fuse() → Verdict (score, band, action)
```

Full rationale for the fusion rule (and the two real bugs it took to get right) is in `core/risk.py`'s own docstring — read it before changing anything there.

### Folder map

| Path | What's in it |
|---|---|
| `core/` | The actual pipeline: MRZ/VIZ reading, crosszone, rules engine, forensics, face verification, crypto (PKI + signed manifest + ledger), risk fusion. |
| `synth/` | Generates the synthetic UTO demo document, the 3 forged attacks (DOB edit, portrait swap, screen recapture), and signs everything. |
| `ui/` | Streamlit console. `style.py` = CSS/design tokens, `screens.py` = pure render functions (data in, markup out, never touches session state), `actions.py` = session-state/ledger logic, `pages.py` = per-screen orchestration wiring the two together. |
| `tests/` | 81 tests, run before every commit. |
| `docs/` | Phase-0 research, strategy, architecture, feature backlog, execution plan. Background/rationale, not setup instructions — this README is the setup doc. |
| `reference/` | The Stitch-generated UI reference design the console's visuals are matched to. |
| `data/`, `models/`, `results/` | Gitignored. Generated/downloaded, never committed — `data/pki/` specifically holds real (if demo-only) private keys. |

## The console

5 screens, fixed sidebar nav:

| Screen | Shows |
|---|---|
| **Command Dashboard** | Live stats from the real ledger, the 6-button Attack Wall, recent cases table. |
| **New Screening** | Upload a document + optional live face capture. |
| **Evidence Analysis** | The document (heatmap-boxed if anything failed), a 4-tier verification sequence, one detail card per failed signal with the actual compared values. |
| **Risk Decision** | Score ring, the real policy.yaml band cutoffs, per-signal weight breakdown. |
| **Investigation** | Case summary, decoded MRZ with real per-field checksum status, hash-chained audit trail, chain-integrity verify + tamper-demo utilities. |

### Attack Wall — what each button actually does

| Button | Attack | Tier that catches it |
|---|---|---|
| GENUINE | Untouched document | Everything passes → LOW |
| CHANGE DOB | VIZ date of birth edited, MRZ left alone | T1 crosszone mismatch |
| REPLACE PHOTO | Portrait swapped with a feathered seam | T2 forensics + T0 crypto (impersonation mode) |
| SCREEN RECAPTURE | Real re-encode + moiré/glare simulation | T2 forensics only — routes to review, never CRITICAL |
| FACE MISMATCH | *(disabled — see below)* | T2 biometric |
| BREAK SIGNATURE | Hand-tampers an already-signed manifest | T0 crypto — CRITICAL, zero forensic/biometric input consulted |

### Unblocking FACE MISMATCH

It's disabled because `data/portraits/` is empty and YuNet correctly detects zero faces in the procedural placeholder oval it falls back to. To turn it on:

1. Drop **two real, consenting** face photos (`.jpg`/`.png`, clear frontal shot) into `data/portraits/`.
2. Re-run `python -m synth.passport` — it randomly picks one as the document's baked-in portrait (`synth/passport.py::_load_or_placeholder_portrait`).
3. On the **New Screening** screen, upload the *other* photo as the live capture for a MISMATCH demo (or the same person's second photo for a MATCH demo).

`data/portraits/` is gitignored — real faces never get committed. Don't put anyone's actual passport/Aadhaar/ID scan through this pipeline expecting a real result (see "What this is NOT," above) — it only wants the face crop, not the document.

## Testing

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -q
```

81 tests covering MRZ checksums, crosszone, rules, risk fusion, all 4 forensic detectors, crypto (both self-consistency and impersonation modes, ledger tamper-detection), and the evidence heatmap. Run this before every commit — CI-equivalent until an actual CI is set up.

## Hard rules for this repo

1. **No invented numbers.** Every figure shown anywhere traces to a real file in `results/`, `core/rules/policy.yaml`, or a cited source. Unknown → `[PLACEHOLDER: how to get it]`, never a guess.
2. **No AI attribution** anywhere — commits, code, docs, slides.
3. **Verify before claiming done.** Run it, show the output.
4. All paths/constants come from `config.py`. Never hardcode a path or threshold elsewhere.
5. Nothing goes in a demo or slide that can't be defended live in Q&A.

## Read next

| Doc | What it settles |
|---|---|
| `docs/01-RESEARCH.md` | The evidence base — every claim above, with its source. |
| `docs/02-STRATEGY.md` | Positioning against other AI-assisted teams. |
| `docs/03-ARCHITECTURE.md` | The Trust Ladder in full, module-by-module. |
| `docs/04-FEATURES.md` | Tiered backlog if there's time left after the internal round. |
| `docs/05-EXECUTION.md` | Demo script, role split, jury Q&A prep. |
| `docs/06-VERIFY-QUEUE.md` | Claims not yet independently verified — clear these before any external presentation. |

These docs predate the final scope cut (they still describe an earlier, larger vision); this README and the actual code in `core/`/`ui/` are the current source of truth whenever they disagree.
