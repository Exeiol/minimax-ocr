#!/usr/bin/env python3
"""
MiniMax Vision OCR - Simple Captcha Solver
Sends image to MiniMax API, returns extracted 4-character text (A-Z, 0-9)
"""

import os
import base64
import requests
import json
import sys

# Configuration
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "YOUR_API_KEY_HERE")
MINIMAX_GROUP_ID = os.environ.get("MINIMAX_GROUP_ID", "YOUR_GROUP_ID_HERE")
API_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"
MOCK_MODE = os.environ.get("MINIMAX_MOCK_MODE", "false").lower() == "true"

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def solve_captcha(image_path, mock_result=None):
    """
    Send captcha image to MiniMax API and extract text.
    Expected: 4 characters, A-Z and 0-9 only.
    """
    # Mock mode for testing without API key
    if MOCK_MODE:
        import re
        import random
        if mock_result:
            clean_text = re.sub(r'[^A-Z0-9]', '', mock_result.upper())[:4]
        else:
            # Generate random 4-char result
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            clean_text = ''.join(random.choice(chars) for _ in range(4))
        return {
            "image": image_path,
            "result": clean_text,
            "raw_response": f"[MOCK] {clean_text}",
            "success": True,
            "mock": True
        }
    # Encode image
    try:
        base64_image = encode_image(image_path)
    except FileNotFoundError:
        return {"error": f"Image not found: {image_path}"}
    except Exception as e:
        return {"error": f"Failed to read image: {str(e)}"}

    # Prepare request (MiniMax supports images via base64 in content)
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build URL with GroupId
    url = f"{API_URL}?GroupId={MINIMAX_GROUP_ID}"

    payload = {
        "model": "MiniMax-M2",  # Use MiniMax-M2 for vision capabilities
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract ONLY the 4 characters you see in this captcha image. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). No other text. Example responses: W5FE, ABCD, 1234."
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
        "temperature": 0.1,  # Low temperature for consistent results
        "max_tokens": 10
    }

    # Make API call
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

    # Parse response
    try:
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["message"]["content"].strip()
            # Clean response - extract only alphanumeric, uppercase
            import re
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
            return {
                "image": image_path,
                "result": clean_text,
                "raw_response": text,
                "success": True
            }
        else:
            return {"error": f"Unexpected API response: {json.dumps(data)}"}
    except Exception as e:
        return {"error": f"Failed to parse response: {str(e)}"}

def batch_solve(image_paths):
    """Solve multiple captcha images"""
    results = []
    for path in image_paths:
        print(f"Processing: {path}")
        result = solve_captcha(path)
        results.append(result)
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Result: {result['result']}")
    return results

if __name__ == "__main__":
    # Usage examples
    if len(sys.argv) < 2:
        print("Usage: python minimax_ocr.py <image_path>")
        print("       python minimax_ocr.py *.gif")
        print("\nSet API key: export MINIMAX_API_KEY='your_key'")
        print("Or use mock mode: export MINIMAX_MOCK_MODE='true'")
        sys.exit(1)

    # Get image paths
    import glob
    if "*" in sys.argv[1]:
        image_paths = glob.glob(sys.argv[1])
    else:
        image_paths = sys.argv[1:]

    # Check API key and Group ID (skip if mock mode)
    if not MOCK_MODE:
        if MINIMAX_API_KEY == "YOUR_API_KEY_HERE":
            print("⚠️  Set MINIMAX_API_KEY environment variable first!")
            print("   export MINIMAX_API_KEY='your_api_key'")
            print("   export MINIMAX_GROUP_ID='your_group_id'")
            print("   Or test with mock mode: export MINIMAX_MOCK_MODE='true'")
            sys.exit(1)
        if MINIMAX_GROUP_ID == "YOUR_GROUP_ID_HERE":
            print("⚠️  Set MINIMAX_GROUP_ID environment variable first!")
            print("   export MINIMAX_GROUP_ID='your_group_id'")
            sys.exit(1)

    # Solve
    results = batch_solve(image_paths)

    # Summary
    successful = sum(1 for r in results if r.get("success"))
    mode = "[MOCK MODE] " if MOCK_MODE else ""
    print(f"\n{mode}📊 Results: {successful}/{len(results)} successful")
