# Arabic PDF OCR & Categorization CLI

## What This Is

A Command Line Interface (CLI) tool for batch processing Arabic PDF documents. It cleans the PDFs to improve OCR readability using division normalization and diacritic boosting, then passes the cleaned images directly to a Vision Model (Gemma 4 26B). The model categorizes each page based on user-provided categories at runtime, and the results are saved both to the PDF's page metadata and to a separate JSON/CSV report.

## Core Value

Accurately pre-process and classify degraded Arabic documents (poor contrast/watermarks) into user-defined categories without losing fine typography.

## Requirements

### Validated

- ✓ Image cleaning logic (green channel extraction, division normalization, white point washout, black-hat filter) — inherited from prior research.

### Active

- [ ] CLI scaffolding for batch processing PDFs.
- [ ] Mechanism to ingest categories via command-line arguments at runtime.
- [ ] Apply image cleaning to each page in the PDF.
- [ ] Integrate with Vision LLM (Gemma 4 26B) endpoint to classify each page using the cleaned image.
- [ ] Update PDF page metadata with the classification result.
- [ ] Generate JSON/CSV report mapping pages to their categories.

### Out of Scope

- [ ] Extracting text using OCR prior to LLM — we are passing images directly to a vision model.
- [ ] Web UI or graphical interface — explicitly requested as a CLI tool for batch processing.
- [ ] Hardcoded categories — categories must be provided dynamically at runtime.

## Context

- Built upon findings from `2_arabic_document_ocr_study`.
- The model requires specific image preprocessing (White Point 200-220, black-hat filter) to avoid data loss on fine Arabic typography and diacritics.
- Aggressive cleaning was shown to erase important ink strokes and trigger internal errors, so gentle washout with morphological filtering is strictly required.

## Constraints

- **Tech Stack**: Python CLI application.
- **AI Model**: Must interface directly with a Vision Model (e.g., Gemma 4 26B endpoint) using image inputs.
- **Output Requirements**: Must produce both modified PDFs (metadata injected) and structured reports.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| CLI Interface | Batch processing efficiency and automation | — Pending |
| Direct Vision Classification | Passing cleaned images directly avoids intermediate OCR text corruption | — Pending |
| Runtime Category Args | Provides maximum flexibility for users to define sets without changing code | — Pending |
| Dual Output (Metadata + Report) | Satisfies both archival (metadata) and data-pipeline (JSON/CSV) use cases | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-30 after initialization*
