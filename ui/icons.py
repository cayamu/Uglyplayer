import os
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer

from config import ASSETS_DIR


ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
_pixmap_cache = {}
DPI_SCALE = 3


def _render_svg(name: str, size: int, color: str) -> QPixmap:
    key = (name, size, color)
    if key in _pixmap_cache:
        return _pixmap_cache[key]

    path = os.path.join(ICONS_DIR, f"{name}.svg")
    if not os.path.exists(path):
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        _pixmap_cache[key] = pix
        return pix

    big = size * DPI_SCALE
    renderer = QSvgRenderer(path)
    pix = QPixmap(big, big)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(p)
    p.end()

    tinted = QPixmap(big, big)
    tinted.fill(Qt.GlobalColor.transparent)
    p2 = QPainter(tinted)
    p2.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p2.drawPixmap(0, 0, pix)
    p2.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    p2.fillRect(tinted.rect(), QColor(color))
    p2.end()

    final = tinted.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    _pixmap_cache[key] = final
    return final


def svg_icon(name: str, color: str = "#E8EAED", size: int = 20) -> QIcon:
    return QIcon(_render_svg(name, size, color))


def svg_pixmap(name: str, color: str = "#E8EAED", size: int = 20) -> QPixmap:
    return _render_svg(name, size, color)


ICON_HOME = "home"
ICON_SEARCH = "search"
ICON_LIBRARY = "library"
ICON_SETTINGS = "settings"
ICON_HEART = "heart"
ICON_LIST = "list"
ICON_LIST_MUSIC = "list-music"
ICON_SHUFFLE = "shuffle"
ICON_REPEAT = "repeat"
ICON_PREVIOUS = "previous"
ICON_NEXT = "next"
ICON_PLAY = "play"
ICON_PAUSE = "pause"
ICON_VOLUME = "volume"
ICON_VOLUME_MUTED = "volume-muted"
ICON_LYRICS = "lyrics"
ICON_FOLDER = "folder"
ICON_CLOCK = "clock"
ICON_MORE = "more"
ICON_CLOSE = "close"
ICON_CHECK = "check"
ICON_MONITOR = "monitor"
ICON_QUEUE = "queue"
ICON_DOWNLOAD = "download"
ICON_UPLOAD = "upload"
ICON_FILE_AUDIO = "file-audio"
ICON_DISC = "disc"
ICON_SLIDERS = "sliders"
ICON_MAXIMIZE = "maximize"
ICON_MINIMIZE = "minimize"
ICON_PLAYLISTS = "playlists"
ICON_MUSIC = "music"
ICON_PLUS = "plus"
ICON_MINUS = "minus"
ICON_TRASH = "trash"
ICON_EDIT = "edit"
ICON_WIFI = "wifi"
ICON_BLUETOOTH = "bluetooth"
ICON_HEADPHONES = "headphones"
ICON_KEYBOARD = "keyboard"
ICON_INFO = "info"