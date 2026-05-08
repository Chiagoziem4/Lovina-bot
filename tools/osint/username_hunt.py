"""
Username Reconnaissance
Check 30+ social platforms for username availability
No API key needed
"""
import httpx
import asyncio
from typing import Dict, List
from config import USER_AGENTS, HTTP_TIMEOUT
import random

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://instagram.com/{}",
    "TikTok": "https://tiktok.com/@{}",
    "Reddit": "https://reddit.com/user/{}",
    "LinkedIn": "https://linkedin.com/in/{}",
    "YouTube": "https://youtube.com/@{}",
    "Facebook": "https://facebook.com/{}",
    "Pinterest": "https://pinterest.com/{}",
    "Twitch": "https://twitch.tv/{}",
    "Discord": "https://discordapp.com/users/{}",
    "Steam": "https://steamcommunity.com/search/users/#text={}",
    "Spotify": "https://open.spotify.com/user/{}",
    "Medium": "https://medium.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "HackerNews": "https://news.ycombinator.com/user?id={}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "Keybase": "https://keybase.io/{}",
    "Telegram": "https://t.me/{}",
    "Chess.com": "https://chess.com/member/{}",
    "Replit": "https://replit.com/@{}",
    "CodePen": "https://codepen.io/{}",
    "npm": "https://npmjs.com/~{}",
    "PyPI": "https://pypi.org/user/{}",
}

async def check_username(username: str) -> Dict | str:
    """
    Check username availability across 27+ platforms
    """
    try:
        if not username or len(username) > 50:
            return "❌ Invalid username"
        
        # Remove special chars
        username = "".join(c for c in username if c.isalnum() or c in "._-")
        
        results = {
            "found": [],
            "not_found": [],
            "error": []
        }
        
        async def check_platform(platform: str, url: str) -> tuple:
            try:
                check_url = url.format(username)
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        check_url,
                        headers=headers,
                        timeout=HTTP_TIMEOUT,
                        follow_redirects=True
                    )
                    
                    # 200/302 = found, 404 = not found
                    if response.status_code == 200 or response.status_code == 302:
                        return platform, "found", check_url
                    elif response.status_code == 404:
                        return platform, "not_found", check_url
                    else:
                        return platform, "error", None
            
            except Exception:
                return platform, "error", None
        
        # Check all platforms concurrently
        tasks = [check_platform(platform, url) for platform, url in PLATFORMS.items()]
        checks = await asyncio.gather(*tasks)
        
        for platform, status, url in checks:
            if status == "found":
                results["found"].append({"platform": platform, "url": url})
            elif status == "not_found":
                results["not_found"].append(platform)
            else:
                results["error"].append(platform)
        
        return {
            "username": username,
            "found_count": len(results["found"]),
            "not_found_count": len(results["not_found"]),
            "results": results
        }
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
