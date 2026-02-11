# MiniMax Vision OCR

Simple captcha solver using MiniMax's multimodal API.

## Setup

```bash
cd ~/minimax-ocr/
pip install -r requirements.txt
```

## Configuration

Create these files in the `minimax-ocr` directory:

### 1. `api.key`
```
your_api_key_here
```

### 2. `group_id.key`  
```
your_group_id_here
```

Get them from: https://platform.minimax.io/

## Input

Put your images in the `input/` directory:
- Supported formats: `.jpg`, `.jpeg`, `.png`
- Files are processed in alphabetical order

## Usage

```bash
# Real API mode
python3 minimax_ocr.py

# Mock mode (testing without API)
export MINIMAX_MOCK_MODE='true'
python3 minimax_ocr.py
```

## Output Format

```
filename.ext	 extracted_text
```

Example:
```
captcha001.png	W5FE
captcha002.png	4RKG
```

## Notes

- Only extracts A-Z and 0-9 characters
- Returns exactly 4 characters maximum
- Temperature 0.1 for consistent results
- MiniMax-M2 model with vision/multimodal capabilities
