"""
Получение текста песни — 3 источника:
1. LRCLIB — синхронизированный (с таймкодами)
2. Lyrics OVH — обычный текст, работает для зарубежного и русского
3. ТекстПесни.ру — фоллбэк для русского (если домен доступен)
"""
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
}

LRCLIB_URL = "https://lrclib.net/api/get"
LYRICS_OVH_URL = "https://api.lyrics.ovh/v1/{artist}/{title}"
TEXTYPESNI_SEARCH = "https://teksty-pesenok.ru/search/?q={query}"


# ==================== LRCLIB ====================
def parse_lrc(lrc_text: str) -> list:
    if not lrc_text:
        return []
    lines = []
    pattern = re.compile(r"\[(\d+):(\d+\.\d+)\]\s*(.*)")
    for line in lrc_text.split("\n"):
        m = pattern.match(line.strip())
        if m:
            minutes = int(m.group(1))
            seconds = float(m.group(2))
            text = m.group(3).strip()
            if text:
                ms = int((minutes * 60 + seconds) * 1000)
                lines.append({"time": ms, "text": text})
    lines.sort(key=lambda x: x["time"])
    return lines


def fetch_from_lrclib(title: str, artist: str, duration_sec: int = 0) -> dict:
    result = {"synced": [], "plain": "", "found": False, "source": ""}
    if not title or not artist:
        return result

    params = {"artist_name": artist, "track_name": title}
    if duration_sec:
        params["duration"] = duration_sec

    try:
        r = requests.get(LRCLIB_URL, params=params, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            return result
        data = r.json()
    except Exception as e:
        print(f"[lyrics/LRCLIB] Ошибка: {e}")
        return result

    synced = data.get("syncedLyrics")
    plain = data.get("plainLyrics")

    if synced:
        result["synced"] = parse_lrc(synced)
        result["found"] = True
        result["source"] = "LRCLIB"
    elif plain:
        result["plain"] = plain
        result["found"] = True
        result["source"] = "LRCLIB"

    return result


# ==================== LYRICS OVH ====================
def fetch_from_lyrics_ovh(title: str, artist: str) -> dict:
    """Lyrics OVH — быстрый, работает без ключа."""
    result = {"synced": [], "plain": "", "found": False, "source": ""}
    if not title or not artist:
        return result

    url = LYRICS_OVH_URL.format(
        artist=requests.utils.quote(artist),
        title=requests.utils.quote(title),
    )

    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code == 200:
            data = r.json()
            lyrics = (data.get("lyrics") or "").strip()
            # Убираем заголовок "Paroles de la chanson..."
            if lyrics.startswith("Paroles de la chanson"):
                idx = lyrics.find("\n")
                if idx > 0:
                    lyrics = lyrics[idx:].strip()

            if lyrics and len(lyrics) > 20:
                result["plain"] = lyrics
                result["found"] = True
                result["source"] = "Lyrics OVH"
    except Exception as e:
        print(f"[lyrics/OVH] Ошибка: {e}")

    return result


# ==================== ТЕКСТПЕСНИ.РУ ====================
def fetch_from_teksty(title: str, artist: str) -> dict:
    """Парсит с teksty-pesenok.ru — для русского."""
    result = {"synced": [], "plain": "", "found": False, "source": ""}
    if not title or not artist:
        return result

    query = f"{artist} {title}"
    url = TEXTYPESNI_SEARCH.format(query=requests.utils.quote(query))

    try:
        r = requests.get(url, headers=HEADERS, timeout=6)
        if r.status_code != 200:
            return result
        soup = BeautifulSoup(r.text, "lxml")
    except Exception as e:
        print(f"[lyrics/teksty] Ошибка: {e}")
        return result

    first_link = soup.select_one(
        "a.song-link, .song a, .track a, .song-list a")
    if not first_link:
        return result

    href = first_link.get("href")
    if not href:
        return result

    if not href.startswith("http"):
        href = "https://teksty-pesenok.ru" + href

    try:
        r2 = requests.get(href, headers=HEADERS, timeout=6)
        soup2 = BeautifulSoup(r2.text, "lxml")
        text_block = soup2.select_one(
            ".song-text, .text, .lyrics, .song__text")
        if not text_block:
            return result
        text = text_block.get_text("\n", strip=True)
        if text and len(text) > 20:
            result["plain"] = text
            result["found"] = True
            result["source"] = "ТекстПесни.ру"
    except Exception as e:
        print(f"[lyrics/teksty] Ошибка: {e}")

    return result


# ==================== ГЛАВНАЯ ====================
def fetch_lyrics(title: str, artist: str, duration_sec: int = 0) -> dict:
    """3 источника по очереди."""
    # 1. LRCLIB (синхронизированный)
    result = fetch_from_lrclib(title, artist, duration_sec)
    if result["found"]:
        print(f"[lyrics] {artist} — {title}: LRCLIB")
        return result

    # 2. Lyrics OVH
    result = fetch_from_lyrics_ovh(title, artist)
    if result["found"]:
        print(f"[lyrics] {artist} — {title}: Lyrics OVH")
        return result

    # 3. ТекстПесни.ру
    result = fetch_from_teksty(title, artist)
    if result["found"]:
        print(f"[lyrics] {artist} — {title}: ТекстПесни.ру")
        return result

    print(f"[lyrics] {artist} — {title}: НЕ найдено")
    return {"synced": [], "plain": "", "found": False, "source": ""}