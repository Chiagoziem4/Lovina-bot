from __future__ import annotations
import random
from pathlib import Path
from urllib.parse import urlparse
class ProxyManager:
    def __init__(self,proxy_file="config/proxies.txt"):
        self.proxy_file=Path(proxy_file); self.proxies=self._load_proxies(); self.banned=set()
    def _load_proxies(self):
        if not self.proxy_file.exists(): return []
        proxies=[]
        for line in self.proxy_file.read_text(encoding="utf-8").splitlines():
            s=line.strip()
            if s and not s.startswith("#"): proxies.append(self._normalise(s))
        return proxies
    @staticmethod
    def _normalise(proxy_url):
        p=urlparse(proxy_url)
        if p.scheme and p.hostname and p.port:
            return {"server":f"{p.scheme}://{p.hostname}:{p.port}","username":p.username,"password":p.password,"raw":proxy_url}
        return {"server":proxy_url,"username":None,"password":None,"raw":proxy_url}
    def get_proxy(self):
        avail=[p for p in self.proxies if str(p["server"]) not in self.banned]
        if not avail:
            if self.proxies: self.banned.clear(); avail=self.proxies
            else: return None
        return random.choice(avail)
    def ban_proxy(self,server): self.banned.add(server)
