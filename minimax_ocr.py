#!/usr/bin/env python3
"""
MiniMax Vision OCR - Captcha Solver
Replicates OpenClaw's internal image analysis method
Reads from input/*.jpg, outputs: filename \t text
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

API_KEY = load_api_key()
MOCK_MODE = os.environ.get("MINIMAX_MOCK_MODE", "false").lower() == "true"

def image_to_base64(image_path):
    """Convert image to base64 data URL"""
    with open(image_path, "rb") as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        ext = image_path.lower().split('.')[-1]
        fmt = 'png' if ext == 'png' else 'jpeg'
        return f"data:image/{fmt};base64,{base64_data}"

def solve_captcha(image_path):
    """Send captcha to MiniMax Vision (same method as OpenClaw)"""
    if MOCK_MODE:
        import random
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(4))

    if not os.path.exists(image_path):
        return "ERROR: File not found"

    try:
        image_url = image_to_base64(image_path)
    except Exception as e:
        return f"ERROR: {e}"

    # OpenClaw's internal image tool uses the vision model endpoint
    # Try the correct MiniMax Vision API format
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Method 1: VLM endpoint (MiniMax-VL-01)
    payload = {
        "model": "MiniMax-VL-01",
        "prompt": "Extract ONLY the 4 characters you see. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). Example: W5FE",
        "image_url": image_url
    }

    try:
        response = requests.post(
            "https://api.minimax.io/v1/coding_plan/vlm",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        base_resp = data.get("base_resp") or {}
        status_code = base_resp.get("status_code")
        if status_code is not None and status_code != 0:
            return f"API_ERROR: {base_resp.get('status_msg', status_code)}"

        text = data.get("text", "").strip()
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
        if clean_text:
            return clean_text
        return "PARSE_ERROR"

    except Exception as e:
        return f"API_ERROR: {e}"

def main():
    """Read images from input directory, print results"""
    input_dir = "input"
    
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' directory not found!")
        exit(1)
    
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    if not files:
        print(f"No .jpg/.jpeg/.png files found in '{input_dir}'")
        exit(0)
    
    for filename in files:
        path = os.path.join(input_dir, filename)
        result = solve_captcha(path)
        print(f"{filename}\t{result}")

if __name__ == "__main__":
    main()
