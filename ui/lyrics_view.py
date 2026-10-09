from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
from ui.theme import Colors, Sizes, font
from ui import icons
from ui.cover_loader import CoverLoader


class LyricsLine(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, text, time_ms=0, parent=None):
        super().__init__(text, parent)
        self.time_ms = time_ms
        self.setFont(font(16, "semibold"))
        self.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 6px 0;")
        self.setWordWrap(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_active(self, active):
        if active:
            self.setStyleSheet(f"color: {Colors.TEXT}; padding: 6px 0;")
        else:
            self.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 6px 0;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.time_ms)


class LyricsView(QWidget):
    closed = pyqtSignal()
    line_clicked = pyqtSignal(int)
    toggle_play = pyqtSignal()
    next_track = pyqtSignal()
    prev_track = pyqtSignal()
    seek = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        self.current_index = -1
        self._total_ms = 0

        v = QVBoxLayout(self)
        v.setContentsMargins(40, 24, 40, 24)
        v.setSpacing(20)

        top = QHBoxLayout()
        top.addStretch()

        title = QLabel("NOW PLAYING")
        title.setFont(font(10, "bold"))
        title.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; letter-spacing: 1.5px;")
        top.addWidget(title)
        top.addStretch()

        for icon_name, action in [
            (icons.ICON_SLIDERS, None),
            (icons.ICON_MAXIMIZE, None),
            (icons.ICON_CLOSE, self._close),
        ]:
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setIcon(icons.svg_icon(icon_name, Colors.TEXT_SECONDARY, 14))
            btn.setIconSize(QSize(14, 14))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none; border-radius: 16px;
                }}
                QPushButton:hover {{ background-color: {Colors.GLASS_HOVER}; }}
            """)
            if action:
                btn.clicked.connect(action)
            top.addWidget(btn)

        v.addLayout(top)

        center = QHBoxLayout()
        center.setSpacing(48)

        left = QVBoxLayout()
        left.setSpacing(16)
        left.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cover = QLabel()
        self.cover.setFixedSize(Sizes.COVER_LYRICS_W, Sizes.COVER_LYRICS_H)
        self.cover.setStyleSheet(f"background-color: {Colors.SURFACE}; border-radius: 10px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setPixmap(icons.svg_pixmap(icons.ICON_MUSIC, Colors.TEXT_SECONDARY, 40))
        left.addWidget(self.cover)

        self.track_title = QLabel("—")
        self.track_title.setFont(font(14, "semibold"))
        self.track_title.setStyleSheet(f"color: {Colors.TEXT};")
        self.track_title.setWordWrap(True)
        self.track_title.setMaximumWidth(Sizes.COVER_LYRICS_W)
        left.addWidget(self.track_title)

        self.track_artist = QLabel("—")
        self.track_artist.setFont(font(11))
        self.track_artist.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        left.addWidget(self.track_artist)
        left.addStretch()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 6px; }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.1); border-radius: 3px; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self.lines_widget = QWidget()
        self.lines_widget.setStyleSheet("background: transparent;")
        self.lines_layout = QVBoxLayout(self.lines_widget)
        self.lines_layout.setContentsMargins(0, 40, 0, 40)
        self.lines_layout.setSpacing(6)
        self.lines_layout.addStretch()
        self.scroll.setWidget(self.lines_widget)

        right = QVBoxLayout()
        right.setSpacing(0)
        right.addWidget(self.scroll, 1)
        center.addLayout(left, 1)
        center.addLayout(right, 3)
        v.addLayout(center, 1)

        controls = QHBoxLayout()
        controls.setSpacing(12)
        controls.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_cur = QLabel("0:00")
        self.time_cur.setFont(font(10))
        self.time_cur.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        controls.addWidget(self.time_cur)

        self.progress = QSlider(Qt.Orientation.Horizontal)
        self.progress.setRange(0, 1000)
        self.progress.setFixedWidth(400)
        self.progress.setStyleSheet(self._slider_qss())
        self.progress.sliderReleased.connect(self._on_seek)
        controls.addWidget(self.progress)

        self.time_total = QLabel("0:00")
        self.time_total.setFont(font(10))
        self.time_total.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        controls.addWidget(self.time_total)
        v.addLayout(controls)

        ctrl2 = QHBoxLayout()
        ctrl2.setSpacing(20)
        ctrl2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sh = self._ctrl_btn(icons.ICON_SHUFFLE, 16)
        ctrl2.addWidget(sh)

        prev = self._ctrl_btn(icons.ICON_PREVIOUS, 18, 40)
        prev.clicked.connect(self.prev_track.emit)
        ctrl2.addWidget(prev)

        self.play_btn