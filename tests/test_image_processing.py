import pytest
import os
import json
import numpy as np
import cv2
import fitz
from unittest.mock import patch, MagicMock
from src.image_processing import adjust_levels, auto_deskew, extract_and_clean_page, process_pdf

def test_adjust_levels():
    image = np.array([[0, 50, 100], [150, 200, 255]], dtype=np.uint8)
    adjusted = adjust_levels(image, 50, 200)
    
    assert adjusted[0, 0] == 0
    assert adjusted[0, 1] == 0
    assert adjusted[1, 1] == 255
    assert adjusted[1, 2] == 255
    assert adjusted[0, 2] > 0 and adjusted[0, 2] < 255

def test_auto_deskew():
    image = np.zeros((100, 100), dtype=np.uint8)
    cv2.rectangle(image, (20, 20), (80, 80), 255, -1)
    
    deskewed = auto_deskew(image)
    assert deskewed.shape == image.shape

def test_extract_and_clean_page(tmp_path):
    pdf_path = str(tmp_path / "test.pdf")
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf_path)
    
    clean_path = extract_and_clean_page(doc, 0, str(tmp_path))
    doc.close()
    
    assert os.path.exists(clean_path)
    assert clean_path.endswith("page_0.png")

def test_process_pdf(tmp_path):
    pdf_path = str(tmp_path / "test.pdf")
    doc = fitz.open()
    doc.new_page()
    doc.new_page()
    doc.save(pdf_path)
    doc.close()
    
    status, tmp_dir = process_pdf(pdf_path, str(tmp_path))
    
    assert status["page_0"]["status"] == "extracted"
    assert status["page_1"]["status"] == "extracted"
    assert os.path.exists(tmp_dir)
    
    progress_file = os.path.join(tmp_dir, "progress.json")
    assert os.path.exists(progress_file)
    with open(progress_file, "r") as f:
        saved_status = json.load(f)
        assert saved_status["page_0"]["status"] == "extracted"

@patch("src.image_processing.extract_and_clean_page")
def test_process_pdf_retry_logic(mock_extract, tmp_path):
    pdf_path = str(tmp_path / "test_error.pdf")
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf_path)
    doc.close()
    
    # First time fail, second time success
    mock_extract.side_effect = [Exception("Failed extraction"), "mock_path"]
    
    status, tmp_dir = process_pdf(pdf_path, str(tmp_path))
    
    # We retry once per page, so it should be extracted
    assert status["page_0"]["status"] == "extracted"
    assert mock_extract.call_count == 2
