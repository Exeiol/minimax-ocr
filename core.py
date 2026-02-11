import re
import requests


ALLOWED_RE = re.compile(r"[^A-Z0-9]")
CODE_RE = re.compile(r"^[A-Z0-9]{4}$")

API_HOST = "https://api.minimax.io"
API_URL = f"{API_HOST}/v1/coding_plan/vlm"

DEFAULT_PROMPT = (
    "You are a precise OCR agent.\n"
    "Read the captcha.\n"
    "Return ONLY the 4-character code.\n"
    "Allowed characters: A-Z and 0-9.\n"
    "No extra text."
)


def clean4(text: str) -> str:
    return ALLOWED_RE.sub("", str(text).upper())[:4]


class MiniMaxOCR:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "MM-API-Source": "OpenClaw",
        }

    def get_4_char_code(
        self,
        image_data_url: str,
        prompt: str = DEFAULT_PROMPT,
        timeout: int = 60,
        additional_prompt: str = "",
    ) -> str:
        payload = {
            "prompt": (
                prompt + "\n" + additional_prompt if additional_prompt else prompt
            ),
            "image_url": image_data_url,
        }

        resp = requests.post(
            API_URL,
            headers=self._headers(),
            json=payload,
            timeout=timeout,
        )

        if not resp.ok:
            return f"ERROR HTTP {resp.status_code}: {resp.text[:300]}"

        data = resp.json()
        base_resp = data.get("base_resp") or {}
        if base_resp.get("status_code") != 0:
            return f"ERROR API {base_resp.get('status_code')}: {base_resp.get('status_msg')}"

        raw = (data.get("content") or "").strip()
        cleaned = clean4(raw)

        # strict validation: if it's not exactly 4 chars, expose raw output
        if not CODE_RE.match(cleaned):
            return f"INVALID: {cleaned} | raw={raw!r}"

        return cleaned
