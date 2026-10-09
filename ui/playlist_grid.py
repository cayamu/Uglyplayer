"""
Сетка плейлистов — как в Spotify.
Показывает карточки плейлистов (обложка + имя + кол-во треков).
"""
from PyQt6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
import qtawesome as qta
import os

from ui.icons import ICON_MUSIC, ICON_PLUS, GRAY


class PlaylistCard(QFrame):
    """Карточка одного плейлиста."""
    clicked = pyqtSignal(str)

    def __init__(self, pid, name, cover_path, count, accent="#1DB954"):
        super().__init__()
        self.pid = pid
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(180, 230)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 20);
            }
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        cover = QLabel()
        cover.setFixedSize(160, 160)
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 6px;
        """)

        if cover_path and os.path.exists(cover_path):
            pix = QPixmap(cover_path)
            if not pix.isNull():
                pix = pix.scaled(
                    160, 160,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation)
                cover.setPixmap(pix)
                cover.setStyleSheet("border-radius: 6px;")
            else:
                cover.setPixmap(
                    qta.icon(ICON_MUSIC, color="#555").pixmap(64, 64))
        else:
            cover.setPixmap(
                qta.icon(ICON_MUSIC, color="#555").pixmap(64, 64))

        v.addWidget(cover)

        name_lbl = QLabel(name[:20])
        name_lbl.setStyleSheet(
            "color: #FFFFFF; font-size: 13px; font-weight: 600;")
        name_lbl.setWordWrap(False)
        v.addWidget(name_lbl)

        count_lbl = QLabel(f"{count} треков")
        count_lbl.setStyleSheet("color: #888; font-size: 11px;")
        v.addWidget(count_lbl)

    def mousePressEvent(self, event):
        self.clicked.emit(self.pid)


class PlaylistGrid(QScrollArea):
    """Сетка плейлистов."""
    playlist_opened = pyqtSignal(str)
    playlist_created_requested = pyqtSignal()

    def __init__(self, accent="#1DB954"):
        super().__init__()
        self.accent = accent
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(20)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("Мои плейлисты")
        title.setStyleSheet(
            "color: #FFFFFF; font-size: 28px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("  Создать")
        add_btn.setIcon(qta.icon(ICON_PLUS, color="#FFFFFF"))
        add_btn.setIconSize(QSize(14, 14))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 18px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {accent}; }}
        """)
        add_btn.clicked.connect(self.playlist_created_requested.emit)
        header.addWidget(add_btn)

        self.layout.addLayout(header)

        # Сетка карточек
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(15)
        self.layout.addWidget(self.grid_widget)

        self.layout.addStretch()
        self.setWidget(self.container)

    def set_accent(self, accent: str):
        self.accent = accent

    def render(self, playlists: dict):
        """Перерисовывает сетку. playlists: {pid: {name, cover, tracks}}"""
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not playlists:
            empty = QLabel("Плейлистов пока нет.\nНажми «Создать», чтобы добавить.")
            empty.setStyleSheet(
                "color: #666; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(empty, 0, 0, 1, 3)
            return

        for i, (pid, pl) in enumerate(playlists.items()):
            row = i // 3
            col = i % 3
            card = PlaylistCard(
                pid,
                pl.get("name", "Без названия"),
                pl.get("cover"),
                len(pl.get("tracks", [])),
                accent=self.accent,
            )
            card.clicked.connect(self.playlist_opened.emit)
            self.grid.addWidget(card, row, col)

        self.grid.setColumnStretch(3, 1)