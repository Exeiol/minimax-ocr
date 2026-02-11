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

    # input_dir = Path("input")
    # for img_path in iter_images(input_dir):
    #     data_url = to_data_url(img_path)
    #     code = ocr.get_4_char_code(data_url)
    #     print(f"{img_path.name}\t{code}")

    input_dir = "./input/image4.jpg"
    data_url = to_data_url(input_dir)
    additional_prompt = ""
    deny_list = ["4QXI"]
    if deny_list:
        additional_prompt += f"Already Denied: {deny_list}"
    code = ocr.get_4_char_code(data_url, additional_prompt=additional_prompt)
    print(f"{input_dir}\t{code}")


if __name__ == "__main__":  # pragma: no cover
    main()
