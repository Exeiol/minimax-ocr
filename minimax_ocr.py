#!/usr/bin/env python3
"""
MiniMax Vision OCR - Captcha Solver
Replicates OpenClaw's internal image analysis method
Reads from input/*.jpg, outputs: filename \t text
"""

import os
import base64
import json
import re
import urllib.request
import urllib.error
import ssl

# Configuration
def load_api_key():
    """Read API key from api.key file"""
    try:
        with open("/home/agent/Desktop/ocr_artifacts/api.key", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: api.key file not found!")
        print("Create 'api.key' file with your MiniMax API key")
        exit(1)

API_KEY = load_api_key()
MOCK_MODE = os.environ.get("MINIMAX_MOCK_MODE", "false").lower() == "true"

def image_to_base64(image_path):
    """Convert image to base64 data URL (OpenClaw format)"""
    with open(image_path, "rb") as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        ext = image_path.lower().split('.')[-1]
        # OpenClaw accepts: png, jpeg, webp
        if ext == 'png':
            fmt = 'png'
        elif ext in ['jpg', 'jpeg']:
            fmt = 'jpeg'
        else:
            fmt = 'jpeg'  # default
        return f"data:image/{fmt};base64,{base64_data}"

def solve_captcha(image_path):
    """Send captcha to MiniMax Vision using EXACT OpenClaw method"""
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

    # OpenClaw's EXACT MiniMax Vision API method:
    # Endpoint: /v1/coding_plan/vlm
    # Headers: Authorization: Bearer, Content-Type: application/json, MM-API-Source: OpenClaw
    # Payload: { prompt, image_url }
    # Response: { base_resp: { status_code, status_msg }, content }

    api_host = os.environ.get("MINIMAX_API_HOST", "https://api.minimax.io")
    url = f"{api_host}/v1/coding_plan/vlm"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "MM-API-Source": "OpenClaw"  # Critical: OpenClaw's signature header
    }

    payload = {
        "prompt": "Extract ONLY the 4 characters you see. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). Example: W5FE",
        "image_url": image_url
    }

    try:
        # Create request with proper SSL context
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            response_body = response.read().decode('utf-8')
            
        # Parse JSON response
        data = json.loads(response_body)
        
        # Parse OpenClaw's exact response format
        base_resp = data.get("base_resp") or {}
        status_code = base_resp.get("status_code")
        if status_code is not None and status_code != 0:
            status_msg = base_resp.get("status_msg", "")
            return f"API_ERROR: {status_msg} (code: {status_code})"

        # OpenClaw extracts "content" field, NOT "text"
        text = data.get("content", "").strip()
        
        # Clean and extract exactly 4 characters
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
        if clean_text:
            return clean_text
        return "PARSE_ERROR"

    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            error_data = json.loads(error_body)
            base_resp = error_data.get("base_resp") or {}
            return f"API_ERROR: {base_resp.get('status_msg', str(e))}"
        except:
            return f"API_ERROR: HTTP {e.code}"
    except json.JSONDecodeError as e:
        return f"API_ERROR: Invalid JSON response"
    except Exception as e:
        return f"API_ERROR: {e}"

def main():
    """Read images from input directory, print results"""
    input_dir = "/home/agent/Desktop/ocr_artifacts/input"
    
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' directory not found!")
        exit(1)
    
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif'))])
    
    if not files:
        print(f"No image files found in '{input_dir}'")
        exit(0)
    
    for filename in files:
        path = os.path.join(input_dir, filename)
        result = solve_captcha(path)
        print(f"{filename}\t{result}")

if __name__ == "__main__":
    main()
