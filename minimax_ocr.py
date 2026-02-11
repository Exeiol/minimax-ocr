import os
import re
import base64
import mimetypes
import requests

ALLOWED_RE = re.compile(r"[^A-Z0-9]")
CODE_RE = re.compile(r"^[A-Z0-9]{4}$")

API_HOST = "https://api.minimax.io"
API_URL = f"{API_HOST}/v1/coding_plan/vlm"


def to_data_url(image_path: str) -> str:
    mime, _ = mimetypes.guess_type(image_path)
    if mime not in ("image/png", "image/jpeg", "image/webp"):
        mime = "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def clean4(text: str) -> str:
    return ALLOWED_RE.sub("", str(text).upper())[:4]


def get_4_char_code(image_path: str, api_key: str) -> str:
    prompt = (
        "You are a precise OCR agent.\n"
        "Read the captcha.\n"
        "Return ONLY the 4-character code.\n"
        "Allowed characters: A-Z and 0-9.\n"
        "No extra text."
    )

    image_data_url = to_data_url(image_path)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "MM-API-Source": "OpenClaw",
    }

    payload = {
        "prompt": prompt,
        "image_url": image_data_url,
    }

    r = requests.post(API_URL, headers=headers, json=payload, timeout=45)
    if not r.ok:
        return f"ERROR HTTP {r.status_code}: {r.text[:300]}"

    j = r.json()

    base_resp = j.get("base_resp") or {}
    if base_resp.get("status_code") != 0:
        return (
            f"ERROR API {base_resp.get('status_code')}: {base_resp.get('status_msg')}"
        )

    raw = (j.get("content") or "").strip()
    out = clean4(raw)

    # strict validation: if it's not exactly 4 chars, expose raw output
    if not CODE_RE.match(out):
        return f"INVALID: {out} | raw={raw!r}"

    return out


API_KEY = open("api.key").read().strip()

for name in sorted(os.listdir("./input")):
    if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        path = os.path.join("./input", name)
        print(f"{name} -> {get_4_char_code(path, API_KEY)}")
