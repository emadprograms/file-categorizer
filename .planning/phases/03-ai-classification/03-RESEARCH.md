# Phase 3: AI Classification - Technical Research

**Date:** 2026-06-30
**Phase:** 03-ai-classification

## 1. Technical Strategy & Integration

The core goal of Phase 3 is to integrate the Gemma 4 26B Vision endpoint to classify each cleaned page of the PDF into one of the user-provided categories.

**Integration Point:**
In `src/cli.py`, after the PDF pages are extracted and cleaned (`process_pdf`), the images reside in `tmp_dir`. We will introduce a new module, `src/ai_classification.py`, containing a function (e.g., `classify_pages(tmp_dir, categories)`) to iterate over the successfully cleaned pages, classify them, and update the `progress.json` file with the results. 

## 2. API Endpoint & SDK Usage

We are required to use the `google-genai` SDK.

**Model:** `gemma-4-26b` (or equivalent valid identifier for the Gemma 4 26B Vision endpoint on Google AI Studio).

**Usage Pattern:**
```python
from google import genai
from google.genai import types
from PIL import Image

# Assumes GEMINI_API_KEY is in environment
client = genai.Client()

def classify_image(image_path: str, categories: list[str]) -> str:
    img = Image.open(image_path)
    
    prompt = f"Categorize this document page into exactly one of the following categories: {', '.join(categories)}."
    
    response = client.models.generate_content(
        model='gemma-4-26b',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "object", 
                "properties": {
                    "category": {"type": "string"}
                }, 
                "required": ["category"]
            }
        )
    )
    return response.text
```

## 3. Rate Limiting & Concurrency Architecture

To respect the strict 7-second minimum interval between API requests and handle API errors, we will implement a sequential processing loop with time tracking and a robust backoff strategy.

**Implementation Details:**
- **Time Tracking:** Maintain a `last_request_time` variable. Before initiating an API call, calculate `elapsed = time.time() - last_request_time`. If `elapsed < 7.0`, sleep for `7.0 - elapsed`. Update `last_request_time = time.time()` immediately before the call.
- **Resumability:** Read `progress.json`. For each `page_X`, check its classification status. If it's already marked as `classification_success`, skip it. Update and save `progress.json` immediately after each page is classified.
- **Error Handling & Backoff:**
  Wrap the API call in a `try-except` block. Inspect the exception for HTTP status codes:
  - **429 (Too Many Requests):** `time.sleep(65)` and retry.
  - **500 / 503 (Server Errors):** `time.sleep(15)` and retry.
  - **401 (Unauthorized):** Log a fatal error and `sys.exit(1)` immediately (fail fast).
  - Use a maximum retry count (e.g., 3 retries per page) to avoid infinite loops on persistent 500s or 429s.

## 4. Prompt, JSON Schema, and Fallback Strategy

**JSON Schema Definition:**
We will enforce JSON output using the API's structured output features (if available for the model) or via prompt instructions.

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "description": "The selected category from the allowed list."
    }
  },
  "required": ["category"]
}
```

**Fallback & Validation Strategy (D-03):**
1. Parse the JSON response.
2. Extract the `category` field.
3. Validate that `category` exists in the dynamically provided `categories` list.
4. **Fallback:** If the model hallucinates an unknown category (or returns invalid JSON), treat it as a failure for that page. The system will retry the classification up to the maximum retry limit. If it continually fails, mark the page's classification status as `error` in `progress.json`.

## 5. Updates to Existing Code

1. **`src/cli.py`:**
   - Retrieve API key from environment variables (`GEMINI_API_KEY`).
   - Call `classify_pages(tmp_dir, categories)`.
   - Update `failed_pages` logic to include pages that failed classification.
2. **`src/ai_classification.py` (New File):**
   - Implement the `classify_pages` loop with the rate limiter.
   - Implement the retry logic based on HTTP status codes.
   - Validate JSON and category inclusion.

## Validation Architecture

The validation for this phase will rely on mocking the google-genai SDK to simulate 200, 429, 500, 503, and 401 HTTP errors and ensure the exponential backoff, rate limiting (strict 7s interval), and JSON fallback behavior function correctly.
