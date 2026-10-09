import os
import requests
from config import DOWNLOADS_DIR

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
}


def download_from_url(url: str, filename: str):
    safe_name = "".join(c for c in filename if c not in r'\/:*?"<>|')
    out_path = os.path.join(DOWNLOADS_DIR, f"{safe_name}.mp3")

    r = requests.get(url, headers=HEADERS, stream=True, timeout=60)
    r.raise_for_status()

    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return out_path