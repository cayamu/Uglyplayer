import os
import json
import time
from config import PLAYLISTS_DIR, ASSETS_DIR

PLAYLISTS_FILE = os.path.join(PLAYLISTS_DIR, "playlists.json")
COVERS_DIR = os.path.join(ASSETS_DIR, "playlist_covers")
os.makedirs(COVERS_DIR, exist_ok=True)


def _default_data():
    return {
        "liked": {"name": "Любимые", "cover": None, "tracks": []},
        "playlists": {}
    }


class PlaylistManager:
    def __init__(self):
        if not os.path.exists(PLAYLISTS_FILE):
            self._save(_default_data())

    def _load(self):
        with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------- ЛЮБИМЫЕ ----------
    def is_liked(self, title: str) -> bool:
        data = self._load()
        return any(t["title"] == title for t in data["liked"]["tracks"])

    def toggle_like(self, track: dict) -> bool:
        data = self._load()
        liked = data["liked"]["tracks"]
        existing = next((t for t in liked if t["title"] == track["title"]), None)

        if existing:
            liked.remove(existing)
            self._save(data)
            return False
        else:
            liked.append({
                "title": track["title"],
                "artist": track.get("artist", ""),
                "url": track.get("url"),
                "cover": track.get("cover"),
                "path": track.get("path"),
            })
            self._save(data)
            return True

    def get_liked(self):
        return self._load()["liked"]["tracks"]

    # ---------- ПЛЕЙЛИСТЫ ----------
    def create_playlist(self, name: str, cover_path: str = None) -> str:
        data = self._load()
        pid = f"pl_{int(time.time() * 1000)}"
        data["playlists"][pid] = {
            "name": name,
            "cover": cover_path,
            "tracks": [],
        }
        self._save(data)
        return pid

    def delete_playlist(self, pid: str):
        data = self._load()
        data["playlists"].pop(pid, None)
        self._save(data)

    def get_playlists(self):
        return self._load()["playlists"]

    def get_playlist(self, pid: str):
        return self._load()["playlists"].get(pid)

    def add_to_playlist(self, pid: str, track: dict):
        data = self._load()
        pl = data["playlists"].get(pid)
        if not pl:
            return
        if not any(t["title"] == track["title"] for t in pl["tracks"]):
            pl["tracks"].append({
                "title": track["title"],
                "artist": track.get("artist", ""),
                "url": track.get("url"),
                "cover": track.get("cover"),
                "path": track.get("path"),
            })
            self._save(data)

    def remove_from_playlist(self, pid: str, title: str):
        data = self._load()
        pl = data["playlists"].get(pid)
        if pl:
            pl["tracks"] = [t for t in pl["tracks"] if t["title"] != title]
            self._save(data)

    # ---------- СОВМЕСТИМОСТЬ ----------
    def add(self, path: str, title: str):
        """Совместимость: добавляет в плейлист по умолчанию."""
        data = self._load()
        if "default" not in data["playlists"]:
            data["playlists"]["default"] = {
                "name": "Скачанные",
                "cover": None,
                "tracks": [],
            }
        data["playlists"]["default"]["tracks"].append({
            "title": title,
            "artist": "",
            "url": path,
            "cover": None,
            "path": path,
        })
        self._save(data)

    def all(self):
        """Все скачанные треки — для библиотеки."""
        data = self._load()
        result = []
        seen = set()
        for t in data["liked"]["tracks"]:
            if t.get("path") and t["title"] not in seen:
                result.append({"path": t["path"], "title": t["title"]})
                seen.add(t["title"])
        for pl in data["playlists"].values():
            for t in pl["tracks"]:
                if t.get("path") and t["title"] not in seen:
                    result.append({"path": t["path"], "title": t["title"]})
                    seen.add(t["title"])
        return result