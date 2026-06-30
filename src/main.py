"""
Command Line Interface for the Arabic PDF OCR & Categorization application.

This module provides the main entry point for the application. It parses
command-line arguments, orchestrates the processing of PDF files, invokes
the AI classification, and saves the final categorized PDFs.
"""
import argparse
import sys
import os
import shutil

# Ensure the root directory is in sys.path when running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils import load_categories
from src.image_processing import process_pdf
from src.ai_classification import classify_pages
from src.metadata import generate_report, inject_pdf_metadata
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_args(args=None) -> argparse.Namespace:
    """
    Parses command-line arguments.
    
    Args:
        args: Optional list of command-line arguments to parse (useful for testing).
              If None, uses sys.argv.
              
    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Arabic PDF OCR & Categorization CLI")
    parser.add_argument("-i", "--input-pdfs", nargs="+", required=True, help="Input PDF files")
    parser.add_argument("-c", "--categories", required=True, dest="categories_file", help="Path to categories file, or a comma-separated list of categories")
    parser.add_argument("-o", "--output-dir", help="Output directory (defaults to the input file's directory)")
    parser.add_argument("-m", "--model", choices=["gemma-4-26b", "gemma-4-31b-it"], default="gemma-4-26b", help="Vision model to use")
    parser.add_argument("--instructions", help="Path to a text file containing custom instructions for the AI")
    return parser.parse_args(args)

def main() -> None:
    """
    Main entry point for the CLI application.
    
    This function coordinates the execution flow: parsing arguments, loading
    categories, processing each PDF, running classification, generating a report,
    and writing the metadata back into the final PDF.
    """
    args = parse_args()
    
    # Load categories
    try:
        categories = load_categories(args.categories_file)
    except Exception as e:
        print(f"Error loading categories: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Load custom instructions if provided
    custom_instructions = ""
    if args.instructions:
        if os.path.isfile(args.instructions):
            with open(args.instructions, "r", encoding="utf-8") as f:
                custom_instructions = f.read().strip()
        else:
            print(f"Error: Instructions file not found: {args.instructions}", file=sys.stderr)
            sys.exit(1)
        
    # Validate and expand input PDFs (handles Windows wildcard passing)
    import glob
    expanded_pdfs = []
    for pattern in args.input_pdfs:
        matches = glob.glob(pattern)
        if not matches:
            print(f"Error: No files matching: {pattern}", file=sys.stderr)
            sys.exit(1)
        expanded_pdfs.extend(matches)
        
    for pdf_path in expanded_pdfs:
        if not os.path.isfile(pdf_path):
            print(f"Error: Input PDF file not found: {pdf_path}", file=sys.stderr)
            sys.exit(1)
            
    # Replace the input_pdfs with the expanded list
    args.input_pdfs = expanded_pdfs
            
    # Create output directory if explicitly provided
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    for pdf_path in args.input_pdfs:
        basename = os.path.basename(pdf_path)
        base_name_without_ext, _ = os.path.splitext(basename)
        
        current_output_dir = args.output_dir if args.output_dir else os.path.dirname(os.path.abspath(pdf_path))
        if not args.output_dir:
            os.makedirs(current_output_dir, exist_ok=True)
            
        report_path = os.path.join(current_output_dir, f"{basename}_report.json")
        if os.path.exists(report_path):
            print(f"Skipping {pdf_path}, report already exists.")
            continue
            
        try:
            status, tmp_dir = process_pdf(pdf_path, current_output_dir)
            
            try:
                print(f"Classifying pages for {pdf_path}...")
                classify_pages(tmp_dir, categories, model=args.model, custom_instructions=custom_instructions)
                
                # Reload status from progress.json to get classification results
                progress_file = os.path.join(tmp_dir, "progress.json")
                if os.path.exists(progress_file):
                    with open(progress_file, "r", encoding="utf-8") as f:
                        status = json.load(f)
                        
                report_data = generate_report(status)
                
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report_data, f, indent=4, ensure_ascii=False)
                
                failed_pages = [
                    str(int(page_key.replace("page_", "")) + 1) 
                    for page_key, page_status in status.items() 
                    if (isinstance(page_status, dict) and page_status.get("status") == "error") or page_status == "error"
                ]
                
                final_pdf_name = f"{base_name_without_ext}_categorized"
                if failed_pages:
                    failed_pages.sort(key=int)
                    final_pdf_name += f"_failed_pages_{'_'.join(failed_pages)}"
                final_pdf_name += ".pdf"
                
                final_pdf_path = os.path.join(current_output_dir, final_pdf_name)
                inject_pdf_metadata(pdf_path, final_pdf_path, report_data)
                
                print(f"Processed {pdf_path}. Target PDF output: {final_pdf_name}")
            finally:
                # Temporary images cleanup
                shutil.rmtree(tmp_dir, ignore_errors=True)
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
            continue

if __name__ == "__main__":
    main()
