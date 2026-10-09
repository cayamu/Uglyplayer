"""
Ассистент: обновляет чарты раз в сутки + строит простые рекомендации.
Без нейросетей. Просто статистика жанров.
Источник: iTunes RSS (Россия).
"""
import os
import json
import time
from collections import Counter

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from api_charts import fetch_top_tracks
from config import ASSETS_DIR

CHARTS_CACHE = os.path.join(ASSETS_DIR, "charts_cache.json")
UPDATE_INTERVAL_MS = 24 * 60 * 60 * 1000   # 24 часа


class Assistant(QObject):
    charts_ready = pyqtSignal(list)              # топ-100
    recommendations_ready = pyqtSignal(list)     # персональные

    def __init__(self):
        super().__init__()
        self._charts = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)

    # ==================== СТАРТ ====================
    def start(self):
        """Грузит кэш, обновляет если устарел, запускает таймер."""
        self._charts = self._load_cache()

        if self._charts:
            self.charts_ready.emit(self._charts)
            print(f"[Assistant] Кэш загружен: {len(self._charts)} треков")

        if self._cache_is_stale():
            print("[Assistant] Кэш устарел — обновляю...")
            self._refresh()

        # Обновление раз в сутки
        self._timer.start(UPDATE_INTERVAL_MS)

    # ==================== КЭШ ====================
    def _cache_is_stale(self) -> bool:
        if not os.path.exists(CHARTS_CACHE):
            return True
        age = time.time() - os.path.getmtime(CHARTS_CACHE)
        return age > (24 * 60 * 60)

    def _load_cache(self) -> list:
        if not os.path.exists(CHARTS_CACHE):
            return []
        try:
            with open(CHARTS_CACHE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("tracks", [])
        except Exception:
            return []

    def _save_cache(self, tracks: list):
        with open(CHARTS_CACHE, "w", encoding="utf-8") as f:
            json.dump(
                {"updated": time.time(), "tracks": tracks},
                f, ensure_ascii=False, indent=2,
            )

    # ==================== ОБНОВЛЕНИЕ ====================
    def _refresh(self):
        """Тянет свежий чарт России и сохраняет в кэш."""
        print("[Assistant] Тяну свежий чарт (RU)...")
        tracks = fetch_top_tracks(country="ru", limit=100)
        if tracks:
            self._charts = tracks
            self._save_cache(tracks)
            self.charts_ready.emit(tracks)
            print(f"[Assistant] Обновлено: {len(tracks)} треков")
        else:
            print("[Assistant] Не удалось обновить чарты")

    def force_refresh(self):
        """Принудительное обновление (для кнопки «обновить»)."""
        self._refresh()

    # ==================== РЕКОМЕНДАЦИИ ====================
    def get_recommendations(self, liked_tracks: list, limit: int = 12) -> list:
        """
        Простая логика:
        1. Смотрим жанры лайкнутых треков.
        2. Берём топ-3 жанра.
        3. Фильтруем чарт по этим жанрам.
        4. Убираем то, что уже лайкнуто.
        """
        if not self._charts:
            return []

        # Если ничего не лайкнуто — возвращаем общий топ
        if not liked_tracks:
            return self._charts[:limit]

        genres = [t.get("genre", "Unknown") for t in liked_tracks]
        genre_counts = Counter(genres)
        top_genres = {g for g, _ in genre_counts.most_common(3)}

        liked_titles = {t.get("title") for t in liked_tracks}

        recs = [
            t for t in self._charts
            if t.get("genre") in top_genres
            and t.get("title") not in liked_titles
        ]

        # Если жанровых совпадений мало — добиваем общим топом
        if len(recs) < limit:
            extra = [
                t for t in self._charts
                if t.get("title") not in liked_titles
                and t not in recs
            ]
            recs.extend(extra[: limit - len(recs)])

        return recs[:limit]

    def get_charts(self) -> list:
        return self._charts