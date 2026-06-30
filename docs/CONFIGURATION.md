<!-- generated-by: gsd-doc-writer -->
# Configuration

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | (none) | API key for the Vision Model (e.g. Gemma 4) used in AI classification |

## Config File Format

This project currently relies exclusively on environment variables and CLI arguments for configuration. There is no external configuration file (JSON/YAML/TOML).

## Required vs Optional Settings

- **`GEMINI_API_KEY`**: **Required**. Missing this setting will cause the AI classification step to fail when connecting to the vision model API.

## Defaults

- **Vision Model**: By default, the CLI uses the `gemma-4-26b` model. This can be overridden using the `-m` CLI argument.

## Per-environment Overrides

No specific per-environment overrides are defined (e.g. `.env.production`). Set environment variables directly in the environment executing the CLI application.
