---
phase: 02-image-processing
plan: 01
subsystem: processing
tags: [pymupdf, opencv, image processing]

# Dependency graph
requires:
  - phase: 01-cli-scaffolding
    provides: [cli structure, category loading]
provides:
  - PDF to image extraction
  - Image cleaning (division normalization, washout, black-hat filter)
  - CLI integration with skipping logic for existing reports
affects: [03-categorization]

# Tech tracking
tech-stack:
  added: [PyMuPDF, opencv-python, numpy]
  patterns: [temp directory per file, progress state caching]

key-files:
  created: [src/image_processing.py]
  modified: [requirements.txt, src/cli.py]

key-decisions:
  - "D-05: Use isolated temporary directories per PDF file for processing to isolate context."
  - "D-08: Permanently failed pages will append to the target categorized PDF filename."

patterns-established:
  - "Pattern 1: Try-except wrapper on per-page processing to maintain progress and avoid whole-PDF failure."

requirements-completed: [IMG-01]

# Coverage metadata
coverage:
  - id: D1
    description: "PDF to image extraction using PyMuPDF at 300 DPI"
    requirement: "IMG-01"
    verification: []
    human_judgment: true
    rationale: "Requires visual verification that images extracted properly maintain text quality"
  - id: D2
    description: "Image morphological cleaning with washout and black-hat"
    requirement: "IMG-01"
    verification: []
    human_judgment: true
    rationale: "Requires visual verification that diacritics and fine typography are preserved"

# Metrics
duration: 10min
completed: 2026-06-30
status: complete
---

# Phase 02 Plan 01: Core Processing and Dependencies Summary

**Implemented PyMuPDF extraction and OpenCV cleaning pipeline for PDF pages, integrated into CLI with resuming/skipping capabilities**

## Performance

- **Duration:** 10 min
- **Started:** 2026-06-30T09:16:14Z
- **Completed:** 2026-06-30T09:18:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Added PyMuPDF, opencv-python, and numpy to dependencies
- Built `extract_and_clean_page` with division normalization, white point washout, and black-hat filtering
- Built `process_pdf` with per-file temporary `.tmp_` workspaces and `progress.json` for retry logic
- Integrated `process_pdf` into CLI loop with smart skipping for already processed PDFs

## Task Commits

Each task was committed atomically:

1. **Task 1: Core Processing and Dependencies** - `6b5edd7` (feat)
2. **Task 2: Image Processing logic** - `ee4a535` (feat)
3. **Task 3: CLI Integration** - `28d7ef4` (feat)

**Plan metadata:** Pending (docs: complete plan)

## Files Created/Modified
- `requirements.txt` - Added dependencies
- `src/image_processing.py` - Core PDF extraction and OpenCV processing logic
- `src/cli.py` - Integrated processing pipeline and implemented graceful skipping/error handling

## Decisions Made
- Used `fitz.Matrix(300/72, 300/72)` to enforce 300 DPI extraction for all pages to ensure standard behavior in OpenCV filtering.
- Reused `try/except` block structure in `cli.py` loop to avoid a single corrupt PDF crashing the batch.
- Deletion of temporary directory (`shutil.rmtree(tmp_dir)`) is positioned at the end of the `cli.py` loop processing, waiting for Phase 3 logic to consume the images before final deletion.

## Deviations from Plan

None - plan executed exactly as written

## Issues Encountered
None

## Next Phase Readiness
- Image extraction and cleaning is ready.
- Next step: integrate Vision LLM for page categorization (Phase 3).
