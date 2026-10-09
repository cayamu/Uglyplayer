from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from ui.theme import Colors, Sizes, font
from ui import icons
from ui.cover_loader import CoverLoader


class TrackRow(QFrame):
    clicked = pyqtSignal(dict)
    play_clicked = pyqtSignal(dict)
    like_clicked = pyqtSignal(dict)
    download_clicked = pyqtSignal(dict)
    plus_clicked = pyqtSignal(dict)

    def __init__(self, track, index=0, liked=False, parent=None):
        super().__init__(parent)
        self.track = track
        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-radius: 8px;
            }}
            QFrame:hover {{ background-color: {Colors.GLASS_HOVER}; }}
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(8, 6, 8, 6)
        h.setSpacing(12)

        num = QLabel(str(index + 1))
        num.setFont(font(12))
        num.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        num.setFixedWidth(22)
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(num)

        self.cover = QLabel()
        self.cover.setFixedSize(Sizes.COVER_TRACK, Sizes.COVER_TRACK)
        self.cover.setStyleSheet(f"background-color: {Colors.SURFACE}; border-radius: 4px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setPixmap(icons.svg_pixmap(icons.ICON_MUSIC, Colors.TEXT_SECONDARY, 18))
        h.addWidget(self.cover)

        self._load_cover(track.get("title", ""), track.get("artist", ""))

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(2)

        title = QLabel(track.get("title", "Unknown"))
        title.setFont(font(13, "semibold"))
        title.setStyleSheet(f"color: {Colors.TEXT};")
        info.addWidget(title)

        artist = QLabel(track.get("artist", ""))
        artist.setFont(font(11))
        artist.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        info.addWidget(artist)
        h.addLayout(info, 3)

        album_lbl = QLabel(track.get("album", track.get("source", "")))
        album_lbl.setFont(font(12))
        album_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        h.addWidget(album_lbl, 2)

        dur = QLabel(track.get("duration", ""))
        dur.setFont(font(12))
        dur.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        dur.setFixedWidth(48)
        dur.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        h.addWidget(dur)

        self.like_btn = self._btn(icons.ICON_HEART, Colors.ACCENT if liked else Colors.TEXT_SECONDARY)
        self.like_btn.clicked.connect(lambda: self.like_clicked.emit(self.track))
        h.addWidget(self.like_btn)

        dl = self._btn(icons.ICON_DOWNLOAD, Colors.TEXT_SECONDARY)
        dl.clicked.connect(lambda: self.download_clicked.emit(self.track))
        h.addWidget(dl)

        pl = self._btn(icons.ICON_PLUS, Colors.TEXT_SECONDARY)
        pl.clicked.connect(lambda: self.plus_clicked.emit(self.track))
        h.addWidget(pl)

        play = self._btn(icons.ICON_PLAY, Colors.TEXT)
        play.clicked.connect(lambda: self.play_clicked.emit(self.track))
        h.addWidget(play)

    def _btn(self, icon_name, color):
        btn = QPushButton()
        btn.setFixedSize(30, 30)
        btn.setIcon(icons.svg_icon(icon_name, color, 14))
        btn.setIconSize(QSize(14, 14))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 15px; }}
            QPushButton:hover {{ background-color: {Colors.GLASS_ACTIVE}; }}
        """)
        return btn

    def _load_cover(self, title, artist):
        if not title:
            return
        loader = CoverLoader(self)
        key = f"{artist} - {title}"

        def on_ready(k, pix):
            if k in (key, key + "__placeholder"):
                self.cover.setPixmap(pix.scaled(
                    Sizes.COVER_TRACK, Sizes.COVER_TRACK,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation))

        loader.cover_ready.connect(on_ready)
        loader.load(title, artist, size=Sizes.COVER_TRACK, callback_key=key)
        self._loader = loader

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.track)