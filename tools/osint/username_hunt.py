import asyncio
import httpx
import random
from config import USER_AGENTS

PLATFORMS = [
    ("GitHub", "https://github.com/{}"),
    ("Twitter/X", "https://twitter.com/{}"),
    ("Instagram", "https://www.instagram.com/{}/"),
    ("Reddit", "https://www.reddit.com/user/{}"),
    ("TikTok", "https://www.tiktok.com/@{}"),
    ("YouTube", "https://www.youtube.com/@{}"),
    ("Twitch", "https://www.twitch.tv/{}"),
    ("Pinterest", "https://www.pinterest.com/{}/"),
    ("LinkedIn", "https://www.linkedin.com/in/{}"),
    ("Telegram", "https://t.me/{}"),
    ("Snapchat", "https://www.snapchat.com/add/{}"),
    ("Medium", "https://medium.com/@{}"),
    ("Dev.to", "https://dev.to/{}"),
    ("Keybase", "https://keybase.io/{}"),
    ("GitLab", "https://gitlab.com/{}"),
    ("HackerNews", "https://news.ycombinator.com/user?id={}"),
    ("Steam", "https://steamcommunity.com/id/{}"),
    ("Mastodon", "https://mastodon.social/@{}"),
    ("ProductHunt", "https://www.producthunt.com/@{}"),
    ("Spotify", "https://open.spotify.com/user/{}"),
]


async def check_username(username: str) -> dict | str:
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    found = []
    not_found = []

    async def check(platform, url_template):
        url = url_template.format(username)
        try:
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                r = await client.get(url, headers=headers)
            if r.status_code == 200:
                found.append({"platform": platform, "url": url})
            else:
                not_found.append(platform)
        except Exception:
            not_found.append(platform)

    await asyncio.gather(*[check(p, u) for p, u in PLATFORMS])
    return {
        "username": username,
        "found_count": len(found),
        "not_found_count": len(not_found),
        "results": {"found": found, "not_found": not_found},
    }
