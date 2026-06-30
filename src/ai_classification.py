import os
import json
import time
import sys
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

def classify_pages(tmp_dir: str, categories: list) -> None:
    progress_file = os.path.join(tmp_dir, "progress.json")
    
    if not os.path.exists(progress_file):
        logger.error(f"Progress file not found in {tmp_dir}")
        return
        
    with open(progress_file, "r", encoding="utf-8") as f:
        status = json.load(f)
        
    client = genai.Client()
    
    last_call_time = 0
    
    for page_key, current_status in status.items():
        if current_status != "success":
            continue
            
        page_num = page_key.split("_")[1]
        image_path = os.path.join(tmp_dir, f"{page_key}.png")
        
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            status[page_key] = "error"
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
                prompt = (
                    "Categorize this Arabic PDF page. "
                    "You must select EXACTLY ONE category from the following list: "
                    f"{categories}. "
                    "Respond with a JSON object containing a single key 'category' with the selected category."
                )
                
                last_call_time = time.time()
                
                response = client.models.generate_content(
                    model='gemma-4-26b',
                    contents=[image, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema={"type": "object", "properties": {"category": {"type": "string"}}, "required": ["category"]}
                    )
                )
                
                try:
                    result = json.loads(response.text)
                    category = result.get("category")
                    
                    if category in categories:
                        status[page_key] = category
                        classified = True
                        break
                    else:
                        logger.warning(f"Invalid category '{category}' returned for {page_key}")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON returned for {page_key}")
                    
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
                else:
                    logger.error(f"API Error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error classifying {page_key}: {e}")
                
        if not classified:
            status[page_key] = "error"
            
        # Save progress after each page
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(status, f)
