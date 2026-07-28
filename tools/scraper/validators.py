from __future__ import annotations
import re
from urllib.parse import urljoin, urlparse
_URL_RE = re.compile(r"^https?$")
def validate_url(url):
    p=urlparse(url)
    if not p.scheme or not p.netloc or not _URL_RE.match(p.scheme): raise ValueError(f"Invalid URL: {url!r}")
    return url
def normalise_url(url, base_url=None):
    return urlparse(urljoin(base_url,url) if base_url else url)._replace(fragment="").geturl()
def same_domain(base_url, candidate_url):
    return urlparse(base_url).netloc == urlparse(candidate_url).netloc
