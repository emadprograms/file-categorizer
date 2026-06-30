# Phase 3: ai-classification - Context

**Gathered:** 2026-06-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Integrate Gemma Vision to categorize cleaned images. This involves passing the pre-extracted, cleaned images from Phase 2 into the Vision LLM API, prompting it to categorize the page based on dynamically loaded categories (from Phase 1), and tracking the resulting categories per page.

</domain>

<decisions>
## Implementation Decisions

### API Provider & SDK
- **D-01:** Use Google AI Studio via `google-genai` SDK for the Gemma 4 26B Vision endpoint.

### Rate Limiting & Concurrency
- **D-02:** Process pages sequentially enforcing a strict minimum interval of 7 seconds between requests (if a request completes in less than 7 seconds, wait the remainder of the time before making the next). Use the existing per-page progress caching to resume on failure.
- **D-04:** API Error Handling Rules:
  - **429 (Too Many Requests):** Wait 65 seconds before retrying.
  - **500 / 503 (Server Errors):** Wait 15 seconds before retrying.
  - **401 (Unauthorized):** Fail fast immediately and abort the script.

### Prompt & Fallback Strategy
- **D-03:** Require JSON output from the LLM. If the model hallucinates an unknown category that is not in the dynamically provided list, fail the page and retry.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope
- `.planning/PROJECT.md` — Core value, Context, and Constraints.
- `.planning/REQUIREMENTS.md` — Requirements AI-01, AI-02.

### Prior Phases
- `.planning/phases/01-cli-scaffolding/01-CONTEXT.md` — Context about dynamic categories.
- `.planning/phases/02-image-processing/02-CONTEXT.md` — Context about temporary per-page image extraction and `progress.json` cache.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/utils.py`: Contains `load_categories` to get the list of categories.

### Established Patterns
- `src/image_processing.py`: established `process_pdf` using `progress.json` to cache page-level status (`status[page_key] = "success"`).
- `src/cli.py`: establishes error handling and `try-except` wrappers.

### Integration Points
- `src/cli.py` invokes the AI integration immediately after `process_pdf` completes and uses the `tmp_dir` where `page_{num}.png` are stored. Clean up of `tmp_dir` happens AFTER classification and PDF generation.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-ai-classification*
*Context gathered: 2026-06-30*
