from PyQt6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsOpacityEffect, QDialog,
    QInputDialog, QFileDialog
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QSize
)
from PyQt6.QtGui import QPixmap
import qtawesome as qta

from ui.icons import (
    ICON_PLAY, ICON_DOWNLOAD, ICON_MUSIC, ICON_TRASH,
    WHITE, GRAY, ACCENT, BLACK
)
from ui.cover_loader import CoverLoader
from ui.scaling import px, pt, font


class TrackList(QScrollArea):
    play_requested = pyqtSignal(dict)
    download_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(int)

    def __init__(self, playlist_manager, accent="#1DB954"):
        super().__init__()
        self.accent = accent
        self._playlist_manager = playlist_manager
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(px(6))
        self.layout.addStretch()

        self.setWidget(self.container)

        self.cover_loader = CoverLoader(self)
        self.cover_loader.cover_ready.connect(self._on_cover_ready)
        self.cover_loader.cover_failed.connect(self._on_cover_failed)

        self._cover_widgets = {}

    def set_accent(self, accent: str):
        self.accent = accent

    def clear(self):
        self._cover_widgets.clear()
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_loading(self, text):
        self.clear()
        lbl = QLabel(text)
        lbl.setFont(font(14))
        lbl.setStyleSheet("color: #666; padding: 60px; background: transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.insertWidget(0, lbl)
        self._animate_widget(lbl, 0)

    def show_empty(self, title, text):
        self.clear()
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        v = QVBoxLayout(container)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setSpacing(px(12))

        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            qta.icon("fa6s.music", color="#333").pixmap(px(64), px(64)))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setFont(font(20, bold=True))
        title_lbl.setStyleSheet("color: #FFFFFF; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(title_lbl)

        text_lbl = QLabel(text)
        text_lbl.setFont(font(14))
        text_lbl.setStyleSheet("color: #666; background: transparent;")
        text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_lbl.setWordWrap(True)
        text_lbl.setMaximumWidth(px(400))
        v.addWidget(text_lbl)

        self.layout.insertWidget(0, container)
        self._animate_widget(container, 0)

    def add_track(self, track, index=0, show_like=True, show_plus=True,
                  show_download=True):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 20, 140);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 12);
            }
            QFrame:hover {
                background-color: rgba(40, 40, 40, 180);
                border: 1px solid rgba(255, 255, 255, 25);
            }
        """)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        h = QHBoxLayout(card)
        h.setContentsMargins(px(14), px(10), px(14), px(10))
        h.setSpacing(px(14))

        num = QLabel(str(index + 1))
        num.setFont(font(14, bold=True))
        num.setStyleSheet("color: #666; background: transparent;")
        num.setFixedWidth(px(30))
        num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(num)

        cover = QLabel()
        cover.setFixedSize(px(56), px(56))
        cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setStyleSheet("""
            background-color: rgba(255,255,255,15);
            border-radius: 6px;
        """)

        cover_url = track.get("cover")
        if cover_url:
            cover.setPixmap(
                qta.icon(ICON_MUSIC, color="#555").pixmap(px(24), px(24)))
            self._cover_widgets[cover_url] = cover
            self.cover_loader.load(cover_url, size=px(56))
        else:
            cover.setPixmap(
                qta.icon(ICON_MUSIC, color="#555").pixmap(px(24), px(24)))

        h.addWidget(cover)

        info = QVBoxLayout()
        info.setSpacing(px(2))

        title = QLabel(track["title"])
        title.setFont(font(14, bold=True))
        title.setStyleSheet("color: #FFFFFF; background: transparent;")
        title.setWordWrap(False)
        info.addWidget(title)

        artist_text = track.get("artist", "")
        if track.get("duration"):
            artist_text += f"  ·  {track['duration']}"
        if track.get("source"):
            artist_text += f"  ·  {track['source']}"

        artist = QLabel(artist_text)
        artist.setFont(font(11))
        artist.setStyleSheet("color: #888; background: transparent;")
        info.addWidget(artist)

        h.addLayout(info, 1)

        # LIKE
        if show_like:
            like_btn = QPushButton()
            is_liked = self._playlist_manager.is_liked(track["title"])
            icon_color = "#e63946" if is_liked else GRAY
            like_btn.setIcon(qta.icon("fa6s.heart", color=icon_color))
            like_btn.setIconSize(QSize(px(16), px(16)))
            like_btn.setFixedSize(px(40), px(36))
            like_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            like_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,10);
                    border: none;
                    border-radius: 18px;
                    padding: 0px;
                }
                QPushButton:hover { background-color: rgba(255,255,255,20); }
            """)
            like_btn.clicked.connect(
                lambda: self._toggle_like(track, like_btn))
            h.addWidget(like_btn)

        # PLUS
        if show_plus:
            plus_btn = QPushButton()
            plus_btn.setIcon(qta.icon("fa6s.plus", color=GRAY))
            plus_btn.setIconSize(QSize(px(16), px(16)))
            plus_btn.setFixedSize(px(40), px(36))
            plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            plus_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,10);
                    border: none;
                    border-radius: 18px;
                    padding: 0px;
                }
                QPushButton:hover { background-color: rgba(255,255,255,20); }
            """)
            plus_btn.clicked.connect(
                lambda: self._open_playlist_dialog(track))
            h.addWidget(plus_btn)

        # PLAY
        play_btn = QPushButton()
        play_btn.setIcon(qta.icon(ICON_PLAY, color=BLACK))
        play_btn.setIconSize(QSize(px(16), px(16)))
        play_btn.setFixedSize(px(42), px(38))
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent};
                border: none;
                border-radius: 19px;
                padding: 0px;
            }}
            QPushButton:hover {{ background-color: {self.accent}; }}
        """)
        play_btn.clicked.connect(
            lambda: self.play_requested.emit(track))
        h.addWidget(play_btn)

        # DOWNLOAD
        if show_download:
            dl_btn = QPushButton()
            dl_btn.setIcon(qta.icon(ICON_DOWNLOAD, color=GRAY))
            dl_btn.setIconSize(QSize(px(16), px(16)))
            dl_btn.setFixedSize(px(42), px(38))
            dl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            dl_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255,255,255,10);
                    border: none;
                    border-radius: 19px;
                    padding: 0px;
                }
                QPushButton:hover { background-color: rgba(255,255,255,20); }
            """)
            dl_btn.clicked.connect(
                lambda: self.download_requested.emit(track))
            h.addWidget(dl_btn)

        self.layout.insertWidget(self.layout.count() - 1, card)
        delay = min(index * 25, 300)
        self._animate_widget(card, delay)

    def _toggle_like(self, track, btn):
        is_now_liked = self._playlist_manager.toggle_like(track)
        icon_color = "#e63946" if is_now_liked else GRAY
        btn.setIcon(qta.icon("fa6s.heart", color=icon_color))

    def _open_playlist_dialog(self, track):
        dlg = QDialog(self)
        dlg.setWindowTitle("Добавить в плейлист")
        dlg.setFixedSize(px(380), px(440))
        dlg.setStyleSheet("""
            QDialog { background: #0a0a0a; }
            QLabel { color: white; font-size: 13px; background: transparent; }
            QPushButton {
                background: #161616; color: white; border: 1px solid #222;
                border-radius: 8px; padding: 10px 14px; text-align: left;
                font-size: 13px;
            }
            QPushButton:hover { background: #222; }
            QPushButton#new {
                background: #1DB954; border: none; color: white;
                font-weight: 600; text-align: center;
            }
            QPushButton#new:hover { background: #1ED760; }
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(px(15), px(15), px(15), px(15))
        layout.setSpacing(px(10))

        title = QLabel(f"Трек: {track['title']}")
        title.setStyleSheet(
            "font-weight: 600; font-size: 14px; background: transparent;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        v = QVBoxLayout(inner)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(px(4))

        playlists = self._playlist_manager.get_playlists()

        def add_to(pid):
            self._playlist_manager.add_to_playlist(pid, track)
            dlg.accept()

        if not playlists:
            empty = QLabel("Плейлистов пока нет.\nСоздай первый!")
            empty.setStyleSheet("color: #666; padding: 20px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(empty)
        else:
            for pid, pl in playlists.items():
                btn = QPushButton(f"  {pl['name']}  ·  {len(pl['tracks'])}")
                btn.setIcon(qta.icon("fa6s.list", color="#B3B3B3"))
                btn.setIconSize(QSize(px(16), px(16)))
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _, p=pid: add_to(p))
                v.addWidget(btn)

        v.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        def create_new():
            name, ok = QInputDialog.getText(
                dlg, "Новый плейлист", "Название плейлиста:")
            if not ok or not name.strip():
                return
            cover_path, _ = QFileDialog.getOpenFileName(
                dlg, "Обложка плейлиста (можно отменить)", "",
                "Картинки (*.png *.jpg *.jpeg *.webp *.bmp)")
            if not cover_path:
                cover_path = None
            pid = self._playlist_manager.create_playlist(
                name.strip(), cover_path=cover_path)
            add_to(pid)

        new_btn = QPushButton("  Создать новый плейлист")
        new_btn.setObjectName("new")
        new_btn.setIcon(qta.icon("fa6s.plus", color="white"))
        new_btn.setIconSize(QSize(px(16), px(16)))
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(create_new)
        layout.addWidget(new_btn)

        dlg.exec()

    def _on_cover_ready(self, url, pixmap):
        if url in self._cover_widgets:
            label = self._cover_widgets[url]
            try:
                label.setPixmap(pixmap)
                label.setStyleSheet("""
                    background-color: rgba(255,255,255,15);
                    border-radius: 6px;
                """)
            except RuntimeError:
                pass
            del self._cover_widgets[url]

    def _on_cover_failed(self, url):
        if url in self._cover_widgets:
            del self._cover_widgets[url]

    def _animate_widget(self, widget, delay_ms):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(250)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        if delay_ms > 0:
            QTimer.singleShot(delay_ms, anim.start)
        else:
            anim.start()

        widget._anim = anim