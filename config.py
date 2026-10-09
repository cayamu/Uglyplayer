import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
PLAYLISTS_DIR = os.path.join(BASE_DIR, "playlists")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
SETTINGS_FILE = os.path.join(ASSETS_DIR, "settings.json")

for d in (DOWNLOADS_DIR, PLAYLISTS_DIR, ASSETS_DIR,
          BACKGROUNDS_DIR, FONTS_DIR, ICONS_DIR):
    os.makedirs(d, exist_ok=True)