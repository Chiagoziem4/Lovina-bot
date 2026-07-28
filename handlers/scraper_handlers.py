from __future__ import annotations
import io,re
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile,Message
from config import GROQ_API_KEY
from utils.permissions import require_not_banned
from utils.formatter import Formatter

router = Router()

def _extract_url(text):
    m=re.search(r"https?://\S+",text or ""); return m.group(0).rstrip(".,)>") if m else None
def _parse_flag(text,flag,default=None):
    m=re.search(rf"--{flag}\s+(\S+)",text or ""); return m.group(1) if m else default
def _has_flag(text,flag): return f"--{flag}" in (text or "")
def _fmt_item(item,i):
    lines=[f"<b>📄 Result {i}</b>"]
    for k in ["title","headline","product_name","job_title","full_name","summary","description"]:
        v=item.get(k)
        if v and isinstance(v,str): lines.append(f"  <b>{k}:</b> {v[:200]}")
    for k,v in item.items():
        if k in {"source_url","_url"} or k in ["title","headline","product_name","job_title","full_name","summary","description"] or v is None: continue
        if isinstance(v,list): lines.append(f"  <b>{k}:</b> {', '.join(str(x) for x in v[:5])}") if v else None
        elif isinstance(v,(bool,int,float)): lines.append(f"  <b>{k}:</b> {v}")
        elif isinstance(v,str) and len(v)<300: lines.append(f"  <b>{k}:</b> {v}")
    url=item.get("source_url") or item.get("_url","")
    if url: lines.append(f"  <b>url:</b> <a href='{url}'>{url[:60]}</a>")
    return "\n".join(lines)

@router.message(Command("scrape"))
@require_not_banned
async def scrape_command(message: Message):
    text=message.text or ""; url=_extract_url(text)
    if not url:
        await message.answer("🕷️ <b>Web Scraper</b>\n\n<b>Usage:</b>\n<code>/scrape https://example.com</code>\n<code>/scrape https://shop.com --schema ecommerce</code>\n<code>/scrape https://blog.com --schema news --depth 2 --pages 10</code>\n<code>/scrape https://site.com --dynamic</code>\n\n<b>Schemas:</b> generic, ecommerce, news, job, social",parse_mode="HTML"); return
    schema=_parse_flag(text,"schema","generic"); depth=int(_parse_flag(text,"depth","1")); max_pages=int(_parse_flag(text,"pages","5")); dynamic=_has_flag(text,"dynamic")
    depth=max(1,min(depth,3)); max_pages=max(1,min(max_pages,20))
    status_msg=await message.answer(f"🕷️ <b>Spider activated</b>\n🎯 <code>{url[:60]}</code>\n📋 Schema: <b>{schema}</b>\n🔢 Pages: <b>{max_pages}</b>\n{'🎭 Dynamic (Playwright)' if dynamic else '⚡ Static (httpx)'}\n\n⏳ Crawling...",parse_mode="HTML")
    last=[""]; 
    async def progress(msg):
        if msg!=last[0]:
            last[0]=msg
            try: await status_msg.edit_text(f"🕷️ <b>Crawling...</b>\n\n{msg}",parse_mode="HTML")
            except Exception: pass
    try:
        from tools.scraper.engine import run_crawl
        result=await run_crawl(url,schema=schema,depth=depth,max_pages=max_pages,use_playwright=dynamic,groq_api_key=GROQ_API_KEY,progress_callback=progress)
    except Exception as exc: await status_msg.edit_text(f"❌ <b>Scrape failed</b>\n\n<code>{str(exc)[:300]}</code>",parse_mode="HTML"); return
    if result.status=="failed": await status_msg.edit_text(f"❌ <b>Crawl failed</b>\n\n<code>{(result.error or '')[:300]}</code>",parse_mode="HTML"); return
    summary=f"✅ <b>Crawl complete — Job #{result.job_id}</b>\n\n📊 Pages: <b>{result.pages_crawled}</b>\n🧠 Extracted: <b>{result.pages_extracted}</b>\n📋 Schema: <b>{schema}</b>\n\n"
    if not result.items: await status_msg.edit_text(summary+"⚠️ No structured data extracted.",parse_mode="HTML"); return
    await status_msg.edit_text(summary+f"📥 /spiderexport --job {result.job_id} to download all",parse_mode="HTML")
    for i,item in enumerate(result.items[:3],1):
        for chunk in Formatter.truncate(_fmt_item(item,i)): await message.answer(chunk,parse_mode="HTML",disable_web_page_preview=True)
    if len(result.items)>3: await message.answer(f"<i>...and {len(result.items)-3} more. /spiderexport --job {result.job_id}</i>",parse_mode="HTML")

