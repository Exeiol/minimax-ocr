# MiniMax Vision OCR

Simple captcha solver using MiniMax's multimodal API.

## Setup

```bash
cd ~/minimax-ocr/
pip install -r requirements.txt
```

## Configure API Key

```bash
export MINIMAX_API_KEY='your_api_key_here'
```

Get your key from: https://platform.minimax.io/

## Usage

```bash
# Single image
python minimax_ocr.py captcha.gif

# Multiple images
python minimax_ocr.py test_images/*.gif

# All images
python minimax_ocr.py *.gif
```

## How It Works

1. Encodes image as base64
2. Sends to MiniMax-M2.1 API with vision capabilities
3. Extracts 4-character captcha text (A-Z, 0-9)
4. Returns clean uppercase result

## Output Example

```
Processing: test_images/captcha.gif
  ✅ Result: W5FE

📊 Results: 1/1 successful
```

## Notes

- Requires MiniMax API key with vision/multimodal access
- Temperature set to 0.1 for consistent results
- Only accepts A-Z and 0-9 characters
- Returns 4 characters maximum
