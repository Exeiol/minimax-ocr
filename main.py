import os
from pathlib import Path

from core import MiniMaxOCR
from utils import to_data_url


def load_api_key() -> str:
    return Path("api.key").read_text().strip()


def iter_images(folder: Path):
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            yield path


def main() -> None:
    api_key = load_api_key()
    ocr = MiniMaxOCR(api_key)

    deny_list = []

    input_dir = "./input/image2.jpg"
    # deny_list.append("4QXI")

    data_url = to_data_url(input_dir)
    additional_prompt = ""
    if deny_list:
        additional_prompt += f"Forbidden outputs (must not return any of these; if your first answer matches one, re-check the image and return a different 4-character code): {deny_list}"
    code = ocr.get_4_char_code(data_url, additional_prompt=additional_prompt)
    print(f"{input_dir}\t{code}")


if __name__ == "__main__":  # pragma: no cover
    main()
