# BorderShield AI — Current State (baseline for the final build)

**Written:** 2026-08-30. **Updated:** 2026-09-10. **Status:** working prototype, selected for the next round. 169/169 automated tests passing. Live at the deployed URL and runnable on localhost.

This is a snapshot of exactly what exists today — every screen, every button, what's real, what's disabled, what's not built. Use it as the starting point for planning the final-round build. It is **not** a roadmap or a Q&A doc — for those, see `docs/team/dossier.html` (answers to judge questions) and `docs/team/run-of-show.html` (the demo script).

---

## What changed since 2026-08-30 (read this before the team meeting)

The biggest gap in the old snapshot — **"was this document actually issued by the government?"** — is closed. A real **Synthetic Issuer Registry** (SQLite, cryptographically signed, honestly labelled as demo/synthetic everywhere it surfaces) now exists, with a pluggable interface a real government connector could drop into later with no code changes elsewhere.

- **2 new Trust Ladder tiers**: T1 Issuer Provenance (decisive against, same authority as Rules), T2 Identity Continuity (advisory, flags one biometric reference tied to multiple registry identities).
- **7 new Attack Wall scenarios** (13 total, up from 6) — several with a document that's *pixel-perfect and still gets caught*, because the registry disagrees with it.
- **The audit ledger's one disclosed gap is closed**: it used to only catch in-place edits, not someone deleting the newest record(s). Now every write signs a `{record_count, tail_hash}` checkpoint, so deletion is caught too.
- **Case File / Audit Trail** gained JSON export buttons, and Case File gained "why is this required?" citations (real external standards where one applies, honest "our own policy" where it doesn't).
- **New Screening (Real Document mode)** gained an optional second-document upload to cross-check date of birth between two independently-issued real documents.
- **A real portability bug was caught and fixed**: a genuinely fresh clone would have scored the untouched genuine document CRITICAL (signature keys don't travel with git). Confirmed by actually simulating a fresh machine, then fixed — the app now self-heals its demo signatures on startup. Already on `master`.
- Tests: **108 → 169**.

Full detail below.

---

## 1. The six screens

Fixed sidebar nav, same order top to bottom. Nothing else exists outside these six — no hidden pages, no half-built screens.

### Overview (`ui/pages.py::render_landing`)
**Purpose:** the front page. Explains the idea before showing any live data. **Unchanged** since the last snapshot.

| Element | What it does |
|---|---|
| Hero text | Static copy — the one-line thesis and a short explanation. |
| Trust Ladder diagram | Static explanation of the tiers and their authority order. Same on every load. |
| **"Open screening command" button** | Navigates to Command Center. |
| **"Screen a document" button** | Navigates to New Screening. |
| "What this is not" section | Static honesty block — synthetic data, demo signing authority, hash-chain not blockchain. |

### Command Center (`render_dashboard`)
**Purpose:** operational hub. Proof the system is live + one-click demo attacks.

| Element | What it does |
|---|---|
| **5 status cards** (was 4) | Biometric models, Signing PKI, **Issuer Registry (new)** — live record count and status breakdown (e.g. "12 records · 7 active · 2 revoked · 1 stolen · 1 expired · 1 invalid"), Ledger chain, Cases logged. All real, read live. |
| **13 scenario cards** (was 6) | Each is a real button. Click → builds a synthetic document, runs it through the actual pipeline, logs a real case, jumps to Case File. |
| — SCN_01 Genuine document | **Works.** Clean pass, LOW/0. |
| — SCN_02 Change of birth date | **Works.** VIZ/MRZ mismatch → Rules tier catches it → CRITICAL. |
| — SCN_03 Replace the portrait | **Works.** Caught by forensics AND the signed-manifest check. |
| — SCN_04 Screen recapture | **Works.** Forensics-only signal → AMBER, never RED. |
| — SCN_05 Face mismatch | **Disabled.** Needs a second, different real person's consenting photo — not on file. Tooltip explains why. |
| — SCN_06 Break the signature | **Works.** Hand-tampers an already-signed record; signature fails; CRITICAL, zero AI/forensic input. |
| — SCN_07 Unregistered document | **New. Works.** Document number the registry has never heard of — reported as "issuance could not be established", never as fake. |
| — SCN_08 Perfect document, revoked | **New. Works. The standout demo.** Crypto, Rules, Forensics, Identity all pass cleanly — nothing is forged. Only the registry says this document was revoked after issue. CRITICAL, "Issuer Provenance — decided here." |
| — SCN_09 Stolen document | **New. Works.** Self-consistent, cleanly signed — registry marks it STOLEN. CRITICAL, same reasoning as revoked. |
| — SCN_09B Registry record expired | **New. Works.** Document's own printed dates are current; only the *registry's* record is EXPIRED. |
| — SCN_09C Registry record invalid | **New. Works.** Distinct from revoked — never validly standing to begin with. |
| — SCN_10 Valid number, wrong identity | **New. Works.** Real, active document number, printed under a different name/DOB than the registry has on file. Nothing about the document itself is broken. |
| — SCN_11 Same person, multiple identities | **New. Works.** This document's own record is clean; its biometric reference is *also* on record under a different name/number. Advisory only, capped at HIGH. |
| Registry integrity demo | **New.** "Simulate registry tampering" button — hand-edits a scratch copy of the registry (a REVOKED record flipped back to ACTIVE without a valid signature), shows integrity check catching it. Never touches the real committed registry. |
| Recent cases table | Real. Every case run this session. |

### New Screening (`render_capture`)
**Purpose:** bring your own document instead of a canned Attack Wall button. Two modes.

**Mode A — Demo Document:** unchanged. PNG upload, exactly 1000×700, optional live face capture, "Screen this document" runs the real pipeline.

**Mode B — Real Document** (`_render_real_document_capture`):

| Element | What it does |
|---|---|
| File uploader (PNG/JPG/JPEG/PDF) | Accepts any identity or educational document. |
| Manual portrait-region override | Draw a bounding box by hand if auto-detection misses the photo. |
| Live camera / face-photo uploader | Optional, for biometric comparison. |
| **"Optional: cross-check date of birth against a second document" (new)** | Upload a *second*, different real document (e.g. a marksheet alongside a passport). If both confidently read a date of birth, the two are compared — agreement is real corroborating evidence, disagreement is a real finding. Reuses the same fusion logic, doesn't touch the single-document path. |
| **"Screen this document" button** | Runs OCR, classification, rule checks, forensics, biometric (if given), cross-document (if a second file given). Result renders inline — not logged to the ledger (privacy). |
| Result: two-column verdict | "What we established" vs "What we could not establish" — never "genuine", always "No adverse signals" when clean. |

### Case File (`render_case`)
**Purpose:** the full result of one screening.

| Element | What it does |
|---|---|
| Verdict hero | Score /100, band, recommended action. |
| Crypto note | Appears when a signature/manifest check forced the verdict. |
| Document image | Flagged regions boxed if anything failed. |
| Portrait comparison | Shown only if a portrait-related check failed. |
| **Trust ladder — 6 rows now** (was 4) | Crypto, Rules, **Issuer Provenance (new)**, Forensics, Biometric, **Identity Continuity (new)**. Each row: `Checks:` (constant question) + `This case:` (actual result). |
| Findings | Only what actually failed, plain-English first, technical wording behind a toggle. |
| Score contributions | Bar per weighted finding + total, with a note when a hard override decided the verdict. |
| Pipeline log | Full line-by-line technical trace. |
| Machine-readable zone | Raw MRZ text + per-field checksum pills. |
| Extracted identity | Document number, nationality, expiry. |
| **Issuer registry (new)** | What the registry lookup found for this document — status, fields compared, match/mismatch per field. |
| **Identity continuity (new)** | Whether this credential's biometric reference appears on any other registry record. |
| **"Why is this required?" links (new)** | Real external-standard citation (ICAO Doc 9303) where one genuinely applies; an honest "this is our own policy" where it's a project decision, never an invented citation. |
| **Export (new)** | "Export case report (JSON)" — downloads the full case as a JSON file. |

### Audit Trail (`render_audit`)
**Purpose:** the tamper-evident ledger across every case run this session.

| Element | What it does |
|---|---|
| Chain events list | Last 12 cases, each with its hash fingerprint. |
| Integrity status | **Now two pills**: "Audit ledger — intact" (in-place edits) AND **"No truncation detected" (new)** — a second, independent check. |
| "What this proves" box | Now states three things: catches in-place edits, catches deletion of the newest record(s) via a signed checkpoint, and — still — proves nothing about document authenticity. |
| **"Re-verify chain" button** | Re-runs both integrity checks. |
| **"Simulate tampering with a past case" button** | Hand-edits the oldest record's band — the chain shows broken from that point. |
| **"Simulate truncation (delete newest record)" button (new)** | Deletes the newest record outright. The hash chain alone would look fine — this is the exact attack the old snapshot listed as an open gap. The signed checkpoint catches it. **Good demo pairing with the tampering button** — show both, in that order, to make the "closed the gap" story land. |
| **"Reset ledger" button** | Deletes all logged cases. |
| **Export (new)** | "Export ledger (JSON)" — downloads every record as stored. |

### System Status (`render_status`)
**Purpose:** proof nothing is faked, for a technical reviewer. Still **4 engine cards** at the top (Biometric, Cryptographic, Ledger chain, Test suite — unchanged) — the registry doesn't get a 5th card here, but:

| Element | What it does |
|---|---|
| **Issuer registry — full contents (new)**, at the bottom of the page | Every registry record, read directly off `data/registry/registry.db` — not a mock table. **Search box** filters by name, document number, or person ID live. |

---

## 2. What's disabled or not built (be upfront about these)

| Item | State | Why |
|---|---|---|
| **Face Mismatch demo (SCN_05)** | Disabled button | Needs a second, different, consenting person's real photo — not on file. Live face MATCH is verified working elsewhere. |
| **Real government registry connection** | Not built, by design | The Synthetic Issuer Registry is architecturally real (signed, pluggable) but its data is our own — not UIDAI, DigiLocker, or Passport Seva. Labelled everywhere. |
| **Real Document mode → Cryptographic check** | Always NOT APPLICABLE | An arbitrary uploaded document has no registered demo signature. |
| **Real Document mode → results in the audit ledger** | Not logged | Privacy — real documents are never written to disk or the ledger. |
| **ELA (Error Level Analysis) forensic check** | Shown, never scored | Known-unreliable technique, included and labelled as such, never contributes to the risk score. |
| **General document scanning (Mode A)** | Out of scope | Mode A reads the exact 1000×700 UTO template layout only. Mode B is the general path. |

**Closed since the last snapshot** (no longer belong on this list): Issuer authenticity checking, ledger tail-truncation detection.

---

## 3. Test coverage & deployment

- **169 automated tests**, all passing: 46 MRZ, 26 Real Document mode, 19 crypto, 37 issuer registry, 10 cross-document, 8 risk fusion, 6 pipeline, 5 face, 5 standards citations, 4 heatmap, 3 export.
- **Deployed** on Streamlit Community Cloud. Auto-redeploys on every push to `master`.
- **Runs on localhost** with `git clone` → `venv` → `pip install -r requirements.txt` → `streamlit run app.py`. No manual downloads.

## 4. Tech stack, in one line each

- **App/UI:** Python, Streamlit
- **Computer vision:** OpenCV, ONNX Runtime (YuNet + SFace, OpenCV Zoo)
- **OCR (Mode B):** RapidOCR
- **PDF:** PyMuPDF
- **Cryptography:** Python `cryptography` library — real X.509 certs, ECDSA P-256, now also signing the registry manifest and the ledger's truncation checkpoint
- **Registry:** SQLite (`core/issuer/`), behind a `Protocol` interface a real connector could replace
- **Policy:** `core/rules/policy.yaml` — every weight/rule is config

---

*For the "why" behind any of this (architecture, cryptography, scoring, rehearsed answers to hard questions), see `docs/team/dossier.html`. For the live demo script, see `docs/team/run-of-show.html` — note it hasn't been fully re-walked against the 13-scenario Command Center yet; the "Perfect document, revoked" and "Simulate truncation" moments above are strong additions to that script.*
