---
wave: 1
depends_on: ["01-cli-scaffolding"]
files_modified:
  - requirements.txt
  - src/image_processing.py
  - src/cli.py
autonomous: true
requirements: ["IMG-01"]
---

# Phase 02: Image Processing - Plan

## Goal
Extract pages from the PDF into images and apply cleaning logic (division normalization, washout, black-hat filter) so they are ready for the Vision LLM in the next phase.

## Requirements
- IMG-01

<threat_model>
ASVS Level: 1
Block on: high

Threats:
- **T1:** Processing maliciously crafted PDFs causing memory exhaustion or arbitrary code execution via OpenCV/PyMuPDF.
  - *Mitigation:* We use standard widely-adopted libraries (PyMuPDF, OpenCV). Temp directories `.tmp_[filename]/` isolate the processing context.
- **T2:** Path traversal when creating temporary directories for processing PDFs.
  - *Mitigation:* Ensure PDF filenames are properly sanitized (using `os.path.basename`) before creating temp directories like `.tmp_[filename]/`.
</threat_model>

## Wave 1: Core Processing and Dependencies

<task>
<action>
Add `PyMuPDF`, `opencv-python`, and `numpy` to `requirements.txt`.
</action>
<read_first>
- requirements.txt
</read_first>
<acceptance_criteria>
- `requirements.txt` contains `PyMuPDF`
- `requirements.txt` contains `opencv-python`
- `requirements.txt` contains `numpy`
</acceptance_criteria>
</task>

<task>
<action>
Create `src/image_processing.py`. Implement `extract_and_clean_page(pdf_document, page_num: int, tmp_dir: str)`:
1. Use `pdf_document.load_page(page_num)` to load the page.
2. Apply `matrix = fitz.Matrix(300/72, 300/72)` and `get_pixmap` to extract at 300 DPI.
3. Convert pixmap to OpenCV numpy array.
4. Apply cleaning filters using `cv2` (division normalization, washout, black-hat).
5. Save the cleaned image to `tmp_dir` (e.g. `page_{page_num}.png`).
6. Return the saved image path.

Implement `process_pdf(pdf_path: str, output_dir: str)`:
1. Extract basename of `pdf_path`.
2. Create an isolated temporary directory `.tmp_[basename]` in `output_dir`.
3. Load or create `progress.json` in the temp directory to track `{"page_N": "success/error"}` status for each page.
4. Iterate over pages in the PDF using `fitz.open(pdf_path)`. If a page is already marked "success" in `progress.json`, skip it.
5. If extraction fails, log the error, mark as "error" in `progress.json`, and continue.
6. After the first pass, loop back and retry any pages marked as "error". (D-07)
7. Return a dict with the final status of all pages, and the path to the temp directory.
(Satisfies D-01, D-02, D-03, D-05, D-06, D-07)
</action>
<read_first>
- .planning/phases/02-image-processing/02-CONTEXT.md
</read_first>
<acceptance_criteria>
- `src/image_processing.py` exists and contains imports `fitz`, `cv2`, `numpy`.
- `extract_and_clean_page` uses `fitz.Matrix(300/72, 300/72)`.
- `process_pdf` creates a `.tmp_` directory and a `progress.json` file inside it.
- `process_pdf` contains logic to retry failed pages.
</acceptance_criteria>
</task>

## Wave 2: CLI Integration

<task>
<action>
Update `src/cli.py` to integrate the image processing step. 
1. Import `process_pdf` from `src.image_processing`.
2. In `main()`, for each `pdf_path` in `args.input_pdfs`, check if the final report `[filename]_report.json` exists in `args.output_dir`. If it does, skip the PDF entirely.
3. Otherwise, call `process_pdf(pdf_path, args.output_dir)`.
4. Wrap `process_pdf` in a `try-except` block. If it raises an exception, print the error to `sys.stderr` and continue to the next PDF in the loop.
5. If pages are permanently failed after retries, explicitly append them to the final PDF output filename (e.g., `[filename]_categorized_failed_pages_4_9.pdf`) and delete the temp workspace.
(Satisfies D-04, D-08)
</action>
<read_first>
- src/cli.py
- src/image_processing.py
</read_first>
<acceptance_criteria>
- `src/cli.py` imports `process_pdf`.
- `src/cli.py` checks for the existence of `[basename]_report.json` and skips if it exists.
- A failed PDF processing does not crash the CLI; it proceeds to the next PDF.
</acceptance_criteria>
</task>

## Must Haves

<must_haves>
truths:
  - D-01: System extracts PDF pages to images.
  - D-02: Images are upscaled to 300 DPI using a zoom matrix.
  - D-03: Morphological cleaning filters are applied via OpenCV.
  - D-04: Final JSON output check correctly skips already-processed PDFs.
  - D-05: A per-file `.tmp_` workspace and `progress.json` cache are created.
  - D-06: Processing failures on a single page do not abort the entire PDF.
  - D-07: Failed pages are retried at the end of the PDF.
  - D-08: Smart naming: permanently failed pages are appended to the final output filename, and the temp workspace is deleted after final output is generated.
prohibitions: []
</must_haves>

## Artifacts this phase produces
- `src/image_processing.py`
- Function: `src.image_processing.extract_and_clean_page`
- Function: `src.image_processing.process_pdf`
