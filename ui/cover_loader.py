import os
import hashlib
import threading
import requests
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QFont, QBrush

from config import ASSETS_DIR


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

CACHE_DIR = os.path.join(ASSETS_DIR, "covers_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _itunes(title, artist):
    try:
        r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": f"{artist} {title}", "media": "music", "limit": 1},
            headers=HEADERS, timeout=5,
        )
        for item in r.json().get("results", []):
            art = item.get("artworkUrl100", "")
            if art:
                return art.replace("100x100", "600x600")
    except Exception:
        pass
    return None


def _deezer(title, artist):
    try:
        r = requests.get(
            "https://api.deezer.com/search",
            params={"q": f"{artist} {title}", "limit": 1},
            headers=HEADERS, timeout=5,
        )
        for item in r.json().get("data", []):
            alb = item.get("album", {})
            cover = alb.get("cover_xl") or alb.get("cover_big")
            if cover:
                return cover
    except Exception:
        pass
    return None


def find_cover(title, artist):
    return _itunes(title, artist) or _deezer(title, artist)


def make_placeholder(size=200, seed=""):
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    h = int(hashlib.md5(seed.encode()).hexdigest()[:6], 16)
    r1, g1, b1 = (h >> 16) & 0xFF, (h >> 8) & 0xFF, h & 0xFF

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor(r1, g1, b1))
    grad.setColorAt(1, QColor(20, 20, 25))
    p.setBrush(QBrush(grad))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(0, 0, size, size), 8, 8)

    letter = (seed[0] if seed else "♪").upper()
    p.setPen(QColor(255, 255, 255, 180))
    p.setFont(QFont("Inter", int(size * 0.3), QFont.Weight.Bold))
    p.drawText(QRectF(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, letter)
    p.end()
    return pix


class CoverLoader(QObject):
    cover_ready = pyqtSignal(str, QPixmap)
    cover_failed = pyqtSignal(str)

    _cache = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pending = {}

    @classmethod
    def _cache_path(cls, key):
        h = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(CACHE_DIR, f"{h}.jpg")

    @classmethod
    def get_cached(cls, key):
        if key in cls._cache:
            return cls._cache[key]
        path = cls._cache_path(key)
        if os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                cls._cache[key] = pix
                return pix
        return None

    def load(self, title, artist, size=200, callback_key=None):
        key = callback_key or f"{artist} - {title}"
        cached = self.get_cached(key)
        if cached:
            self.cover_ready.emit(key, cached)
            return
        placeholder = make_placeholder(size, key)
        self.cover_ready.emit(key + "__placeholder", placeholder)
        if key in self._pending:
            return
        self._pending[key] = True
        threading.Thread(target=self._fetch, args=(title, artist, key, size),
                         daemon=True).start()

    def _fetch(self, title, artist, key, size):
        try:
            url = find_cover(title, artist)
            if not url:
                self.cover_failed.emit(key)
                return
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            with open(self._cache_path(key), "wb") as f:
                f.write(r.content)
            pix = QPixmap()
            pix.loadFromData(r.content)
            if pix.isNull():
                self.cover_failed.emit(key)
                return
            pix = pix.scaled(size, size,
                             Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                             Qt.TransformationMode.SmoothTransformation)
            type(self)._cache[key] = pix
            self.cover_ready.emit(key, pix)
        except Exception as e:
            print(f"[CoverLoader] {key}: {e}")
            self.cover_failed.emit(key)
        finally:
            self._pending.pop(key, None)