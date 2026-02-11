# MiniMax Vision OCR

Simple captcha solver using MiniMax's multimodal API.

## Setup

```bash
cd ~/minimax-ocr/
pip install -r requirements.txt
```

## Configure API Key

```bash
export MINIMAX_API_KEY='your_api_key'
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

## Testing Without API Key (Mock Mode)

Test the code without an API key using mock mode:

```bash
export MINIMAX_MOCK_MODE='true'
python minimax_ocr.py test_images/*.gif
```

Mock mode generates random 4-character results for testing.

## How It Works

1. Encodes image as base64
2. Sends to MiniMax-M2.1 API (vision/multimodal)
3. Extracts 4-character captcha (A-Z, 0-9)
4. Returns clean uppercase text

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
- Use `MINIMAX_MOCK_MODE=true` for testing without API
