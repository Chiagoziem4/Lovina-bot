from __future__ import annotations
import random
_UAS=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0"]
try:
    from fake_useragent import UserAgent; _ua=UserAgent()
except Exception: _ua=None
def get_random_ua():
    if _ua:
        try: return _ua.random
        except Exception: pass
    return random.choice(_UAS)
