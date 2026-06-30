# Project Roadmap

## Proposed Roadmap

**4 phases** | **7 requirements mapped** | All v1 requirements covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | CLI Scaffolding | 1/1 | Complete    | 2026-06-30 |
| 2 | Image Processing | Extract pages from PDF and apply cleaning logic | IMG-01 | 2 |
| 3 | AI Classification | Integrate Gemma Vision to categorize cleaned images | AI-01, AI-02 | 3 |
| 4 | Reporting & Metadata | Save categories to PDF metadata and generate report | OUT-01, OUT-02 | 2 |

### Phase Details

### Phase 1: CLI Scaffolding

**Goal:** Implement CLI to ingest PDFs and parse categories
**Requirements:** CLI-01, CLI-02
**Success criteria:**

1. CLI accepts single or multiple PDF paths as input.
2. CLI accepts a dynamic list of categories via argument and validates them.

### Phase 2: Image Processing

**Goal:** Extract pages from PDF and apply cleaning logic
**Requirements:** IMG-01
**Success criteria:**

1. PDF is successfully split into individual page images.
2. Cleaning logic (division normalization, washout, black-hat filter) runs successfully on each image.

### Phase 3: AI Classification

**Goal:** Integrate Gemma Vision to categorize cleaned images
**Requirements:** AI-01, AI-02
**Success criteria:**

1. Cleaned images are sent to the Gemma 4 26B vision endpoint.
2. Prompt properly instructs the model to select exactly one of the user-provided categories.
3. System reliably parses the classification response for each page.

### Phase 4: Reporting & Metadata

**Goal:** Save categories to PDF metadata and generate report
**Requirements:** OUT-01, OUT-02
**Success criteria:**

1. PDF page metadata is updated with the categorized result.
2. A JSON/CSV report is generated mapping each page to its category.
