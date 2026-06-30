<!-- generated-by: gsd-doc-writer -->
# Arabic PDF OCR & Categorization CLI

A Command Line Interface (CLI) tool for batch processing Arabic PDF documents, enhancing OCR readability, and categorizing pages using a Vision Model (Gemma 4 26B).

## Installation

```bash
git clone https://github.com/your-username/File-Categorizer.git
cd File-Categorizer
pip install -r requirements.txt
```

## Quick Start

1. Create a `categories.txt` file or use a comma-separated list of categories.
2. Run the CLI tool on your PDF files:

```bash
python src/main.py -i input.pdf -c categories.txt --instructions instructions.txt
```

## Usage Examples

**Process multiple PDFs and specify an output directory:**
```bash
python src/main.py --input-pdfs docs/*.pdf --categories "Invoice,Receipt,Contract" --output-dir out/
```

**Specify a different vision model:**
```bash
python src/main.py -i invoice.pdf -c categories.txt -m gemma-4-31b-it --instructions instructions.txt
```

## Contributing

See CONTRIBUTING.md for guidelines.

## License

This project is unlicensed or its license is not specified in the repository.
