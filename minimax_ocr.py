#!/usr/bin/env python3
"""
MiniMax Vision OCR - Simple Captcha Solver
Uses MiniMax-VL-01 vision-language model via Coding Plan API
Reads images from 'input' directory, outputs: filename \t text
"""

import os
import base64
import requests
import re

# Configuration
API_KEY = None
MOCK_MODE = os.environ.get("MINIMAX_MOCK_MODE", "false").lower() == "true"

def load_api_key():
    """Read API key from api.key file"""
    global API_KEY
    try:
        with open("api.key", "r") as f:
            API_KEY = f.read().strip()
    except FileNotFoundError:
        print("Error: api.key file not found!")
        print("Create 'api.key' file with your MiniMax API key")
        exit(1)

def image_to_data_url(image_path):
    """Convert image to base64 data URL"""
    with open(image_path, "rb") as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        # Detect format from file extension
        if image_path.lower().endswith('.png'):
            format = 'png'
        elif image_path.lower().endswith('.webp'):
            format = 'webp'
        else:
            format = 'jpeg'
        return f"data:image/{format};base64,{base64_data}"

def solve_captcha(image_path, mock_result=None):
    """
    Send captcha image to MiniMax Vision API and extract 4 characters (A-Z, 0-9).
    Uses Anthropic API format for Coding Plan subscribers.
    """
    # Mock mode for testing
    if MOCK_MODE:
        if mock_result:
            clean_text = re.sub(r'[^A-Z0-9]', '', mock_result.upper())[:4]
        else:
            import random
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            clean_text = ''.join(random.choice(chars) for _ in range(4))
        return clean_text

    # Read API key
    if API_KEY is None:
        load_api_key()

    # Encode image
    try:
        image_url = image_to_data_url(image_path)
    except Exception as e:
        return f"ERROR: {e}"

    # Method 1: Try Anthropic API format (for Coding Plan subscribers)
    anthropic_url = "https://api.minimax.io/anthropic/v1/messages"
    
    anthropic_headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    anthropic_payload = {
        "model": "MiniMax-VL-01",
        "max_tokens": 10,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract ONLY the 4 characters you see in this image. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). No other text. Example: W5FE"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_url.split(",")[1]
                        }
                    }
                ]
            }
        ]
    }

    # Try Anthropic format first (Coding Plan)
    try:
        response = requests.post(anthropic_url, headers=anthropic_headers, json=anthropic_payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Parse Anthropic response
        if "content" in data and len(data["content"]) > 0:
            for block in data["content"]:
                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
                    if clean_text:
                        return clean_text
        
        return "PARSE_ERROR: no text in response"
    except Exception as e:
        error_str = str(e)
        
        # If Anthropic format fails, try VLM format
        vlm_url = "https://api.minimax.io/v1/coding_plan/vlm"
        
        vlm_headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        vlm_payload = {
            "model": "MiniMax-VL-01",
            "prompt": "Extract ONLY the 4 characters you see in this image. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). No other text. Example: W5FE",
            "image_url": image_url
        }
        
        try:
            response = requests.post(vlm_url, headers=vlm_headers, json=vlm_payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for MiniMax errors
            base_resp = data.get("base_resp") or {}
            status_code = base_resp.get("status_code")
            if status_code is not None and status_code != 0:
                return f"API_ERROR: {base_resp.get('status_msg', status_code)}"
            
            # Extract text
            text = data.get("text", "").strip()
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
            if clean_text:
                return clean_text
            return "PARSE_ERROR: no valid characters"
        except Exception as e2:
            return f"API_ERROR: {str(e)}"

def main():
    """Read images from input directory, print results"""
    input_dir = "input"
    
    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' directory not found!")
        print(f"Create '{input_dir}' folder and put images there")
        exit(1)
    
    # Get sorted list of image files
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    
    if not files:
        print(f"No .jpg/.jpeg/.png/.webp files found in '{input_dir}'")
        exit(0)
    
    # Process each file
    for filename in files:
        path = os.path.join(input_dir, filename)
        result = solve_captcha(path)
        print(f"{filename}\t{result}")

if __name__ == "__main__":
    main()
