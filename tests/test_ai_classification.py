import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ai_classification import classify_pages
from google.genai.errors import APIError

@pytest.fixture
def temp_dir(tmpdir):
    d = tmpdir.mkdir("tmp_pdf")
    progress_file = d.join("progress.json")
    status = {
        "page_0": "success",
        "page_1": "success",
        "page_2": "error"
    }
    progress_file.write(json.dumps(status))
    d.join("page_0.png").write("fake_image_data")
    d.join("page_1.png").write("fake_image_data")
    return str(d)

@patch("src.ai_classification.genai.Client")
@patch("src.ai_classification.time.sleep")
def test_classify_pages_success(mock_sleep, mock_client, temp_dir):
    # Setup mock client
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.text = '{"category": "invoice"}'
    mock_instance.models.generate_content.return_value = mock_response
    
    categories = ["invoice", "receipt", "contract"]
    classify_pages(temp_dir, categories)
    
    with open(os.path.join(temp_dir, "progress.json"), "r") as f:
        status = json.load(f)
        
    assert status["page_0"]["category"] == "invoice"
    assert status["page_1"]["category"] == "invoice"
    assert status["page_2"] == "error"  # Was skipped
    
    # 7 second limit enforced?
    assert mock_sleep.call_count >= 1

@patch("src.ai_classification.genai.Client")
@patch("src.ai_classification.time.sleep")
def test_classify_pages_invalid_category(mock_sleep, mock_client, temp_dir):
    # Setup mock client
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.text = '{"category": "invalid_cat"}'
    mock_instance.models.generate_content.return_value = mock_response
    
    categories = ["invoice", "receipt"]
    classify_pages(temp_dir, categories)
    
    with open(os.path.join(temp_dir, "progress.json"), "r") as f:
        status = json.load(f)
        
    assert status["page_0"]["status"] == "error"
    assert status["page_1"]["status"] == "error"
    assert mock_instance.models.generate_content.call_count == 6  # 3 retries for 2 pages

@patch("src.ai_classification.genai.Client")
@patch("src.ai_classification.time.sleep")
def test_classify_pages_rate_limit(mock_sleep, mock_client, temp_dir):
    mock_instance = mock_client.return_value
    mock_response = MagicMock()
    mock_response.text = '{"category": "invoice"}'
    
    def side_effect(*args, **kwargs):
        if mock_instance.models.generate_content.call_count == 1:
            class MockAPIError(APIError):
                def __init__(self, code):
                    self.code = code
            raise MockAPIError(429)
        return mock_response
        
    mock_instance.models.generate_content.side_effect = side_effect
    
    categories = ["invoice"]
    classify_pages(temp_dir, categories)
    
    # Should sleep 65s for 429 error
    mock_sleep.assert_any_call(65)
    
    with open(os.path.join(temp_dir, "progress.json"), "r") as f:
        status = json.load(f)
        
    assert status["page_0"]["category"] == "invoice"
