from __future__ import annotations
import asyncio, random
from collections import deque
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
from tools.scraper.antidetect.behaviour import compute_delay
from tools.scraper.antidetect.header_factory import build_headers
from tools.scraper.antidetect.proxy_manager import ProxyManager
from tools.scraper.validators import normalise_url, same_domain

_CHROME_IMPERSONATE_TARGETS = ["chrome124","chrome123","chrome120","chrome116","chrome110"]
_MAX_RETRIES = 3
_MAX_BACKOFF = 120

class StaticCrawler:
    def __init__(self,*,proxy_manager=None,delay=2.0,randomise_delay=True,max_pages=20,timeout=30.0):
        self.proxy_manager=proxy_manager; self.delay=delay; self.randomise_delay=randomise_delay
        self.max_pages=max_pages; self.timeout=timeout
        self._impersonate=random.choice(_CHROME_IMPERSONATE_TARGETS)
        self._use_curl_cffi=self._check_curl_cffi()
    @staticmethod
    def _check_curl_cffi():
        try: import curl_cffi; return True
        except ImportError: return False
    async def crawl(self,start_url,depth=1):
        seen=set(); queue=deque([(start_url,0,"https://www.google.com/")])
        return await (self._crawl_curl(queue,seen,depth) if self._use_curl_cffi else self._crawl_httpx(queue,seen,depth))
    async def _crawl_curl(self,queue,seen,depth):
        from curl_cffi.requests import AsyncSession
        pages=[]; proxy=self.proxy_manager.get_proxy() if self.proxy_manager else None
        proxy_url=proxy.get("raw") if proxy else None
        async with AsyncSession(impersonate=self._impersonate,timeout=self.timeout) as session:
            while queue and len(pages)<self.max_pages:
                url,current_depth,referer=queue.popleft(); url=urldefrag(url).url
                if url in seen: continue
                seen.add(url)
                page=await self._fetch_curl(session,url,referer=referer,proxy_url=proxy_url)
                if page is None: continue
                pages.append(page)
                if current_depth>=depth: continue
                for link in self.extract_links(page["html"],url):
                    if link not in seen: queue.append((link,current_depth+1,url))
        return pages
    async def _fetch_curl(self,session,url,*,referer=None,proxy_url=None,attempt=1):
        headers=build_headers(referer=referer); kwargs={"headers":headers}
        if proxy_url: kwargs["proxies"]={"https":proxy_url,"http":proxy_url}
        await asyncio.sleep(compute_delay(self.delay,self.randomise_delay))
        try: response=await session.get(url,**kwargs)
        except Exception: return None
        if response.status_code in (429,503):
            if attempt>_MAX_RETRIES: return None
            if self.proxy_manager and proxy_url: self.proxy_manager.ban_proxy(proxy_url); new=self.proxy_manager.get_proxy(); proxy_url=new.get("raw") if new else None
            raw=response.headers.get("Retry-After") or response.headers.get("retry-after")
            wait=min(int(raw),_MAX_BACKOFF) if raw and str(raw).isdigit() else min(2**attempt+random.uniform(0,1),_MAX_BACKOFF)
            await asyncio.sleep(wait)
            return await self._fetch_curl(session,url,referer=referer,proxy_url=proxy_url,attempt=attempt+1)
        if response.status_code==403 and self.proxy_manager and proxy_url: self.proxy_manager.ban_proxy(proxy_url)
        return {"url":str(response.url),"html":response.text,"status":response.status_code,"headers":dict(response.headers)}
    async def _crawl_httpx(self,queue,seen,depth):
        import httpx; pages=[]
        async with httpx.AsyncClient(follow_redirects=True,timeout=self.timeout,verify=False) as client:
            while queue and len(pages)<self.max_pages:
                url,current_depth,referer=queue.popleft(); url=urldefrag(url).url
                if url in seen: continue
                seen.add(url)
                page=await self._fetch_httpx(client,url,referer=referer)
                if page is None: continue
                pages.append(page)
                if current_depth>=depth: continue
                for link in self.extract_links(page["html"],url):
                    if link not in seen: queue.append((link,current_depth+1,url))
        return pages
    async def _fetch_httpx(self,client,url,*,referer=None,attempt=1):
        import httpx
        proxy=self.proxy_manager.get_proxy() if self.proxy_manager else None
        headers=build_headers(referer=referer); kwargs={"headers":headers}
        if proxy: kwargs["proxy"]=proxy.get("raw",proxy.get("server"))
        await asyncio.sleep(compute_delay(self.delay,self.randomise_delay))
        try:
            try: response=await client.get(url,**kwargs)
            except TypeError: kwargs.pop("proxy",None); response=await client.get(url,**kwargs)
        except httpx.HTTPError: return None
        if response.status_code in (429,503):
            if attempt>_MAX_RETRIES: return None
            if self.proxy_manager and proxy: self.proxy_manager.ban_proxy(str(proxy["server"]))
            raw=response.headers.get("retry-after","")
            wait=min(int(raw),_MAX_BACKOFF) if raw.isdigit() else min(2**attempt+random.uniform(0,1),_MAX_BACKOFF)
            await asyncio.sleep(wait); return await self._fetch_httpx(client,url,referer=referer,attempt=attempt+1)
        if response.status_code==403 and self.proxy_manager and proxy: self.proxy_manager.ban_proxy(str(proxy["server"]))
        return {"url":str(response.url),"html":response.text,"status":response.status_code,"headers":dict(response.headers)}
    @staticmethod
    def extract_links(html,base_url):
        soup=BeautifulSoup(html or "","lxml"); links=[]
        for a in soup.select("a[href]"):
            href=a.get("href")
            if not href: continue
            c=normalise_url(href,base_url)
            if c.startswith("http") and same_domain(base_url,c): links.append(c)
        return links
