#!/usr/bin/env python3
"""
MiniMax Vision OCR - Captcha Solver using MiniMax Coding Plan MCP
Uses the understand_image tool from MiniMax-Coding-Plan-MCP

Setup:
    pip install minimax-coding-plan-mcp
    uvx minimax-coding-plan-mcp
    
Or use direct API with a different vision provider (OpenAI GPT-4o, Google Gemini)
"""

import os
import subprocess
import json
import re

# Configuration
MOCK_MODE = os.environ.get("MINIMAX_MOCK_MODE", "false").lower() == "true"

def solve_captcha(image_path, mock_result=None):
    """
    Send captcha image to MiniMax via understand_image tool.
    Requires MiniMax Coding Plan MCP server to be running.
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

    # Check if file exists
    if not os.path.exists(image_path):
        return f"ERROR: File not found: {image_path}"

    # Method 1: Use MiniMax Coding Plan MCP (if available)
    try:
        result = subprocess.run(
            ["npx", "-y", "minimax-coding-plan-mcp", "understand_image"],
            input=json.dumps({
                "prompt": "Extract ONLY the 4 characters you see. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). Example: W5FE",
                "image_url": f"file://{os.path.abspath(image_path)}"
            }),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if "text" in data:
                text = data["text"]
                clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
                if clean_text:
                    return clean_text
    except Exception as mcp_error:
        pass  # Fall through to next method
    
    # Method 2: Use OpenAI GPT-4o (alternative)
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key:
        try:
            import base64
            from openai import OpenAI
            
            client = OpenAI(api_key=openai_key)
            
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract ONLY the 4 characters you see in this image. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). Example: W5FE"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            text = response.choices[0].message.content.strip()
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
            if clean_text:
                return clean_text
        except Exception as openai_error:
            pass  # Fall through to next method
    
    # Method 3: Use Google Gemini (alternative)
    gemini_key = os.environ.get("GOOGLE_API_KEY", "")
    if gemini_key:
        try:
            import httpx
            from PIL import Image
            
            img = Image.open(image_path)
            
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                json={
                    "contents": [{
                        "parts": [
                            {"text": "Extract ONLY the 4 characters you see. Reply with exactly 4 uppercase letters or numbers (A-Z, 0-9). Example: W5FE"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(img.tobytes()).decode('utf-8')}}
                        ]
                    }],
                    "generationConfig": {"maxOutputTokens": 10, "temperature": 0.1}
                },
                timeout=30
            )
            
            data = response.json()
            if "candidates" in data:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
                if clean_text:
                    return clean_text
        except Exception as gemini_error:
            pass
    
    # Method 4: Local OCR fallback (EasyOCR)
    try:
        import easyocr
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_path, detail=0)
        if result:
            text = ' '.join(result)
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())[:4]
            if clean_text:
                return clean_text
    except Exception:
        pass
    
    return "ERROR: No vision provider available. Set MINIMAX_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY, or install EasyOCR."

def main():
    """Read images from input directory, print results"""
    input_dir = "input"
    
    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' directory not found!")
        print(f"Create '{input_dir}' folder and put images there")
        exit(1)
    
    # Get sorted list of image files
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))])
    
    if not files:
        print(f"No image files found in '{input_dir}'")
        exit(0)
    
    # Process each file
    for filename in files:
        path = os.path.join(input_dir, filename)
        result = solve_captcha(path)
        print(f"{filename}\t{result}")

if __name__ == "__main__":
    main()
