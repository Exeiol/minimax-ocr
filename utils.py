import base64
import mimetypes
from pathlib import Path


def to_data_url(image_path: str) -> str:
    """
    Convert an image on disk to a data URL string.
    Keeps core logic free from file I/O so it can be reused elsewhere.
    """
    path = Path(image_path)
    mime, _ = mimetypes.guess_type(path.name)
    if mime not in ("image/png", "image/jpeg", "image/webp"):
        mime = "image/jpeg"

    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"
