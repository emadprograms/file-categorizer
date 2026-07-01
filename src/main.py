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

import logging
from datetime import datetime

def setup_logging():
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"run_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)


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
    parser.add_argument("-m", "--model", choices=["gemma-4-26b", "gemma-4-31b-it", "gemma-4-26b-a4b-it"], default="gemma-4-26b-a4b-it", help="Vision model to use")
    parser.add_argument("--instructions", help="Path to a text file containing custom instructions for the AI")
    return parser.parse_args(args)

def main() -> None:
    """
    Main entry point for the CLI application.
    
    This function coordinates the execution flow: parsing arguments, loading
    categories, processing each PDF, running classification, generating a report,
    and writing the metadata back into the final PDF.
    """
    setup_logging()
    
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")
        sys.exit(1)
        
    args = parse_args()
    
    # Load categories
    try:
        categories = load_categories(args.categories_file)
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        sys.exit(1)
        
    # Load custom instructions if provided
    custom_instructions = ""
    if args.instructions:
        if os.path.isfile(args.instructions):
            with open(args.instructions, "r", encoding="utf-8") as f:
                custom_instructions = f.read().strip()
        else:
            logger.error(f"Error: Instructions file not found: {args.instructions}")
            sys.exit(1)
        
    # Validate and expand input PDFs (handles Windows wildcard passing)
    import glob
    expanded_pdfs = []
    for pattern in args.input_pdfs:
        matches = glob.glob(pattern)
        if not matches:
            logger.error(f"Error: No files matching: {pattern}")
            sys.exit(1)
        for m in matches:
            if "categorized_pdfs" not in m and "_categorized" not in os.path.basename(m):
                expanded_pdfs.append(m)
                
    if not expanded_pdfs:
        logger.error("Error: No valid input PDFs found (all matching files were output PDFs).")
        sys.exit(1)
        
    for pdf_path in expanded_pdfs:
        if not os.path.isfile(pdf_path):
            logger.error(f"Error: Input PDF file not found: {pdf_path}")
            sys.exit(1)
            
    # Replace the input_pdfs with the expanded list
    args.input_pdfs = expanded_pdfs
            
    # Create output directory if explicitly provided
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    for pdf_path in args.input_pdfs:
        basename = os.path.basename(pdf_path)
        base_name_without_ext, _ = os.path.splitext(basename)
        
        input_dir = os.path.dirname(os.path.abspath(pdf_path))
        report_path = os.path.join(input_dir, f"{base_name_without_ext}_report.json")
        
        if args.output_dir:
            final_output_dir = args.output_dir
            tmp_base_dir = args.output_dir
        else:
            final_output_dir = os.path.join(input_dir, "categorized_pdfs")
            tmp_base_dir = input_dir
            
        os.makedirs(final_output_dir, exist_ok=True)
        if tmp_base_dir != final_output_dir:
            os.makedirs(tmp_base_dir, exist_ok=True)
        
        resume_status = {}
        if os.path.exists(report_path):
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    existing_report = json.load(f)
                    
                has_failed_pages = False
                for page_num_str, page_info in existing_report.items():
                    page_idx = int(page_num_str) - 1
                    page_key = f"page_{page_idx}"
                    
                    if page_info.get("category") not in categories:
                        has_failed_pages = True
                        resume_status[page_key] = {"status": "error"}
                    else:
                        resume_status[page_key] = {
                            "status": "classified",
                            "category": page_info.get("category"),
                            "reason": page_info.get("reason", ""),
                            "telemetry": page_info.get("telemetry", {})
                        }
                        
                if not has_failed_pages:
                    logger.info(f"Skipping {pdf_path}, report already exists and all pages succeeded.")
                    continue
                else:
                    logger.info(f"Resuming {pdf_path} to retry failed pages.")
                    tmp_dir = os.path.join(tmp_base_dir, f".tmp_{basename}")
                    os.makedirs(tmp_dir, exist_ok=True)
                    progress_file_path = os.path.join(tmp_dir, "progress.json")
                    if not os.path.exists(progress_file_path):
                        with open(progress_file_path, "w", encoding="utf-8") as f:
                            json.dump(resume_status, f)
            except Exception as e:
                logger.warning(f"Could not read existing report {report_path}: {e}")
            
        try:
            status, tmp_dir = process_pdf(pdf_path, tmp_base_dir)
            
            if status is None:
                logger.error(f"Skipping {pdf_path} due to an error opening the file.")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                continue
            
            logger.info(f"Classifying pages for {pdf_path}...")
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
            
            final_pdf_path = os.path.join(final_output_dir, final_pdf_name)
            
            inject_pdf_metadata(pdf_path, final_pdf_path, report_data)
            
            logger.info(f"Processed {pdf_path}. Target PDF output: {final_pdf_name}")
            
            # Temporary images cleanup on complete success
            shutil.rmtree(tmp_dir, ignore_errors=True)
            
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            continue

if __name__ == "__main__":
    main()
