import os
from pathlib import Path

from core import MiniMaxOCR
from utils import get_b64_image


def load_api_key() -> str:
    return Path("api.key").read_text().strip()


def iter_images(folder: Path):
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            yield path


def process_image(ocr: MiniMaxOCR, image_b4: str, deny_list: list[str] = []) -> str:
    additional_prompt = ""
    if deny_list:
        additional_prompt += f"Forbidden outputs (must not return any of these; if your first answer matches one, re-check the image and return a different 4-character code): {deny_list}"
    return ocr.get_4_char_code(image_b4, additional_prompt=additional_prompt)


def main() -> None:
    api_key = load_api_key()
    ocr = MiniMaxOCR(api_key)
    deny_list = []

    input_dir = "./input/image2.jpg"
    # deny_list.append("4QXI")

    code = process_image(ocr, get_b64_image(input_dir), deny_list)
    print(f"{input_dir}\t{code}")


if __name__ == "__main__":  # pragma: no cover
    main()
