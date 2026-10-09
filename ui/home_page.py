from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
from ui.theme import Colors, Sizes, font
from ui import icons
from ui.cover_loader import CoverLoader


class AlbumCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, item, size=180, parent=None):
        super().__init__(parent)
        self.item = item
        self.setFixedSize(size, size + 60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{ background-color: transparent; border-radius: 12px; }}
            QFrame:hover {{ background-color: {Colors.GLASS_HOVER}; }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(8)

        self.cover = QLabel()
        self.cover.setFixedSize(size - 16, size - 16)
        self.cover.setStyleSheet(f"background-color: {Colors.SURFACE}; border-radius: 8px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setPixmap(icons.svg_pixmap(icons.ICON_MUSIC, Colors.TEXT_SECONDARY, 48))
        v.addWidget(self.cover)

        title = item.get("title", "")
        artist = item.get("artist", "")
        if title:
            self._load_cover(title, artist, size - 16)

        tl = QLabel(title or "Untitled")
        tl.setFont(font(13, "semibold"))
        tl.setStyleSheet(f"color: {Colors.TEXT};")
        v.addWidget(tl)

        al = QLabel(artist)
        al.setFont(font(11))
        al.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        v.addWidget(al)

    def _load_cover(self, title, artist, size):
        loader = CoverLoader(self)
        key = f"{artist} - {title}"

        def on_ready(k, pix):
            if k in (key, key + "__placeholder"):
                self.cover.setPixmap(pix.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation))

        loader.cover_ready.connect(on_ready)
        loader.load(title, artist, size=size, callback_key=key)
        self._loader = loader

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.item)


class HomePage(QScrollArea):
    track_clicked = pyqtSignal(dict)
    album_clicked = pyqtSignal(dict)
    see_all_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.1); border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.v = QVBoxLayout(self.container)
        self.v.setContentsMargins(24, 24, 24, 24)
        self.v.setSpacing(24)

        pt = QLabel("1. HOME")
        pt.setFont(font(11, "bold"))
        pt.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; letter-spacing: 1.5px;")
        self.v.addWidget(pt)

        greeting = QLabel("Good evening,")
        greeting.setFont(font(24, "bold"))
        greeting.setStyleSheet(f"color: {Colors.TEXT};")
        self.v.addWidget(greeting)

        sub = QLabel("Here's what's new for you.")
        sub.setFont(font(12))
        sub.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.v.addWidget(sub)

        self.recently_layout = self._make_section("Recently Played", "recently")
        self.featured_layout = self._make_section("Featured Albums", "featured")

        self.v.addStretch()
        self.setWidget(self.container)

    def _make_section(self, title_text, key):
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        wv = QVBoxLayout(wrapper)
        wv.setContentsMargins(0, 0, 0, 0)
        wv.setSpacing(12)

        header = QHBoxLayout()
        t = QLabel(title_text)
        t.setFont(font(16, "bold"))
        t.setStyleSheet(f"color: {Colors.TEXT};")
        header.addWidget(t)
        header.addStretch()

        sa = QPushButton("See all")
        sa.setFont(font(11))
        sa.setCursor(Qt.CursorShape.PointingHandCursor)
        sa.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {Colors.TEXT_SECONDARY}; padding: 4px 8px;
            }}
            QPushButton:hover {{ color: {Colors.TEXT}; }}
        """)
        sa.clicked.connect(lambda: self.see_all_clicked.emit(key))
        header.addWidget(sa)
        wv.addLayout(header)

        cards = QWidget()
        cards.setStyleSheet("background: transparent;")
        cl = QHBoxLayout(cards)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(16)
        cl.addStretch()
        wv.addWidget(cards)

        self.v.addWidget(wrapper)
        return cl

    def set_recently(self, tracks):
        self._fill(self.recently_layout, tracks, 160)

    def set_featured(self, albums):
        self._fill(self.featured_layout, albums, 180)

    def _fill(self, layout, items, size):
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            e = QLabel("Нет данных")
            e.setFont(font(12))
            e.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 20px;")
            layout.insertWidget(0, e)
            return

        for item in items:
            card = AlbumCard(item, size=size)
            card.clicked.connect(self.album_clicked.emit)
            layout.insertWidget(layout.count() - 1, card)