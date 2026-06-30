import os
import sys
import pytest
import json
import fitz
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@patch("src.ai_classification.genai.Client")
@patch("src.ai_classification.time.sleep")
def test_full_pipeline(mock_sleep, mock_client, tmp_path):
    # Setup mock LLM response
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.text = '{"category": "Invoice", "reason": "E2E testing"}'
    mock_instance.models.generate_content.return_value = mock_response

    # Setup inputs
    input_pdf = tmp_path / "sample.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(input_pdf))
    doc.close()
    
    categories_file = tmp_path / "cats.txt"
    categories_file.write_text("Invoice\nReceipt\n")
    
    out_dir = tmp_path / "output"
    
    # Mock sys.argv
    test_args = ["main.py", "-i", str(input_pdf), "-c", str(categories_file), "-o", str(out_dir)]
    
    with patch.object(sys, 'argv', test_args):
        from src.main import main
        main()
        
    # Verify outputs
    report_path = out_dir / "sample.pdf_report.json"
    assert report_path.exists()
    
    with open(report_path, "r") as f:
        report = json.load(f)
        assert report["1"]["category"] == "Invoice"
        
    final_pdf_path = out_dir / "sample_categorized.pdf"
    assert final_pdf_path.exists()
    
    # Verify metadata in final PDF
    final_doc = fitz.open(str(final_pdf_path))
    labels = final_doc.get_page_labels()
    assert len(labels) == 1
    assert labels[0]["prefix"] == "1 - Invoice"
    final_doc.close()
