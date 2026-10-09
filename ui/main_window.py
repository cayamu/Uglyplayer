"""
Главное окно — сборка всего + автоплейлист + фоны.
"""
import os
import threading
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QSize, QTimer
from PyQt6.QtGui import QPixmap

from ui.theme import Colors, Sizes, font, get_app_qss, load_fonts
from ui.sidebar import Sidebar
from ui.library_panel import LibraryPanel
from ui.home_page import HomePage
from ui.search_page import SearchPage
from ui.settings_page import SettingsPage
from ui.lyrics_view import LyricsView
from ui.player_bar import PlayerBar

from player import Player
from search_engine import search_tracks
from playlist_manager import PlaylistManager
from config import BACKGROUNDS_DIR


class SignalBus(QObject):
    search_done = pyqtSignal(list)
    search_error = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UglyPlayer")
        self.resize(Sizes.WINDOW_W, Sizes.WINDOW_H)
        self.setMinimumSize(1100, 700)

        self.setStyleSheet(get_app_qss())

        # Логика
        self.player = Player()
        self.pm = PlaylistManager()
        self.bus = SignalBus()

        # ============ АВТОПЛЕЙЛИСТ ============
        self._queue = []           # список треков (очередь)
        self._current_index = -1   # текущий
        self._current_track = None

        self.bus.search_done.connect(self._on_search_done)
        self.bus.search_error.connect(lambda e: print(f"[Search] {e}"))

        self.player.position_changed.connect(self._on_position)
        self.player.duration_changed.connect(self._on_duration)
        self.player.state_changed.connect(self._on_state)
        self.player.track_ended.connect(self._play_next)   # АВТОПЕРЕКЛЮЧЕНИЕ

        self._build_ui()
        self._connect_signals()
        self._refresh_playlists()

        # Фон
        self._load_background()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setStyleSheet(f"background-color: {Colors.BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(12)

        self.sidebar = Sidebar()
        top.addWidget(self.sidebar)

        self.library = LibraryPanel()
        top.addWidget(self.library)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        self.page_home = HomePage()
        self.page_search = SearchPage()
        self.page_settings = SettingsPage()
        self.page_lyrics = LyricsView()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_search)
        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_lyrics)

        main_frame = QFrame()
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.GLASS_BG};
                border: 1px solid {Colors.GLASS_BORDER};
                border-radius: {Sizes.RADIUS}px;
            }}
        """)
        mv = QVBoxLayout(main_frame)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.addWidget(self.stack)
        top.addWidget(main_frame, 1)

        root.addLayout(top, 1)

        self.player_bar = PlayerBar()
        root.addWidget(self.player_bar)

    # ==================== ФОН ====================
    def _load_background(self):
        """Загружает фон из assets/backgrounds/BG_DARK.png."""
        candidates = [
            "BG_DARK.png",
            "BG_MAIN_01.png",
            "BG_MAIN_02.png",
            "BG_RED_GLOW.png",
            "BG_TEXTURE.png",
        ]

        bg_path = None
        for name in candidates:
            path = os.path.join(BACKGROUNDS_DIR, name)
            if os.path.exists(path):
                bg_path = path
                break

        if not bg_path:
            print("[BG] Фон не найден")
            return

        try:
            central = self.centralWidget()
            pix = QPixmap(bg_path)

            # Устанавливаем как фон через QSS
            path_str = bg_path.replace("\\", "/")
            central.setStyleSheet(f"""
                QWidget#centralWidget {{
                    background-image: url('{path_str}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                }}
            """)
            print(f"[BG] Фон: {os.path.basename(bg_path)}")
        except Exception as e:
            print(f"[BG] Ошибка: {e}")

    def _connect_signals(self):
        self.sidebar.nav_clicked.connect(self._on_nav)

        self.library.playlist_clicked.connect(self._on_playlist_clicked)
        self.library.tab_changed.connect(self._on_library_tab)
        self.library.new_playlist_clicked.connect(self._on_new_playlist)

        self.page_search.search_requested.connect(self._on_search)
        self.page_search.track_clicked.connect(self._play_track)
        self.page_search.like_clicked.connect(self._on_like)
        self.page_search.download_clicked.connect(self._on_download)

        self.page_home.album_clicked.connect(self._on_album_clicked)
        self.page_home.see_all_clicked.connect(lambda k: print(f"[SeeAll] {k}"))

        self.player_bar.play_clicked.connect(self.player.toggle_pause)
        self.player_bar.seek.connect(self.player.seek)
        self.player_bar.volume_changed.connect(self.player.set_volume)
        self.player_bar.lyrics_clicked.connect(self._toggle_lyrics)
        self.player_bar.like_clicked.connect(self._on_like_current)
        self.player_bar.next_clicked.connect(self._play_next)     # АВТО
        self.player_bar.prev_clicked.connect(self._play_prev)     # АВТО

        self.page_lyrics.closed.connect(self._toggle_lyrics)
        self.page_lyrics.line_clicked.connect(self.player.seek)
        self.page_lyrics.toggle_play.connect(self.player.toggle_pause)
        self.page_lyrics.seek.connect(self.player.seek)
        self.page_lyrics.next_track.connect(self._play_next)
        self.page_lyrics.prev_track.connect(self._play_prev)

    # ==================== NAV ====================
    def _on_nav(self, key: str):
        if key == "home":
            self.stack.setCurrentWidget(self.page_home)
        elif key == "search":
            self.stack.setCurrentWidget(self.page_search)
        elif key == "library":
            self.stack.setCurrentWidget(self.page_home)
        elif key == "settings":
            self.stack.setCurrentWidget(self.page_settings)

    def _on_library_tab(self, tab: str):
        if tab == "liked":
            self.library.set_liked(self.pm.get_liked())
        else:
            self._refresh_playlists()

    def _refresh_playlists(self):
        try:
            playlists = self.pm.get_playlists()
            items = []
            for pid, pl in (playlists or {}).items():
                items.append({
                    "id": pid,
                    "name": pl.get("name", "Untitled"),
                    "count": len(pl.get("tracks", [])),
                    "cover": pl.get("cover"),
                })
            self.library.set_playlists(items)
        except Exception as e:
            print(f"[Library] err: {e}")
            self.library.set_playlists([])

    def _on_playlist_clicked(self, pid: str):
        print(f"[Library] Playlist: {pid}")

    def _on_new_playlist(self):
        print("[Library] New playlist")

    # ==================== SEARCH ====================
    def _on_search(self, query: str):
        print(f"[Search] {query}")
        threading.Thread(
            target=self._do_search, args=(query,), daemon=True
        ).start()

    def _do_search(self, query: str):
        try:
            tracks = search_tracks(query, limit=30)
            self.bus.search_done.emit(tracks)
        except Exception as e:
            self.bus.search_error.emit(str(e))

    def _on_search_done(self, tracks: list):
        self.page_search.show_results(
            tracks, query=self.page_search.search.text())

    # ==================== PLAY + АВТОПЛЕЙЛИСТ ====================
    def _play_track(self, track: dict):
        url = track.get("url") or track.get("preview")
        if not url:
            print("[Play] Нет URL")
            return

        # Сохраняем очередь из текущих результатов поиска
        if hasattr(self.page_search, "_tracks"):
            self._queue = list(self.page_search._tracks)
        else:
            self._queue = [track]

        # Находим индекс
        try:
            self._current_index = next(
                i for i, t in enumerate(self._queue)
                if t.get("title") == track.get("title")
            )
        except StopIteration:
            self._current_index = 0

        self._play_internal(track)

    def _play_internal(self, track: dict):
        url = track.get("url") or track.get("preview")
        if not url:
            return

        print(f"[Play] {track.get('title')} — {track.get('artist')}")
        self.player.play_url(url)
        self._current_track = track

        self.player_bar.set_track(
            track.get("title", "—"),
            track.get("artist", "—"),
            track.get("cover"),
        )
        self.page_lyrics.set_track(track)

        try:
            liked = self.pm.is_liked(track.get("title", ""))
            self.player_bar.set_liked(liked)
        except Exception:
            pass

        threading.Thread(
            target=self._load_lyrics, args=(track,), daemon=True
        ).start()

    def _play_next(self):
        """Следующий трек из очереди."""
        if not self._queue:
            print("[Play] Очередь пуста")
            return
        self._current_index = (self._current_index + 1) % len(self._queue)
        track = self._queue[self._current_index]
        self._play_internal(track)

    def _play_prev(self):
        """Предыдущий трек."""
        if not self._queue:
            return
        self._current_index = (self._current_index - 1) % len(self._queue)
        track = self._queue[self._current_index]
        self._play_internal(track)

    def _on_album_clicked(self, item: dict):
        """Клик по альбому — играем первый трек."""
        print(f"[Home] Album: {item}")

    # ==================== LYRICS ====================
    def _load_lyrics(self, track: dict):
        try:
            from lyrics_api import fetch_lyrics
            result = fetch_lyrics(
                track.get("title", ""), track.get("artist", ""))
            lines = result.get("synced") or []
            if not lines and result.get("plain"):
                lines = [{"text": l, "time": 0}
                         for l in result["plain"].split("\n") if l.strip()]

            QTimer.singleShot(0, lambda: self.page_lyrics.set_lines(lines))
        except Exception as e:
            print(f"[Lyrics] err: {e}")

    def _toggle_lyrics(self):
        if self.stack.currentWidget() is self.page_lyrics:
            self.stack.setCurrentWidget(self.page_home)
        else:
            self.stack.setCurrentWidget(self.page_lyrics)

    # ==================== PLAYER SIGNALS ====================
    def _on_position(self, ms: int):
        self.player_bar.set_position(ms)
        self.page_lyrics.set_position(ms)

    def _on_duration(self, ms: int):
        self.player_bar.set_duration(ms)
        self.page_lyrics.set_duration(ms)

    def _on_state(self, state: str):
        playing = state == "playing"
        self.player_bar.set_playing(playing)
        self.page_lyrics.set_playing(playing)

    # ==================== LIKE / DOWNLOAD ====================
    def _on_like(self, track: dict):
        if not track:
            return
        try:
            liked = self.pm.toggle_like(track)
            self.player_bar.set_liked(liked)
            self._refresh_playlists()
        except Exception as e:
            print(f"[Like] err: {e}")

    def _on_like_current(self):
        if self._current_track:
            self._on_like(self._current_track)

    def _on_download(self, track: dict):
        if not track:
            return
        threading.Thread(
            target=self._do_download, args=(track,), daemon=True
        ).start()

    def _do_download(self, track: dict):
        try:
            from downloader import download_from_url
            url = track.get("url") or track.get("preview")
            name = f"{track.get('artist', '?')} - {track['title']}"
            path = download_from_url(url, name)
            self.pm.add(path, track["title"])
            print(f"[Download] {path}")
            self._refresh_playlists()
        except Exception as e:
            print(f"[Download] err: {e}")