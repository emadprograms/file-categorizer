<!-- generated-by: gsd-doc-writer -->
# Development

## Local Setup

To set up the project for development:
1. Clone the repository.
2. It's recommended to create a virtual environment (`python -m venv venv` and `source venv/bin/activate`).
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and fill in required values like `GEMINI_API_KEY`.

## Build Commands

| Command | Description |
|---------|-------------|
| `python src/main.py` | Runs the main CLI script directly (no build step needed). |

## Code Style

No specific linting or formatting tools (like flake8 or black) are currently configured. Standard PEP-8 guidelines are recommended.

## Branch Conventions

No branch naming conventions are documented. Please use descriptive branch names (e.g., `feat/add-new-model`, `fix/ocr-bug`).

## PR Process

- Create a feature branch from `main`.
- Ensure tests pass before opening a Pull Request.
- Request review from maintainers.
