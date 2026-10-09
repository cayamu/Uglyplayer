"""
UglyPlayer — тема. ВСЕ обводки убраны.
"""
import os
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QGraphicsBlurEffect, QWidget
from PyQt6.QtCore import Qt

from config import ASSETS_DIR


class Colors:
    BG = "#050607"
    SURFACE = "#17191B"
    BORDER = "#2A2D31"
    ACCENT = "#F04444"
    ACCENT_HOVER = "#FF5C5C"
    TEXT = "#E8EAED"
    TEXT_SECONDARY = "#898D92"
    TEXT_DISABLED = "#4A4C50"
    GLASS_BG = "rgba(255, 255, 255, 0.04)"
    GLASS_BG_STRONG = "rgba(255, 255, 255, 0.06)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.09)"
    GLASS_HOVER = "rgba(255, 255, 255, 0.08)"
    GLASS_ACTIVE = "rgba(255, 255, 255, 0.12)"


class Sizes:
    WINDOW_W = 1440
    WINDOW_H = 900
    SIDEBAR_W = 72
    LIBRARY_W = 260
    LYRICS_W = 320
    PLAYER_H = 88
    SEARCH_H = 42
    COVER_ALBUM = 280
    COVER_LYRICS_W = 140
    COVER_LYRICS_H = 180
    COVER_PLAYER = 56
    COVER_TRACK = 40
    PLAY_BTN = 48
    CTRL_BTN = 36
    CTRL_ICON = 20
    NAV_BTN = 48
    NAV_ICON = 22
    PROGRESS_W = 350
    VOLUME_W = 180
    RADIUS = 20
    RADIUS_SMALL = 12
    RADIUS_LARGE = 24
    PADDING = 16


class Fonts:
    FAMILY = "Inter Variable"
    H1 = 20
    H2 = 16
    BODY = 14
    SMALL = 12
    TINY = 10


def load_fonts():
    fonts_dir = os.path.join(ASSETS_DIR, "fonts")
    if not os.path.exists(fonts_dir):
        return
    for f in os.listdir(fonts_dir):
        if f.lower().endswith((".otf", ".ttf")):
            QFontDatabase.addApplicationFont(os.path.join(fonts_dir, f))
    print(f"[Fonts] OK")


def font(size: int = 14, weight: str = "regular") -> QFont:
    f = QFont("Inter Variable")
    if not f.exactMatch():
        f = QFont("Segoe UI")
    f.setPointSize(size)
    if weight == "bold":
        f.setWeight(QFont.Weight.Bold)
    elif weight == "semibold":
        f.setWeight(QFont.Weight.DemiBold)
    elif weight == "medium":
        f.setWeight(QFont.Weight.Medium)
    return f


def apply_blur(widget: QWidget, radius: int = 20):
    eff = QGraphicsBlurEffect(widget)
    eff.setBlurRadius(radius)
    eff.setBlurHints(QGraphicsBlurEffect.BlurHint.PerformanceHint)
    widget.setGraphicsEffect(eff)


QSS = f"""
* {{ outline: 0px; }}
*:focus {{ outline: none; border: none; }}

QMainWindow, QWidget {{
    background-color: {Colors.BG};
    color: {Colors.TEXT};
    font-family: "Inter Variable", "Segoe UI", Arial;
}}

QLabel {{
    color: {Colors.TEXT};
    background: transparent;
    border: none;
    outline: none;
    padding: 0px;
}}
QLabel:focus {{ outline: none; border: none; }}
QLabel[secondary="true"] {{ color: {Colors.TEXT_SECONDARY}; }}

QPushButton {{
    background-color: transparent;
    border: none;
    outline: none;
    color: {Colors.TEXT};
    padding: 4px 8px;
    border-radius: {Sizes.RADIUS_SMALL}px;
}}
QPushButton:hover {{ background-color: {Colors.GLASS_HOVER}; }}
QPushButton:pressed {{ background-color: {Colors.GLASS_ACTIVE}; }}
QPushButton:focus {{ outline: none; border: none; }}
QPushButton[accent="true"] {{
    background-color: {Colors.ACCENT};
    color: #FFFFFF;
    border-radius: 24px;
}}
QPushButton[accent="true"]:hover {{ background-color: {Colors.ACCENT_HOVER}; }}

QLineEdit {{
    background-color: {Colors.GLASS_BG_STRONG};
    border: 1px solid {Colors.GLASS_BORDER};
    border-radius: 20px;
    padding: 0 16px;
    color: {Colors.TEXT};
    outline: none;
}}
QLineEdit:focus {{ border: 1px solid {Colors.ACCENT}; }}

QSlider::groove:horizontal {{
    background: rgba(255, 255, 255, 0.1);
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: #FFFFFF;
    width: 10px; height: 10px;
    margin: -3px 0; border-radius: 5px;
    border: none;
}}
QSlider::handle:horizontal:hover {{ background: {Colors.ACCENT}; }}
QSlider::sub-page:horizontal {{
    background: {Colors.ACCENT};
    border-radius: 2px;
}}
QSlider:focus {{ outline: none; }}

QScrollBar:vertical {{
    background: transparent; width: 8px; border: none;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: rgba(255, 255, 255, 0.2); }}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0px; border: none; }}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{ background: none; }}

QCheckBox {{
    color: {Colors.TEXT}; outline: none; border: none; spacing: 8px;
}}
QCheckBox::indicator {{
    width: 20px; height: 20px;
    border-radius: 10px;
    background: transparent;
    border: 2px solid {Colors.TEXT_SECONDARY};
}}
QCheckBox::indicator:checked {{
    background-color: {Colors.ACCENT};
    border-color: {Colors.ACCENT};
}}

QComboBox {{
    background-color: {Colors.GLASS_BG};
    border: 1px solid {Colors.GLASS_BORDER};
    border-radius: 8px;
    padding: 0 12px;
    color: {Colors.TEXT};
    min-height: 34px;
    outline: none;
}}
QComboBox:focus {{ border: 1px solid {Colors.ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.GLASS_BORDER};
    color: {Colors.TEXT};
}}

QFrame[glass="true"] {{
    background-color: {Colors.GLASS_BG};
    border: 1px solid {Colors.GLASS_BORDER};
    border-radius: {Sizes.RADIUS}px;
}}
QFrame {{ border: none; }}
"""


def get_app_qss() -> str:
    return QSS