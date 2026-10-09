from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap
from ui.theme import Colors, Sizes, font
from ui import icons
from ui.cover_loader import CoverLoader


class PlaylistRow(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, pid, name, count, cover_path=None, parent=None):
        super().__init__(parent)
        self.pid = pid
        self.setFixedHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{ background-color: transparent; border-radius: 10px; }}
            QFrame:hover {{ background-color: {Colors.GLASS_HOVER}; }}
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(8, 6, 8, 6)
        h.setSpacing(10)

        self.cover = QLabel()
        self.cover.setFixedSize(Sizes.COVER_TRACK, Sizes.COVER_TRACK)
        self.cover.setStyleSheet(f"background-color: {Colors.SURFACE}; border-radius: 6px;")
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setPixmap(icons.svg_pixmap(icons.ICON_MUSIC, Colors.TEXT_SECONDARY, 18))
        h.addWidget(self.cover)

        if cover_path and not QPixmap(cover_path).isNull():
            self.cover.setPixmap(QPixmap(cover_path).scaled(
                Sizes.COVER_TRACK, Sizes.COVER_TRACK,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation))
        elif name:
            self._load_cover(name)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(2)

        name_lbl = QLabel(name)
        name_lbl.setFont(font(13, "semibold"))
        name_lbl.setStyleSheet(f"color: {Colors.TEXT};")
        info.addWidget(name_lbl)

        cnt = QLabel(f"{count} tracks")
        cnt.setFont(font(11))
        cnt.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        info.addWidget(cnt)
        h.addLayout(info, 1)

        more = QPushButton()
        more.setFixedSize(24, 24)
        more.setIcon(icons.svg_icon(icons.ICON_MORE, Colors.TEXT_SECONDARY, 14))
        more.setIconSize(QSize(14, 14))
        more.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 12px; }}
            QPushButton:hover {{ background-color: {Colors.GLASS_ACTIVE}; }}
        """)
        h.addWidget(more)

    def _load_cover(self, name):
        loader = CoverLoader(self)
        key = f"playlist - {name}"

        def on_ready(k, pix):
            if k in (key, key + "__placeholder"):
                self.cover.setPixmap(pix.scaled(
                    Sizes.COVER_TRACK, Sizes.COVER_TRACK,
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation))

        loader.cover_ready.connect(on_ready)
        loader.load(name, "playlist", size=Sizes.COVER_TRACK, callback_key=key)
        self._loader = loader

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.pid)


class LibraryPanel(QFrame):
    playlist_clicked = pyqtSignal(str)
    search_changed = pyqtSignal(str)
    tab_changed = pyqtSignal(str)
    new_playlist_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(Sizes.LIBRARY_W)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GLASS_BG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: {Sizes.RADIUS}px;
            }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(14, 14, 14, 14)
        v.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("YOUR LIBRARY")
        title.setFont(font(10, "bold"))
        title.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; letter-spacing: 1.5px;")
        header.addWidget(title)
        header.addStretch()

        add = QPushButton()
        add.setFixedSize(26, 26)
        add.setIcon(icons.svg_icon(icons.ICON_PLUS, Colors.TEXT, 14))
        add.setIconSize(QSize(14, 14))
        add.setCursor(Qt.CursorShape.PointingHandCursor)
        add.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 13px; }}
            QPushButton:hover {{ background-color: {Colors.GLASS_HOVER}; }}
        """)
        add.clicked.connect(self.new_playlist_clicked.emit)
        header.addWidget(add)
        v.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search your library...")
        self.search.setFixedHeight(Sizes.SEARCH_H)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.GLASS_BG_STRONG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: {Sizes.SEARCH_H // 2}px;
                padding: 0 14px;
                color: {Colors.TEXT};
                font-size: 12px;
            }}
            QLineEdit:focus {{ border: 1px solid {Colors.ACCENT}; }}
        """)
        self.search.textChanged.connect(self.search_changed.emit)
        v.addWidget(self.search)

        tabs = QHBoxLayout()
        tabs.setSpacing(16)
        self.tab_playlists = QPushButton("Playlists")
        self.tab_liked = QPushButton("Liked Tracks")
        for btn, key in [(self.tab_playlists, "playlists"), (self.tab_liked, "liked")]:
            btn.setFont(font(12, "semibold"))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._on_tab(k))
            tabs.addWidget(btn)
        tabs.addStretch()
        v.addLayout(tabs)

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

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(2)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.list_widget)
        v.addWidget(self.scroll, 1)

        self.current_tab = "playlists"
        self._update_tabs()

    def _on_tab(self, key):
        self.current_tab = key
        self._update_tabs()
        self.tab_changed.emit(key)

    def _update_tabs(self):
        for btn, key in [(self.tab_playlists, "playlists"), (self.tab_liked, "liked")]:
            if key == self.current_tab:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {Colors.TEXT}; padding: 4px 0;
                        border-bottom: 2px solid {Colors.ACCENT};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        color: {Colors.TEXT_SECONDARY}; padding: 4px 0;
                    }}
                    QPushButton:hover {{ color: {Colors.TEXT}; }}
                """)

    def set_playlists(self, playlists):
        self._clear()
        if not playlists:
            e = QLabel("No playlists yet")
            e.setFont(font(12))
            e.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 20px;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.insertWidget(0, e)
            return
        for pl in playlists:
            row = PlaylistRow(pl.get("id", ""), pl.get("name", "Untitled"),
                              pl.get("count", 0), pl.get("cover"))
            row.clicked.connect(self.playlist_clicked.emit)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def set_liked(self, tracks):
        self._clear()
        if not tracks:
            e = QLabel("No liked tracks")
            e.setFont(font(12))
            e.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 20px;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.insertWidget(0, e)
            return
        for t in tracks:
            row = PlaylistRow(t.get("title", ""), t.get("title", "Untitled"),
                              0, t.get("cover"))
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def _clear(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()