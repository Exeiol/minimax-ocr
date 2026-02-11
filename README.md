# MiniMax Vision OCR

Simple captcha solver using MiniMax's multimodal API.

## Setup

```bash
cd ~/minimax-ocr/
pip install -r requirements.txt
```

## Configuration

Create these files in the `minimax-ocr` directory:

### 1. `api.key` (REQUIRED unless `MINIMAX_API_KEY` env var is set)
```
your_api_key_here
```

Get it from: https://platform.minimax.io/

### 2. `group_id.key` (OPTIONAL)
```
your_group_id_here
```
Only needed if your API requires it. Try without first.

## Input

Put your images in the `input/` directory:
- Supported formats: `.jpg`, `.jpeg`, `.png`
- Files are processed in alphabetical order

## Usage

```bash
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

- Core request logic lives in `core.py` (`MiniMaxOCR.get_4_char_code`)
- File I/O is isolated in `utils.py` so services can inject their own image data
- Only extracts A-Z and 0-9 characters; returns exactly 4 characters maximum
