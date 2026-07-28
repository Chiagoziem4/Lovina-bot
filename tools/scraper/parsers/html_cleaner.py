from __future__ import annotations
from bs4 import BeautifulSoup
NOISE={"script","style","noscript","svg","iframe","header","footer","nav","aside","form","button","input"}
def clean_html(html):
    soup=BeautifulSoup(html or "","lxml")
    for t in soup.find_all(NOISE): t.decompose()
    for s in ["[role='navigation']",".ad",".ads",".cookie-banner"]:
        for n in soup.select(s): n.decompose()
    main=soup.find("main") or soup.find("article") or soup.body or soup
    return str(main)
