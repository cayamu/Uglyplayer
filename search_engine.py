import asyncio
from msoc import search as msoc_search


async def _search_async(query: str, limit: int = 25):
    tracks = []
    try:
        async for sound in msoc_search(query):
            url = getattr(sound, "url", None)
            if not url:
                continue  # пропускаем треки без ссылки

            tracks.append({
                "title": getattr(sound, "title", "Unknown") or "Unknown",
                "artist": getattr(sound, "artist", "") or "",
                "url": url,
                "duration": getattr(sound, "duration", "") or "",
                "source": getattr(sound, "source", "") or "",
                "cover": None,  # msoc не отдаёт обложки
            })
            if len(tracks) >= limit:
                break
    except Exception as e:
        print(f"[search_engine] Ошибка: {e}")
        raise
    return tracks


def search_tracks(query: str, limit: int = 25):
    """Синхронная обёртка для вызова из фонового потока."""
    return asyncio.run(_search_async(query, limit))