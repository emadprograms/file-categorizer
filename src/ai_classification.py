"""
AI Classification module.

This module handles communicating with the Google GenAI API to categorize
cleaned document images into predefined categories.
"""
import os
import json
import time
import sys
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

def classify_pages(tmp_dir: str, categories: list, model: str = 'gemma-4-26b', custom_instructions: str = "") -> None:
    """
    Classifies processed PDF pages using a vision model.
    
    This function reads the `progress.json` file to find pages that have been
    successfully extracted, uploads the images to the GenAI API, and prompts the
    model to categorize them into one of the provided categories. It updates the
    progress file with the classification results.
    
    Args:
        tmp_dir: The temporary directory containing the extracted images and `progress.json`.
        categories: A list of valid category strings.
        model: The name of the Google GenAI vision model to use (default: 'gemma-4-26b').
        custom_instructions: Optional string containing specific rules for the AI.
    """
    progress_file = os.path.join(tmp_dir, "progress.json")
    
    if not os.path.exists(progress_file):
        logger.error(f"Progress file not found in {tmp_dir}")
        return
        
    with open(progress_file, "r", encoding="utf-8") as f:
        status = json.load(f)
        
    client = genai.Client(http_options={'timeout': 60000.0})
    
    last_call_time = 0
    
    for page_key, current_status in status.items():
        is_ready = (current_status == "success") or (isinstance(current_status, dict) and current_status.get("status") == "extracted")
        if not is_ready:
            continue
            
        page_num = page_key.split("_")[1]
        image_path = os.path.join(tmp_dir, f"{page_key}.png")
        
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            status[page_key] = {"status": "error", "error": "Image not found"}
            continue
            
        # Try up to 3 times for classification
        max_retries = 3
        classified = False
        
        for attempt in range(max_retries):
            # Enforce 7-second rate limit
            current_time = time.time()
            elapsed = current_time - last_call_time
            if elapsed < 7.0:
                time.sleep(7.0 - elapsed)
            
            try:
                # Prepare image and prompt
                image = client.files.upload(file=image_path)
                try:
                    prompt = (
                        "Categorize this Arabic PDF page. "
                        "You must select EXACTLY ONE category from the following list: "
                        f"{categories}. "
                    )
                    
                    if custom_instructions:
                        prompt += f"CRITICAL INSTRUCTIONS:\n{custom_instructions}\n"
                        
                    prompt += (
                        "Respond with a JSON object containing 'category' (the chosen category) "
                        "and 'reason' (the thinking or evidence from the page justifying this choice)."
                    )
                    
                    last_call_time = time.time()
                    
                    response = client.models.generate_content(
                        model=model,
                        contents=[image, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema={"type": "object", "properties": {"category": {"type": "string", "enum": categories}, "reason": {"type": "string"}}, "required": ["category", "reason"]}
                        )
                    )
                    
                    try:
                        result = json.loads(response.text)
                        category = result.get("category")
                        
                        if category in categories:
                            status[page_key] = {
                                "status": "classified",
                                "category": category,
                                "reason": result.get("reason", "")
                            }
                            classified = True
                            break
                        else:
                            logger.warning(f"Invalid category '{category}' returned for {page_key}")
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON returned for {page_key}")
                finally:
                    try:
                        # Clean up the file from cloud storage
                        client.files.delete(name=image.name)
                    except Exception as e:
                        logger.warning(f"Failed to delete {image.name} from cloud storage: {e}")
                    
                    
            except APIError as e:
                if e.code == 429:
                    logger.warning("Rate limit exceeded (429). Sleeping for 65 seconds.")
                    time.sleep(65)
                elif e.code in (500, 503):
                    logger.warning(f"Server error ({e.code}). Sleeping for 15 seconds.")
                    time.sleep(15)
                elif e.code == 401:
                    logger.error("Authentication failed (401). Please check your API key.")
                    sys.exit(1)
                elif e.code == 404:
                    logger.error(f"Model not found or endpoint not supported (404): {e}")
                    sys.exit(1)
                else:
                    logger.error(f"API Error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error classifying {page_key}: {e}")
                
        if not classified:
            status[page_key] = {"status": "error", "error": "Classification failed after retries"}
            
        # Save progress after each page
        tmp_progress = progress_file + ".tmp"
        with open(tmp_progress, "w", encoding="utf-8") as f:
            json.dump(status, f)
        os.replace(tmp_progress, progress_file)