@router.message(Command("extract"))
@require_not_banned
async def extract_command(message: Message):
    text=message.text or ""; url=_extract_url(text)
    if not url: await message.answer("Usage: /extract https://example.com [--schema job]"); return
    schema=_parse_flag(text,"schema","generic")
    msg=await message.answer(f"🔬 Extracting from <code>{url[:60]}</code>...",parse_mode="HTML")
    try:
        from tools.scraper.engine import run_crawl
        result=await run_crawl(url,schema=schema,depth=0,max_pages=1,groq_api_key=GROQ_API_KEY)
    except Exception as exc: await msg.edit_text(f"❌ <code>{str(exc)[:300]}</code>",parse_mode="HTML"); return
    if not result.items: await msg.edit_text(f"⚠️ No data extracted from <code>{url}</code>",parse_mode="HTML"); return
    await msg.edit_text(f"✅ <b>Job #{result.job_id}</b> | Schema: <b>{schema}</b>",parse_mode="HTML")
    for chunk in Formatter.truncate(_fmt_item(result.items[0],1)): await message.answer(chunk,parse_mode="HTML",disable_web_page_preview=True)

@router.message(Command("spiderexport"))
@require_not_banned
async def spider_export_command(message: Message):
    text=message.text or ""; fmt=_parse_flag(text,"format","json"); job_id_str=_parse_flag(text,"job")
    if fmt not in ("json","csv","jsonl"): await message.answer("❌ Format must be: json, csv, or jsonl"); return
    try:
        from tools.scraper.engine import get_job_items,get_all_jobs
        from tools.scraper.exporter import export_items
        if job_id_str: job_id=int(job_id_str); items=get_job_items(job_id)
        else:
            jobs=get_all_jobs(limit=1)
            if not jobs: await message.answer("⚠️ No crawl jobs found. Run /scrape first."); return
            job_id=jobs[0]["id"]; items=get_job_items(job_id)
        if not items: await message.answer(f"⚠️ No items for job #{job_id}"); return
        file_bytes,filename=export_items(items,format=fmt)
        await message.answer_document(BufferedInputFile(file_bytes,filename=f"job{job_id}_{filename}"),caption=f"📦 <b>Export — Job #{job_id}</b>\nFormat: <b>{fmt.upper()}</b>\nItems: <b>{len(items)}</b>",parse_mode="HTML")
    except Exception as exc: await message.answer(f"❌ Export failed: <code>{str(exc)[:200]}</code>",parse_mode="HTML")

@router.message(Command("spiderjobs"))
@require_not_banned
async def spider_jobs_command(message: Message):
    try:
        from tools.scraper.engine import get_all_jobs; jobs=get_all_jobs(limit=10)
    except Exception as exc: await message.answer(f"❌ <code>{exc}</code>",parse_mode="HTML"); return
    if not jobs: await message.answer("📭 No crawl jobs yet."); return
    lines=["<b>🕷️ Recent Crawl Jobs</b>\n"]
    for job in jobs:
        icon={"done":"✅","running":"⏳","failed":"❌"}.get(job["status"],"❓")
        lines.append(f"{icon} <b>#{job['id']}</b> — <code>{(job['url'] or '')[:45]}</code>\n   {job['schema']} | {job['pages_crawled']} crawled | {job['pages_extracted']} extracted")
    await message.answer("\n\n".join(lines),parse_mode="HTML",disable_web_page_preview=True)

@router.message(Command("spiderstats"))
@require_not_banned
async def spider_stats_command(message: Message):
    try:
        from tools.scraper.engine import get_db_stats; s=get_db_stats()
    except Exception as exc: await message.answer(f"❌ <code>{exc}</code>",parse_mode="HTML"); return
    await message.answer(f"<b>🕷️ Spider Statistics</b>\n\n🗂️ Total jobs: <b>{s['total_jobs']}</b>\n✅ Completed: <b>{s['jobs_done']}</b>\n❌ Failed: <b>{s['jobs_failed']}</b>\n📦 Total items: <b>{s['total_items']}</b>",parse_mode="HTML")

@router.message(Command("schemas"))
@require_not_banned
async def schemas_command(message: Message):
    await message.answer("<b>📋 Extraction Schemas</b>\n\n🔹 <b>generic</b> — title, description, author, date, tags, summary\n🔹 <b>ecommerce</b> — product_name, price, brand, rating, availability, sku\n🔹 <b>news</b> / <b>article</b> — headline, author, date, outlet, topics, summary\n🔹 <b>job</b> / <b>job_posting</b> — job_title, company, location, salary, skills, apply_url\n🔹 <b>social</b> / <b>profile</b> — full_name, username, bio, followers, company\n\n<code>/scrape https://site.com --schema ecommerce</code>",parse_mode="HTML")
