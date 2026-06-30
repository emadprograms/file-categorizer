# Phase 3: ai-classification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-30
**Phase:** 03-ai-classification
**Areas discussed:** API Provider & SDK, Rate Limiting & Concurrency, Prompt & Fallback Strategy

---

## API Provider & SDK

| Option | Description | Selected |
|--------|-------------|----------|
| Google AI Studio (via google-genai SDK) | Google AI Studio | ✓ |
| Google Cloud Vertex AI | Vertex AI | |
| HuggingFace Inference API | HuggingFace | |
| Local execution (e.g. Ollama) | Local | |

**User's choice:** Google AI Studio (via google-genai SDK)
**Notes:** User selected Google AI Studio

---

## Rate Limiting & Concurrency

| Option | Description | Selected |
|--------|-------------|----------|
| Process sequentially with a delay between requests | Sequential w/ delay | ✓ |
| Process concurrently (e.g. ThreadPoolExecutor) with exponential backoff and retries | Concurrent w/ backoff | |
| Process sequentially without delay, fail fast on rate limit | Sequential fail fast | |

**User's choice:** Process sequentially with a delay between requests
**Notes:** User selected sequential processing

---

## Prompt & Fallback Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| JSON output (use structured outputs if available) and map unknown categories to "Uncategorized" | JSON output, map unknown | |
| JSON output, but fail the page and retry if category is unknown | JSON output, fail and retry | ✓ |
| Raw text output (extract string), map unknown to "Uncategorized" | Raw text output, map unknown | |

**User's choice:** JSON output, but fail the page and retry if category is unknown
**Notes:** User selected JSON output with fail and retry

---

## the agent's Discretion

None

## Deferred Ideas

None
