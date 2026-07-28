from __future__ import annotations
import asyncio,json,os,sqlite3
from dataclasses import dataclass,field
from datetime import datetime,timezone
from pathlib import Path
from tools.scraper.static_crawler import StaticCrawler
from tools.scraper.ai.extractor import DataExtractor
from tools.scraper.ai.schemas import get_schema_model
from tools.scraper.antidetect.proxy_manager import ProxyManager
from tools.scraper.queue_manager import QueueManager

DATA_DIR=Path(os.getenv("SPIDER_DATA_DIR","data/spider"))
DB_PATH=DATA_DIR/"spider.db"
MAX_CONTENT_CHARS=int(os.getenv("MAX_CONTENT_CHARS","12000"))
MAX_PAGES_DEFAULT=int(os.getenv("SPIDER_MAX_PAGES","20"))
DOWNLOAD_DELAY=float(os.getenv("SPIDER_DELAY","2.0"))
RANDOMISE_DELAY=os.getenv("SPIDER_RANDOMISE_DELAY","true").lower() in {"1","true","yes"}

@dataclass
class CrawlResult:
    job_id:int; url:str; schema:str; pages_crawled:int; pages_extracted:int
    items:list[dict]=field(default_factory=list); started_at:str=""; completed_at:str=""; status:str="done"; error:str|None=None

def _init_db():
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS crawl_jobs(id INTEGER PRIMARY KEY AUTOINCREMENT,url TEXT,schema TEXT DEFAULT 'generic',status TEXT DEFAULT 'running',pages_crawled INTEGER DEFAULT 0,pages_extracted INTEGER DEFAULT 0,started_at TEXT,completed_at TEXT,error TEXT);
        CREATE TABLE IF NOT EXISTS extracted_items(id INTEGER PRIMARY KEY AUTOINCREMENT,job_id INTEGER,url TEXT,raw_json TEXT,extracted_at TEXT,FOREIGN KEY(job_id) REFERENCES crawl_jobs(id));
    """); con.commit(); con.close()

def _create_job(url,schema):
    _init_db(); con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("INSERT INTO crawl_jobs(url,schema,status,started_at) VALUES(?,?,'running',?)",(url,schema,datetime.now(timezone.utc).isoformat()))
    j=cur.lastrowid; con.commit(); con.close(); return j

def _save_item(job_id,url,item):
    con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("INSERT INTO extracted_items(job_id,url,raw_json,extracted_at) VALUES(?,?,?,?)",(job_id,url,json.dumps(item),datetime.now(timezone.utc).isoformat()))
    cur.execute("UPDATE crawl_jobs SET pages_extracted=pages_extracted+1 WHERE id=?",(job_id,)); con.commit(); con.close()

def _finish_job(job_id,status,error=None):
    con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("UPDATE crawl_jobs SET status=?,completed_at=?,error=? WHERE id=?",(status,datetime.now(timezone.utc).isoformat(),error,job_id)); con.commit(); con.close()

def _inc_crawled(job_id):
    con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("UPDATE crawl_jobs SET pages_crawled=pages_crawled+1 WHERE id=?",(job_id,)); con.commit(); con.close()

def get_job_items(job_id):
    _init_db(); con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("SELECT url,raw_json FROM extracted_items WHERE job_id=?",(job_id,)); rows=cur.fetchall(); con.close()
    result=[]
    for url,raw in rows:
        try: d=json.loads(raw); d["_url"]=url; result.append(d)
        except Exception: pass
    return result

def get_all_jobs(limit=20):
    _init_db(); con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("SELECT id,url,schema,status,pages_crawled,pages_extracted,started_at FROM crawl_jobs ORDER BY id DESC LIMIT?",(limit,)); rows=cur.fetchall(); con.close()
    return [{"id":r[0],"url":r[1],"schema":r[2],"status":r[3],"pages_crawled":r[4],"pages_extracted":r[5],"started_at":r[6]} for r in rows]

def get_db_stats():
    _init_db(); con=sqlite3.connect(DB_PATH); cur=con.cursor()
    cur.execute("SELECT COUNT(*) FROM crawl_jobs"); jobs=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM extracted_items"); items=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM crawl_jobs WHERE status='done'"); done=cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM crawl_jobs WHERE status='failed'"); failed=cur.fetchone()[0]
    con.close(); return {"total_jobs":jobs,"total_items":items,"jobs_done":done,"jobs_failed":failed}

async def run_crawl(url,*,schema="generic",depth=1,max_pages=MAX_PAGES_DEFAULT,use_proxies=False,use_playwright=False,groq_api_key=None,progress_callback=None):
    job_id=_create_job(url,schema); schema_model=get_schema_model(schema)
    proxy_manager=ProxyManager() if use_proxies else None
    extractor=DataExtractor(schema_model=schema_model,groq_api_key=groq_api_key,max_chars=MAX_CONTENT_CHARS)
    items=[]; pages_crawled=0; pages_extracted=0
    try:
        if use_playwright:
            from tools.scraper.dynamic_crawler import DynamicCrawler
            crawler=DynamicCrawler(proxy_manager=proxy_manager)
        else:
            crawler=StaticCrawler(proxy_manager=proxy_manager,delay=DOWNLOAD_DELAY,randomise_delay=RANDOMISE_DELAY,max_pages=max_pages)
        if use_playwright:
            queue=QueueManager(); queue.add(url,depth=0)
            try:
                while queue and pages_crawled<max_pages:
                    cur_url,cur_depth=queue.pop()
                    if progress_callback: await progress_callback(f"🔍 Page {pages_crawled+1}: {cur_url[:50]}...")
                    page=await crawler.scrape(cur_url)
                    if not page.get("html"): continue
                    pages_crawled+=1; _inc_crawled(job_id)
                    extracted=await extractor.extract(page["url"],page["html"])
                    if extracted: _save_item(job_id,page["url"],extracted); items.append(extracted); pages_extracted+=1
                    if cur_depth<depth:
                        for link in crawler.extract_links(page["html"],page["url"]): queue.add(link,depth=cur_depth+1)
            finally: await crawler.close()
        else:
            raw_pages=await crawler.crawl(url,depth=depth)
            for page in raw_pages:
                if pages_crawled>=max_pages: break
                pages_crawled+=1; _inc_crawled(job_id)
                if progress_callback: await progress_callback(f"🔍 Extracting page {pages_crawled}: {page['url'][:50]}...")
                extracted=await extractor.extract(page["url"],page["html"])
                if extracted: _save_item(job_id,page["url"],extracted); items.append(extracted); pages_extracted+=1
        _finish_job(job_id,"done")
        return CrawlResult(job_id=job_id,url=url,schema=schema,pages_crawled=pages_crawled,pages_extracted=pages_extracted,items=items,status="done")
    except Exception as exc:
        _finish_job(job_id,"failed",str(exc))
        return CrawlResult(job_id=job_id,url=url,schema=schema,pages_crawled=pages_crawled,pages_extracted=pages_extracted,items=items,status="failed",error=str(exc))
