import argparse
import sys
import os
import shutil

# Ensure the root directory is in sys.path when running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils import load_categories
from src.image_processing import process_pdf
from src.ai_classification import classify_pages
import json

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Arabic PDF OCR & Categorization CLI")
    parser.add_argument("-i", "--input-pdfs", nargs="+", required=True, help="Input PDF files")
    parser.add_argument("-c", "--categories-file", required=True, help="Path to categories file")
    parser.add_argument("-o", "--output-dir", required=True, help="Output directory")
    return parser.parse_args(args)

def main():
    args = parse_args()
    
    # Load categories
    try:
        categories = load_categories(args.categories_file)
    except Exception as e:
        print(f"Error loading categories: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Validate input PDFs
    for pdf_path in args.input_pdfs:
        if not os.path.isfile(pdf_path):
            print(f"Error: Input PDF file not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)
            
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    for pdf_path in args.input_pdfs:
        basename = os.path.basename(pdf_path)
        base_name_without_ext, _ = os.path.splitext(basename)
        
        report_path = os.path.join(args.output_dir, f"{basename}_report.json")
        if os.path.exists(report_path):
            print(f"Skipping {pdf_path}, report already exists.")
            continue
            
        try:
            status, tmp_dir = process_pdf(pdf_path, args.output_dir)
            
            print(f"Classifying pages for {pdf_path}...")
            classify_pages(tmp_dir, categories)
            
            # Reload status from progress.json to get classification results
            progress_file = os.path.join(tmp_dir, "progress.json")
            if os.path.exists(progress_file):
                with open(progress_file, "r", encoding="utf-8") as f:
                    status = json.load(f)
            
            failed_pages = [
                page_key.replace("page_", "") 
                for page_key, page_status in status.items() 
                if page_status == "error"
            ]
            
            final_pdf_name = f"{base_name_without_ext}_categorized"
            if failed_pages:
                failed_pages.sort(key=int)
                final_pdf_name += f"_failed_pages_{'_'.join(failed_pages)}"
            final_pdf_name += ".pdf"
            
            print(f"Processed {pdf_path}. Target PDF output: {final_pdf_name}")
            
            # Temporary: delete tmp_dir as instructed. 
            # In Phase 3, this will happen AFTER LLM classification and PDF generation.
            # shutil.rmtree(tmp_dir, ignore_errors=True)
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
