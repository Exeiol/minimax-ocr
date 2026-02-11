import base64
import requests
import re
import json
import os


def get_4_char_code(image_path, api_key):
    """
    Uses MiniMax-VL-01 to extract a 4-character alphanumeric code from an image.
    """
    # 1. Encode image to base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # 2. Setup API details
    # OpenClaw typically uses the v2 chat completion for MiniMax
    url = "https://api.minimax.io/v1/text/chatcompletion_v2"
    # url = "https://api.minimaxi.chat/v1/text/chatcompletion_v2"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": "MiniMax-M2.1",  # OpenClaw's preferred vision model
        "messages": [
            {
                "role": "system",
                "content": "You are a precise OCR agent. Locate the 4-character code in the image. "
                "The code consists of uppercase letters and digits [A-Z, 0-9]. "
                "Return ONLY the 4-character code and nothing else.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Find and extract the 4-character alphanumeric code from this image.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            },
        ],
        "temperature": 0.01,  # Low temperature for deterministic OCR
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # 3. Extract and sanitize result
        # print(data)
        json.dump(
            data, open("debug_output.json", "w"), indent=4
        )  # Save raw response for debugging
        raw_text = data["choices"][0]["message"]["content"].strip()

        # OpenClaw-style validation: Ensure it matches the 4-char alphanumeric pattern
        match = re.search(r"[A-Z0-9]{4}", raw_text.upper())
        if match:
            return match.group(0)
        return f"Code not found or invalid format. Raw output: {raw_text}"

    except Exception as e:
        return f"Error: {str(e)}"


# Example Usage:
API_KEY = open("api.key").read().strip()

for i in os.listdir("./input"):
    if i.endswith(".jpg") or i.endswith(".png"):
        print(f"Processing {i}: {get_4_char_code(os.path.join('./input', i), API_KEY)}")
        # break
