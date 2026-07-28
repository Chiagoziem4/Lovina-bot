from __future__ import annotations
import re
from bs4 import BeautifulSoup
_WS=re.compile(r"\s+")
def extract_text(html): return _WS.sub(" ",BeautifulSoup(html or "","lxml").get_text(" ",strip=True)).strip()
