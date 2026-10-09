import asyncio
from msoc import search


async def main():
    tracks = []
    async for sound in search("test"):
        tracks.append(sound)
        if len(tracks) >= 5:
            break
    
    print(f"OK, найдено: {len(tracks)}")
    for t in tracks:
        print(f"  {getattr(t, 'artist', '?')} — {getattr(t, 'title', '?')}")
        print(f"    URL: {getattr(t, 'url', '?')}")


asyncio.run(main())