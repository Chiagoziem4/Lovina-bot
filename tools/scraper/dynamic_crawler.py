from __future__ import annotations
import random
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
from tools.scraper.antidetect.behaviour import human_delay,simulate_mouse_move,simulate_scroll
from tools.scraper.antidetect.proxy_manager import ProxyManager
from tools.scraper.antidetect.useragent_rotator import get_random_ua
from tools.scraper.validators import normalise_url,same_domain
class DynamicCrawler:
    def __init__(self,proxy_manager=None,*,headless=True):
        self.proxy_manager=proxy_manager; self.headless=headless; self._playwright=None; self._browser=None
    async def _ensure_browser(self):
        if self._browser: return
        from playwright.async_api import async_playwright
        self._playwright=await async_playwright().start()
        proxy=self.proxy_manager.get_proxy() if self.proxy_manager else None
        kw={"headless":self.headless,"args":["--no-sandbox","--disable-blink-features=AutomationControlled"]}
        if proxy: kw["proxy"]={"server":proxy["server"],"username":proxy.get("username"),"password":proxy.get("password")}
        self._browser=await self._playwright.chromium.launch(**kw)
    async def scrape(self,url,wait_for="networkidle"):
        await self._ensure_browser()
        context=await self._browser.new_context(user_agent=get_random_ua(),viewport={"width":random.randint(1200,1920),"height":random.randint(800,1080)},locale="en-US")
        page=await context.new_page()
        try:
            try:
                from playwright_stealth import stealth_async; await stealth_async(page)
            except ImportError: pass
            await human_delay(1.2,2.4)
            response=await page.goto(url,wait_until=wait_for,timeout=30000)
            await simulate_mouse_move(page); await simulate_scroll(page); await human_delay(0.8,1.6)
            html=await page.content()
            return {"url":page.url,"html":html,"status":response.status if response else 0,"headers":{}}
        except Exception as e: return {"url":url,"html":"","status":0,"headers":{},"error":str(e)}
        finally: await context.close()
    async def close(self):
        if self._browser: await self._browser.close()
        if self._playwright: await self._playwright.stop()
    @staticmethod
    def extract_links(html,base_url):
        soup=BeautifulSoup(html or "","lxml"); links=[]
        for a in soup.select("a[href]"):
            href=a.get("href")
            if not href: continue
            c=urldefrag(normalise_url(href,base_url)).url
            if c.startswith("http") and same_domain(base_url,c): links.append(c)
        return links
