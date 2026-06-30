import os
import json
import logging
import fitz  # PyMuPDF
import cv2
import numpy as np

logger = logging.getLogger(__name__)

def adjust_levels(image, black_point, white_point):
    lut = np.zeros(256, dtype=np.uint8)
    for i in range(256):
        if i <= black_point:
            lut[i] = 0
        elif i >= white_point:
            lut[i] = 255
        else:
            lut[i] = int(((i - black_point) / (white_point - black_point)) * 255.0)
    return cv2.LUT(image, lut)

def auto_deskew(image):
    thresh = cv2.bitwise_not(image)
    _, thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return image
        
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    if abs(angle) < 0.5:
        return image
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def extract_and_clean_page(pdf_document, page_num: int, tmp_dir: str) -> str:
    """
    Extracts a single page from a PyMuPDF document, cleans it exactly like the reference implementation, and saves it as an image.
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
    gray = img_np[:, :, 1]
    
    # Auto-Deskew
    gray = auto_deskew(gray)
    
    # Estimate Background (Illumination Map)
    kernel_large = np.ones((15, 15), np.uint8)
    bg = cv2.dilate(gray, kernel_large, iterations=1)
    bg = cv2.GaussianBlur(bg, (21, 21), 0)
    
    # Illumination Normalization (Division)
    # Add small epsilon to prevent division by zero, though cv2/numpy handle it mostly
    bg_float = bg.astype(np.float32)
    bg_float[bg_float == 0] = 1.0
    normalized = 255 * (gray.astype(np.float32) / bg_float)
    normalized = np.clip(normalized, 0, 255).astype(np.uint8)
    
    # Wash Out Light Colors ("Clean Background")
    cleaned = adjust_levels(normalized, black_point=0, white_point=220)
    
    # Diacritic Boost (Black-Hat Filter)
    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    blackhat = cv2.morphologyEx(cleaned, cv2.MORPH_BLACKHAT, kernel_small)
    boosted = cv2.subtract(cleaned, blackhat)
    
    # Sharpening (Unsharp Mask)
    gaussian = cv2.GaussianBlur(boosted, (0, 0), 2.0)
    sharpened = cv2.addWeighted(boosted, 1.5, gaussian, -0.5, 0)
    
    output_path = os.path.join(tmp_dir, f"page_{page_num}.png")
    cv2.imwrite(output_path, sharpened)
    
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
