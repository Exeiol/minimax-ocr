#!/usr/bin/env python3
"""
MiniMax Vision OCR - Simple Captcha Solver
Reads images from 'input' directory, outputs: filename \t text
"""

import os
import base64
import requests
import re

# Configuration
def load_api_key():
    """Read API key from api.key file"""
    try:
        with open("api.key", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: api.key file not found!")
        print("Create 'api.key' file with your MiniMax API key")
        exit(1)

def load_group_id():
    """Read Group ID from group_id.key file"""
    try:
        with open("group_id.key", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: group_id.key file not found!")
        print("Create 'group_id.key' file with your MiniMax Group ID")
        exit(1)

API_KEY = load_api_key()
GROUP_ID = load_group_id()
API_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"
MOCK_MODE = os.environ.get("MINIMAX_MOCK_MODE", "false").lower() == "true"

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def solve_captcha(image_path, mock_result=None):
    """
    Send captcha image to MiniMax API and extract 4 characters (A-Z, 0-9).
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

    # Encode image
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        return f"ERROR: {e}"

    # Prepare request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{API_URL}?GroupId={GROUP_ID}"

    payload = {
        "model": "MiniMax-M2",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract ONLY the 4 characters you see. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). No other text. Example: W5FE"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }

    # Make API call
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except Exception as e:
        return f"API_ERROR: {e}"

    # Parse response
    try:
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["message"]["content"].strip()
            # Extract only A-Z and 0-9, uppercase, exactly 4 chars
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
            return clean_text
        else:
            return f"PARSE_ERROR"
    except Exception:
        return "PARSE_ERROR"

def main():
    """Read images from input directory, print results"""
    input_dir = "input"
    
    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' directory not found!")
        print(f"Create '{input_dir}' folder and put images there")
        exit(1)
    
    # Get sorted list of image files
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    if not files:
        print(f"No .jpg/.jpeg/.png files found in '{input_dir}'")
        exit(0)
    
    # Process each file
    for filename in files:
        path = os.path.join(input_dir, filename)
        result = solve_captcha(path)
        print(f"{filename}\t{result}")

if __name__ == "__main__":
    main()
