# SIH 2026 — PS 26188: AI-Based Fake Identity & Document Screening System

**Organisation:** Ministry of Home Affairs · Sashastra Seema Bal (SSB), Police II Division
**Category:** Software · **Theme:** Blockchain & Cybersecurity
**Status:** Phase 0 (research complete) → Phase 1 (spec + idea PPT)

---

## The one-line thesis

> **Everyone else will build a classifier. We build a trust hierarchy — cryptography first, deterministic rules second, machine learning last and never load-bearing — running offline on a handheld at an open land border.**

## Why this wins

Three findings from the 2026 literature drive every decision in this repo:

1. **The best industrial systems in the world get ~26.5% EER on unseen ID documents.**
   (Third Competition on Document Forgery Detection, 2026 — Incode, open-set Track 2.)
   Any SIH team claiming 99% accuracy has overfit. A border system whose verdict depends on a CNN is not deployable. Ours doesn't.

2. **Generative AI cannot reliably forge non-Latin scripts** — "Script-Dependent Generative Instability" (SDGI), documented for Chinese and Tamil.
   Devanagari is the hardest case. Indian and Nepali documents are therefore a *defensive asset*, not a handicap. Nobody else will exploit this.

3. **SSB does not guard an airport. It guards a 1,751 km open border** where Indians and Nepalis cross without passport or visa, tens of thousands daily.
   Every competing team will demo a passport upload on a laptop with Wi-Fi. We demo a handheld in airplane mode at Raxaul.

## Read in this order

| Doc | What it settles |
|---|---|
| [01-RESEARCH.md](docs/01-RESEARCH.md) | The evidence base. Every number, with its source. |
| [02-STRATEGY.md](docs/02-STRATEGY.md) | Positioning, the five theses, what beats the other AI-assisted teams. |
| [03-ARCHITECTURE.md](docs/03-ARCHITECTURE.md) | The Trust Ladder. Modules, fusion rule, stack. |
| [04-FEATURES.md](docs/04-FEATURES.md) | Tiered backlog: TABLE-STAKES / EDGE / WOW, with effort and risk. |
| [05-EXECUTION.md](docs/05-EXECUTION.md) | Calendar, 6-person role split, demo script, PPT outline, jury Q&A prep. |
| [06-VERIFY-QUEUE.md](docs/06-VERIFY-QUEUE.md) | Claims NOT yet verified. Clear these before the PPT ships. |

## Hard rules for this repo

1. **No invented numbers.** Every figure in the PPT or paper traces to a file in `results/` or a cited source. Unknown → `[PLACEHOLDER: how to get it]`.
2. **No AI attribution** anywhere — commits, code, slides, report.
3. **Verify before claiming done.** Show the output.
4. Nothing goes in a slide that we cannot demo or defend in Q&A.
