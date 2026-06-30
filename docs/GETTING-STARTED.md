<!-- generated-by: gsd-doc-writer -->
# Getting Started

## Prerequisites

- Python 3.8 or higher.
- Ensure you have pip installed for dependency management.

## Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/File-Categorizer.git
   ```
2. Navigate into the project directory:
   ```bash
   cd File-Categorizer
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to add your actual API key.*

## First Run

Run the CLI tool with a sample PDF and a categories file:

```bash
python src/cli.py -i sample.pdf -c categories.txt
```

## Common Setup Issues

- **Missing API Key**: If you forget to configure the `.env` file, the AI classification step will fail with an authentication error. Make sure `GEMINI_API_KEY` is present.
- **Dependency Issues**: If some packages like `PyMuPDF` or `opencv-python` fail to install due to system-level missing binaries, ensure your system has the standard C++ build tools installed.

## Next Steps

- Check out [DEVELOPMENT.md](DEVELOPMENT.md) for local development workflows.
- View [TESTING.md](TESTING.md) to understand how to run tests.
