# Requirements

## v1 Requirements

### Core Processing
- [ ] **CLI-01**: User can ingest single or multiple PDF files via command line.
- [ ] **CLI-02**: User can pass user-defined categories via command-line arguments at runtime.
- [ ] **IMG-01**: System converts PDF pages to images and applies cleaning logic (division normalization, washout, black-hat filter).
- [ ] **AI-01**: System passes cleaned images to the Gemma 4 26B vision endpoint.
- [ ] **AI-02**: System prompts the model to categorize each page exactly into one of the provided categories.
- [ ] **OUT-01**: System injects the resulting category into the original (or cleaned) PDF's page metadata.
- [ ] **OUT-02**: System generates a JSON/CSV report mapping each page to its category.

## v2 Requirements (Deferred)
(None)

## Out of Scope
- [ ] Extracting text using OCR prior to LLM — Passing images directly to the vision model avoids intermediate data corruption on Arabic text.
- [ ] Web UI or graphical interface — Requested specifically as a CLI tool for batch processing.
- [ ] Hardcoded categories — Must be dynamically ingested to handle varying document types.

## Traceability
(To be updated by roadmap)
