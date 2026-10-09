"""
Нижний плеер 88px.
Обложка 56x56, инфо, кнопки, прогресс 350x4, громкость 180x4.
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap

from ui.theme import Colors, Sizes, font
from ui import icons
from ui.cover_loader import CoverLoader


def fmt_time(ms):
    if not ms or ms < 0 or ms > 100_000_000:
        return "0:00"
    s = int(ms // 1000)
    return f"{s // 60}:{s % 60:02d}"


class PlayerBar(QFrame):
    play_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    shuffle_clicked = pyqtSignal()
    repeat_clicked = pyqtSignal()
    lyrics_clicked = pyqtSignal()
    queue_clicked = pyqtSignal()
    like_clicked = pyqtSignal()
    seek = pyqtSignal(int)
    volume_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(Sizes.PLAYER_H)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GLASS_BG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: {Sizes.RADIUS}px;
            }}
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(14, 8, 14, 8)
        h.setSpacing(12)

        # ============ ЛЕВАЯ ============
        left = QHBoxLayout()
        left.setSpacing(12)

        self.cover = QLabel()
        self.cover.setFixedSize(Sizes.COVER_PLAYER, Sizes.COVER_PLAYER)
        self.cover.setStyleSheet(f"""
            background-color: {Colors.SURFACE};
            border-radius: 8px;
        """)
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setPixmap(
            icons.svg_pixmap(icons.ICON_MUSIC, Colors.TEXT_SECONDARY, 24))
        left.addWidget(self.cover)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(2)

        self.title_lbl = QLabel("Ничего не играет")
        self.title_lbl.setFont(font(13, "semibold"))
        self.title_lbl.setStyleSheet(f"color: {Colors.TEXT};")
        info.addWidget(self.title_lbl)

        self.artist_lbl = QLabel("—")
        self.artist_lbl.setFont(font(11))
        self.artist_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY};")
        info.addWidget(self.artist_lbl)

        left.addLayout(info)
        left.addStretch()

        # Like
        self.like_btn = self._icon_btn(icons.ICON_HEART, 16)
        self.like_btn.clicked.connect(self.like_clicked.emit)
        left.addWidget(self.like_btn)

        left_widget = QFrame()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(320)
        left_widget.setStyleSheet("background: transparent; border: none;")
        h.addWidget(left_widget)

        # ============ ЦЕНТР ============
        center = QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(4)

        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shuffle
        sh = self._small_ctrl(icons.ICON_SHUFFLE, 16)
        sh.clicked.connect(self.shuffle_clicked.emit)
        btns.addWidget(sh)

        # Prev
        prev = self._small_ctrl(icons.ICON_PREVIOUS, 18)
        prev.clicked.connect(self.prev_clicked.emit)
        btns.addWidget(prev)

        # Play (48x48, красный)
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(Sizes.PLAY_BTN, Sizes.PLAY_BTN)
        self.play_btn.setIcon(icons.svg_icon(
            icons.ICON_PLAY, "#FFFFFF", 20))
        self.play_btn.setIconSize(QSize(20, 20))
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT};
                border: none;
                border-radius: {Sizes.PLAY_BTN // 2}px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_HOVER};
            }}
        """)
        self.play_btn.clicked.connect(self.play_clicked.emit)
        btns.addWidget(self.play_btn)

        # Next
        nxt = self._small_ctrl(icons.ICON_NEXT, 18)
        nxt.clicked.connect(self.next_clicked.emit)
        btns.addWidget(nxt)

        # Repeat
        rp = self._small_ctrl(icons.ICON_REPEAT, 16)
        rp.clicked.connect(self.repeat_clicked.emit)
        btns.addWidget(rp)

        center.addLayout(btns)

        # Progress
        prog = QHBoxLayout()
        prog.setSpacing(8)
        prog.setContentsMargins(0, 0, 0, 0)

        self.time_cur = QLabel("0:00")
        self.time_cur.setFont(font(10))
        self.time_cur.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY};")
        self.time_cur.setFixedWidth(36)
        self.time_cur.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prog.addWidget(self.time_cur)

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.setFixedWidth(Sizes.PROGRESS_W)
        self.seek_slider.setFixedHeight(14)
        self.seek_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.seek_slider.setStyleSheet(self._slider_qss())
        self.seek_slider.sliderReleased.connect(self._on_seek_end)
        prog.addWidget(self.seek_slider)

        self.time_total = QLabel("0:00")
        self.time_total.setFont(font(10))
        self.time_total.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY};")
        self.time_total.setFixedWidth(36)
        prog.addWidget(self.time_total)

        center.addLayout(prog)

        center_widget = QFrame()
        center_widget.setLayout(center)
        center_widget.setStyleSheet("background: transparent; border: none;")
        h.addWidget(center_widget, 1)

        # ============ ПРАВАЯ ============
        right = QHBoxLayout()
        right.setSpacing(10)

        # Lyrics
        lyrics_btn = self._small_ctrl(icons.ICON_LYRICS, 16)
        lyrics_btn.clicked.connect(self.lyrics_clicked.emit)
        right.addWidget(lyrics_btn)

        # Volume icon
        vol_icon = QPushButton()
        vol_icon.setFixedSize(28, 28)
        vol_icon.setIcon(icons.svg_icon(
            icons.ICON_VOLUME, Colors.TEXT_SECONDARY, 16))
        vol_icon.setIconSize(QSize(16, 16))
        vol_icon.setStyleSheet("""
            QPushButton { background: transparent; border: none; }
        """)
        right.addWidget(vol_icon)

        # Volume slider
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(Sizes.VOLUME_W)
        self.vol_slider.setFixedHeight(14)
        self.vol_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vol_slider.setStyleSheet(self._slider_qss())
        self.vol_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit(v / 100))
        right.addWidget(self.vol_slider)

        # Queue
        queue_btn = self._small_ctrl(icons.ICON_QUEUE, 16)
        queue_btn.clicked.connect(self.queue_clicked.emit)
        right.addWidget(queue_btn)

        right_widget = QFrame()
        right_widget.setLayout(right)
        right_widget.setFixedWidth(320)
        right_widget.setStyleSheet("background: transparent; border: none;")
        h.addWidget(right_widget)

    def _small_ctrl(self, icon_name: str, size: int = 16) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(32, 32)
        btn.setIcon(icons.svg_icon(icon_name, Colors.TEXT_SECONDARY, size))
        btn.setIconSize(QSize(size, size))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GLASS_HOVER};
            }}
        """)
        return btn

    def _icon_btn(self, icon_name: str, size: int) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(28, 28)
        btn.setIcon(icons.svg_icon(icon_name, Colors.TEXT_SECONDARY, size))
        btn.setIconSize(QSize(size, size))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GLASS_HOVER};
            }}
        """)
        return btn

    def _slider_qss(self):
        return f"""
            QSlider::groove:horizontal {{
                background: rgba(255, 255, 255, 0.1);
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                width: 10px;
                height: 10px;
                margin: -3px 0;
                border-radius: 5px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {Colors.ACCENT};
            }}
            QSlider::sub-page:horizontal {{
                background: {Colors.ACCENT};
                border-radius: 2px;
            }}
        """

    def _on_seek_end(self):
        self.seek.emit(self.seek_slider.value())

    # ============ API ============
    def set_track(self, title: str, artist: str, cover_path: str = None):
        self.title_lbl.setText(title or "—")
        self.artist_lbl.setText(artist or "—")

        if cover_path:
            pix = QPixmap(cover_path)
            if not pix.isNull():
                pix = pix.scaled(
                    Sizes.COVER_PLAYER, Sizes.COVER_PLAYER,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation)
                self.cover.setPixmap(pix)
                return

        # Загрузка обложки
        if title:
            loader = CoverLoader(self)
            key = f"{artist} - {title}"

            def on_ready(k, pix):
                if k in (key, key + "__placeholder"):
                    self.cover.setPixmap(pix.scaled(
                        Sizes.COVER_PLAYER, Sizes.COVER_PLAYER,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation))

            loader.cover_ready.connect(on_ready)
            loader.load(title, artist, size=Sizes.COVER_PLAYER,
                        callback_key=key)
            self._loader = loader

    def set_playing(self, playing: bool):
        icon = icons.ICON_PAUSE if playing else icons.ICON_PLAY
        self.play_btn.setIcon(icons.svg_icon(icon, "#FFFFFF", 20))

    def set_position(self, ms: int, total: int = 0):
        if total > 0:
            self.seek_slider.setRange(0, total)
        self.seek_slider.setValue(ms)
        self.time_cur.setText(fmt_time(ms))

    def set_duration(self, ms: int):
        self.seek_slider.setRange(0, ms)
        self.time_total.setText(fmt_time(ms))

    def set_liked(self, liked: bool):
        color = Colors.ACCENT if liked else Colors.TEXT_SECONDARY
        self.like_btn.setIcon(icons.svg_icon(icons.ICON_HEART, color, 16))