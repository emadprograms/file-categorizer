import os
import json
import logging
import fitz  # PyMuPDF
import cv2
import numpy as np

logger = logging.getLogger(__name__)

def extract_and_clean_page(pdf_document, page_num: int, tmp_dir: str) -> str:
    """
    Extracts a single page from a PyMuPDF document, cleans it, and saves it as an image.
    """
    page = pdf_document.load_page(page_num)
    matrix = fitz.Matrix(300/72, 300/72)
    pix = page.get_pixmap(matrix=matrix)

    # Convert pixmap to numpy array for OpenCV
    if pix.n - pix.alpha < 4:      # GRAY or RGB
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        if pix.alpha:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
        elif pix.n == 1:
            img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
    else:                          # CMYK
        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_CMYK2RGB)
        
    # Green channel extraction
    img_gray = img_np[:, :, 1]
    
    # Division normalization (background removal)
    # Estimate background
    bg = cv2.medianBlur(img_gray, 21)
    # Add a small epsilon to avoid division by zero
    diff = 255 - cv2.absdiff(img_gray, bg)
    norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
    
    # White point washout (White Point 200-220)
    # Map 200 to 255
    washout = np.clip(norm.astype(np.float32) * (255.0 / 200.0), 0, 255).astype(np.uint8)
    
    # Black-hat filter (to boost fine details/diacritics)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    blackhat = cv2.morphologyEx(washout, cv2.MORPH_BLACKHAT, kernel)
    
    # Subtract blackhat from washout (makes dark parts darker)
    cleaned = cv2.subtract(washout, blackhat)
    
    output_path = os.path.join(tmp_dir, f"page_{page_num}.png")
    cv2.imwrite(output_path, cleaned)
    
    return output_path

def process_pdf(pdf_path: str, output_dir: str) -> tuple[dict, str]:
    """
    Processes all pages in a PDF, saving cleaned images to a temporary directory.
    Returns the page status dict and the path to the temp directory.
    """
    basename = os.path.basename(pdf_path)
    tmp_dir = os.path.join(output_dir, f".tmp_{basename}")
    os.makedirs(tmp_dir, exist_ok=True)
    
    progress_file = os.path.join(tmp_dir, "progress.json")
    
    status = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                status = json.load(f)
        except json.JSONDecodeError:
            pass

    def save_progress():
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(status, f)

    try:
        pdf_document = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Failed to open PDF {pdf_path}: {e}")
        return status, tmp_dir

    num_pages = len(pdf_document)
    
    # First pass
    for page_num in range(num_pages):
        page_key = f"page_{page_num}"
        if status.get(page_key) == "success":
            continue
            
        try:
            extract_and_clean_page(pdf_document, page_num, tmp_dir)
            status[page_key] = "success"
        except Exception as e:
            logger.error(f"Failed to process page {page_num} of {pdf_path}: {e}")
            status[page_key] = "error"
            
        save_progress()
        
    # Retry failed pages
    for page_num in range(num_pages):
        page_key = f"page_{page_num}"
        if status.get(page_key) == "error":
            try:
                extract_and_clean_page(pdf_document, page_num, tmp_dir)
                status[page_key] = "success"
            except Exception as e:
                logger.error(f"Retry failed for page {page_num} of {pdf_path}: {e}")
                status[page_key] = "error"
                
            save_progress()

    pdf_document.close()
    return status, tmp_dir
