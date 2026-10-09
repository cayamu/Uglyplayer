"""
Получение чартов из iTunes RSS — топ-100 треков.
Без ключей, без авторизации, бесплатно.
Работает везде, включая РФ.
"""
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# iTunes RSS — топ-100 песен для разных стран
CHARTS_URL = "https://itunes.apple.com/{country}/rss/topsongs/limit=100/json"


def fetch_top_tracks(country: str = "ru", limit: int = 100) -> list:
    """
    Тянет топ-100 из iTunes RSS.
    country: "ru" — Россия, "us" — США, "gb" — Британия и т.д.
    Возвращает список словарей:
    [{'title','artist','genre','cover','preview','url','source'}]
    """
    url = CHARTS_URL.format(country=country)

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[api_charts] Ошибка запроса: {e}")
        return []

    entries = data.get("feed", {}).get("entry", [])
    tracks = []

    for e in entries[:limit]:
        try:
            title = e["im:name"]["label"]
            artist = e["im:artist"]["label"]
            genre = (
                e.get("category", {})
                .get("attributes", {})
                .get("label", "Unknown")
            )
            images = e.get("im:image", [])
            cover = images[-1]["label"] if images else None

            preview = None
            for link in e.get("link", []):
                if link.get("attributes", {}).get("type") == "audio/x-m4a":
                    preview = link.get("attributes", {}).get("href")
                    break

            tracks.append({
                "title": title,
                "artist": artist,
                "genre": genre,
                "cover": cover,
                "preview": preview,
                "url": preview,
                "duration": "",
                "source": "iTunes Top-100 RU",
            })
        except Exception:
            continue

    print(f"[api_charts] Загружено: {len(tracks)} треков ({country})")
    return tracks