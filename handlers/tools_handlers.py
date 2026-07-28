from __future__ import annotations
import io,re
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile,Message
from utils.permissions import require_not_banned
from utils.formatter import Formatter

router = Router()

def _args(text,n=1): parts=(text or "").split(maxsplit=n); return parts[1:] if len(parts)>1 else []
def _arg(text): a=_args(text,1); return a[0].strip() if a else ""
def _rest(text): parts=(text or "").split(maxsplit=1); return parts[1].strip() if len(parts)>1 else ""
def _fmt(d,title=""):
    if isinstance(d,str): return f"❌ {d}"
    lines=[f"<b>{title}</b>\n"] if title else []
    for k,v in d.items():
        if v is None or v=="": continue
        if isinstance(v,list): lines.append(f"<b>{k}:</b>\n"+"".join(f"  • {i}\n" for i in v[:10])) if v else None
        elif isinstance(v,dict): lines.append(f"<b>{k}:</b> {str(v)[:200]}")
        else: lines.append(f"<b>{k}:</b> {str(v)[:300]}")
    return "\n".join(lines)
async def _send(msg,result,title=""):
    text=_fmt(result,title) if not isinstance(result,str) else f"❌ {result}"
    for chunk in Formatter.truncate(text): await msg.answer(chunk,parse_mode="HTML",disable_web_page_preview=True)

# ── NETWORK ──────────────────────────────────────────────────────────────────
@router.message(Command("ping"))
@require_not_banned
async def ping_cmd(message: Message):
    host=_arg(message.text)
    if not host: await message.answer("Usage: /ping <host>"); return
    m=await message.answer(f"📡 Pinging <code>{host}</code>...",parse_mode="HTML")
    from tools.network.recon import ping_host; result=await ping_host(host)
    await m.edit_text(_fmt(result if isinstance(result,dict) else {"result":result},f"📡 Ping — {host}"),parse_mode="HTML")

@router.message(Command("traceroute"))
@require_not_banned
async def traceroute_cmd(message: Message):
    host=_arg(message.text)
    if not host: await message.answer("Usage: /traceroute <host>"); return
    m=await message.answer(f"🛤️ Tracing <code>{host}</code>...",parse_mode="HTML")
    from tools.network.recon import traceroute_host; result=await traceroute_host(host)
    await m.delete(); await _send(message,result,f"🛤️ Traceroute — {host}")

@router.message(Command("banner"))
@require_not_banned
async def banner_cmd(message: Message):
    args=_args(message.text,2)
    if len(args)<2: await message.answer("Usage: /banner <host> <port>"); return
    try: port=int(args[1])
    except ValueError: await message.answer("Port must be a number"); return
    m=await message.answer(f"🏴 Grabbing banner from <code>{args[0]}:{port}</code>...",parse_mode="HTML")
    from tools.network.recon import banner_grab; result=await banner_grab(args[0],port)
    await m.edit_text(_fmt(result if isinstance(result,dict) else {"result":result},f"🏴 Banner — {args[0]}:{port}"),parse_mode="HTML")

@router.message(Command("rdns"))
@require_not_banned
async def rdns_cmd(message: Message):
    ip=_arg(message.text)
    if not ip: await message.answer("Usage: /rdns <IP>"); return
    from tools.network.recon import reverse_dns; await _send(message,await reverse_dns(ip),f"🔄 Reverse DNS — {ip}")

@router.message(Command("asn"))
@require_not_banned
async def asn_cmd(message: Message):
    ip=_arg(message.text)
    if not ip: await message.answer("Usage: /asn <IP>"); return
    m=await message.answer(f"🌐 ASN lookup <code>{ip}</code>...",parse_mode="HTML")
    from tools.network.recon import asn_lookup; result=await asn_lookup(ip)
    await m.edit_text(_fmt(result if isinstance(result,dict) else {"result":result},f"🌐 ASN — {ip}"),parse_mode="HTML")

@router.message(Command("geoip"))
@require_not_banned
async def geoip_cmd(message: Message):
    ip=_arg(message.text)
    if not ip: await message.answer("Usage: /geoip <IP>"); return
    m=await message.answer(f"🌍 GeoIP lookup <code>{ip}</code>...",parse_mode="HTML")
    from tools.network.recon import asn_lookup; result=await asn_lookup(ip)
    await m.edit_text(_fmt(result if isinstance(result,dict) else {"result":result},f"🌍 GeoIP — {ip}"),parse_mode="HTML")

@router.message(Command("zonetransfer"))
@require_not_banned
async def zonetransfer_cmd(message: Message):
    domain=_arg(message.text)
    if not domain: await message.answer("Usage: /zonetransfer <domain>"); return
    m=await message.answer(f"🗺️ Zone transfer <code>{domain}</code>...",parse_mode="HTML")
    from tools.network.recon import dns_zone_transfer; result=await dns_zone_transfer(domain)
    await m.delete(); await _send(message,result,f"🗺️ Zone Transfer — {domain}")

@router.message(Command("dnsbrute"))
@require_not_banned
async def dnsbrute_cmd(message: Message):
    domain=_arg(message.text)
    if not domain: await message.answer("Usage: /dnsbrute <domain>"); return
    m=await message.answer(f"💥 DNS brute force <code>{domain}</code>...",parse_mode="HTML")
    from tools.network.recon import dns_brute; result=await dns_brute(domain)
    await m.delete(); await _send(message,result,f"💥 DNS Brute — {domain}")

@router.message(Command("httpmethods"))
@require_not_banned
async def httpmethods_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /httpmethods <url>"); return
    from tools.network.recon import http_methods; await _send(message,await http_methods(url),f"🔧 HTTP Methods — {url}")

@router.message(Command("openredirect"))
@require_not_banned
async def openredirect_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /openredirect <url>"); return
    m=await message.answer(f"↪️ Testing redirect on <code>{url}</code>...",parse_mode="HTML")
    from tools.network.recon import open_redirect_check; result=await open_redirect_check(url)
    await m.delete(); await _send(message,result,f"↪️ Open Redirect — {url}")

# ── CRYPTO ───────────────────────────────────────────────────────────────────
@router.message(Command("passgen"))
@require_not_banned
async def passgen_cmd(message: Message):
    arg=_arg(message.text)
    try: length=max(8,min(128,int(arg))) if arg else 20
    except ValueError: length=20
    from tools.crypto.ciphers import generate_password; await _send(message,generate_password(length),"🔐 Password Generator")

@router.message(Command("passcheck"))
@require_not_banned
async def passcheck_cmd(message: Message):
    pw=_rest(message.text)
    if not pw: await message.answer("Usage: /passcheck <password>"); return
    from tools.crypto.ciphers import check_password_strength; await _send(message,check_password_strength(pw),"🔑 Password Strength")

@router.message(Command("gentoken"))
@require_not_banned
async def gentoken_cmd(message: Message):
    arg=_arg(message.text)
    try: length=max(8,min(256,int(arg))) if arg else 32
    except ValueError: length=32
    from tools.crypto.ciphers import generate_token; await _send(message,generate_token(length),"🎲 Token Generator")

@router.message(Command("caesar"))
@require_not_banned
async def caesar_cmd(message: Message):
    args=_args(message.text,3)
    if len(args)<2: await message.answer("Usage: /caesar <text> <shift> [decrypt]"); return
    try: shift=int(args[1])
    except ValueError: await message.answer("Shift must be a number"); return
    decrypt=len(args)>2 and args[2].lower()=="decrypt"
    from tools.crypto.ciphers import caesar_cipher; await _send(message,caesar_cipher(args[0],shift,decrypt),"🔄 Caesar Cipher")

@router.message(Command("rotbrute"))
@require_not_banned
async def rotbrute_cmd(message: Message):
    text=_rest(message.text)
    if not text: await message.answer("Usage: /rotbrute <ciphertext>"); return
    from tools.crypto.ciphers import rot_brute; results=rot_brute(text)
    lines=[f"<b>🔄 ROT Brute Force</b>\n<i>Input: {text}</i>\n"]+[f"<b>ROT{r['shift']:2d}:</b> <code>{r['text']}</code>" for r in results]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("vigenere"))
@require_not_banned
async def vigenere_cmd(message: Message):
    args=_args(message.text,3)
    if len(args)<2: await message.answer("Usage: /vigenere <text> <key> [decrypt]"); return
    decrypt=len(args)>2 and args[2].lower()=="decrypt"
    from tools.crypto.ciphers import vigenere_cipher; await _send(message,vigenere_cipher(args[0],args[1],decrypt),"🔐 Vigenère")

@router.message(Command("atbash"))
@require_not_banned
async def atbash_cmd(message: Message):
    text=_rest(message.text)
    if not text: await message.answer("Usage: /atbash <text>"); return
    from tools.crypto.ciphers import atbash_cipher; await _send(message,atbash_cipher(text),"🔁 Atbash")

@router.message(Command("xorcipher"))
@require_not_banned
async def xorcipher_cmd(message: Message):
    args=_args(message.text,2)
    if len(args)<2: await message.answer("Usage: /xorcipher <text> <key>"); return
    from tools.crypto.ciphers import xor_cipher; await _send(message,xor_cipher(args[0],args[1]),"⊕ XOR Cipher")

@router.message(Command("morse"))
@require_not_banned
async def morse_cmd(message: Message):
    args=_args(message.text,2)
    if not args or len(args)<2: await message.answer("Usage: /morse encode <text>\n       /morse decode <morse>"); return
    mode=args[0].lower(); content=" ".join(args[1:])
    from tools.crypto.ciphers import morse_encode,morse_decode
    await _send(message,morse_encode(content) if mode=="encode" else morse_decode(content) if mode=="decode" else "Use encode or decode","📡 Morse")

@router.message(Command("railfence"))
@require_not_banned
async def railfence_cmd(message: Message):
    args=_args(message.text,3)
    if len(args)<2: await message.answer("Usage: /railfence <text> <rails> [decrypt]"); return
    try: rails=int(args[1])
    except ValueError: await message.answer("Rails must be a number"); return
    decrypt=len(args)>2 and args[2].lower()=="decrypt"
    from tools.crypto.ciphers import rail_fence_cipher; await _send(message,rail_fence_cipher(args[0],rails,decrypt),"🚂 Rail Fence")

@router.message(Command("freqanalysis"))
@require_not_banned
async def freqanalysis_cmd(message: Message):
    text=_rest(message.text)
    if not text: await message.answer("Usage: /freqanalysis <ciphertext>"); return
    from tools.crypto.ciphers import frequency_analysis; await _send(message,frequency_analysis(text),"📊 Frequency Analysis")

@router.message(Command("baseconvert"))
@require_not_banned
async def baseconvert_cmd(message: Message):
    args=_args(message.text,3)
    if len(args)<3: await message.answer("Usage: /baseconvert <value> <from_base> <to_base>\nExample: /baseconvert FF 16 10"); return
    try:
        from tools.crypto.ciphers import base_convert; await _send(message,base_convert(args[0],int(args[1]),int(args[2])),"🔢 Base Convert")
    except Exception as e: await message.answer(f"❌ {e}")

@router.message(Command("hex2bin"))
@require_not_banned
async def hex2bin_cmd(message: Message):
    h=_arg(message.text)
    if not h: await message.answer("Usage: /hex2bin <hex>"); return
    from tools.crypto.ciphers import hex_to_binary; await _send(message,hex_to_binary(h),"🔢 Hex to Binary")

@router.message(Command("extencode"))
@require_not_banned
async def extencode_cmd(message: Message):
    args=_args(message.text,2)
    if len(args)<2: await message.answer("Usage: /extencode <format> <text>\nFormats: base32, base85, binary, decimal"); return
    from tools.crypto.ciphers import extended_encode; await _send(message,extended_encode(args[1],args[0]),f"🔡 Encode ({args[0]})")

@router.message(Command("uuidgen"))
@require_not_banned
async def uuidgen_cmd(message: Message):
    import uuid; await message.answer(f"🆔 <b>UUID v4</b>\n\n<code>{uuid.uuid4()}</code>",parse_mode="HTML")

@router.message(Command("uuidinfo"))
@require_not_banned
async def uuidinfo_cmd(message: Message):
    uid=_arg(message.text)
    if not uid: await message.answer("Usage: /uuidinfo <uuid>"); return
    from tools.crypto.ciphers import uuid_analyse; await _send(message,uuid_analyse(uid),"🆔 UUID Analysis")

# ── WEB ──────────────────────────────────────────────────────────────────────
@router.message(Command("headers"))
@require_not_banned
async def headers_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /headers <url>"); return
    m=await message.answer(f"🛡️ Analysing headers <code>{url}</code>...",parse_mode="HTML")
    from tools.web.analysis import analyse_security_headers; result=await analyse_security_headers(url)
    await m.delete(); await _send(message,result,f"🛡️ Security Headers — {url}")

@router.message(Command("cors"))
@require_not_banned
async def cors_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /cors <url>"); return
    m=await message.answer(f"🌐 CORS check <code>{url}</code>...",parse_mode="HTML")
    from tools.web.analysis import check_cors; result=await check_cors(url)
    await m.delete(); await _send(message,result,f"🌐 CORS — {url}")

@router.message(Command("robots"))
@require_not_banned
async def robots_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /robots <url>"); return
    from tools.web.analysis import fetch_robots; await _send(message,await fetch_robots(url),f"🤖 Robots.txt")

@router.message(Command("sitemap"))
@require_not_banned
async def sitemap_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /sitemap <url>"); return
    from tools.web.analysis import parse_sitemap; await _send(message,await parse_sitemap(url),f"🗺️ Sitemap")

@router.message(Command("techstack"))
@require_not_banned
async def techstack_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /techstack <url>"); return
    m=await message.answer(f"🔍 Detecting tech stack <code>{url}</code>...",parse_mode="HTML")
    from tools.web.analysis import detect_tech_stack; result=await detect_tech_stack(url)
    await m.delete(); await _send(message,result,f"🔍 Tech Stack")

@router.message(Command("pagemeta"))
@require_not_banned
async def pagemeta_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /pagemeta <url>"); return
    from tools.web.analysis import extract_page_meta; await _send(message,await extract_page_meta(url),f"📄 Page Meta")

@router.message(Command("links"))
@require_not_banned
async def links_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /links <url>"); return
    from tools.web.analysis import extract_links_from_page; await _send(message,await extract_links_from_page(url),"🔗 Links")

@router.message(Command("harvestemail"))
@require_not_banned
async def harvestemail_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /harvestemail <url>"); return
    from tools.web.analysis import harvest_emails; await _send(message,await harvest_emails(url),"📧 Email Harvest")

@router.message(Command("cookies"))
@require_not_banned
async def cookies_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /cookies <url>"); return
    from tools.web.analysis import analyse_cookies; await _send(message,await analyse_cookies(url),"🍪 Cookie Analysis")

@router.message(Command("redirectchain"))
@require_not_banned
async def redirectchain_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /redirectchain <url>"); return
    from tools.web.analysis import check_redirect_chain; await _send(message,await check_redirect_chain(url),"↪️ Redirect Chain")

@router.message(Command("wayback"))
@require_not_banned
async def wayback_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /wayback <domain>"); return
    m=await message.answer(f"⏳ Wayback Machine <code>{url}</code>...",parse_mode="HTML")
    from tools.web.analysis import wayback_lookup; result=await wayback_lookup(url)
    await m.delete(); await _send(message,result,"⏳ Wayback Machine")

@router.message(Command("forms"))
@require_not_banned
async def forms_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /forms <url>"); return
    from tools.web.analysis import find_forms; await _send(message,await find_forms(url),"📝 Forms")

@router.message(Command("comments"))
@require_not_banned
async def comments_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /comments <url>"); return
    from tools.web.analysis import extract_comments; await _send(message,await extract_comments(url),"💬 HTML Comments")

@router.message(Command("jsfiles"))
@require_not_banned
async def jsfiles_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /jsfiles <url>"); return
    from tools.web.analysis import list_js_files; await _send(message,await list_js_files(url),"📜 JS Files")

@router.message(Command("cdn"))
@require_not_banned
async def cdn_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /cdn <url>"); return
    from tools.web.analysis import detect_cdn; await _send(message,await detect_cdn(url),"☁️ CDN Detection")

@router.message(Command("waf"))
@require_not_banned
async def waf_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /waf <url>"); return
    m=await message.answer(f"🛡️ WAF detection <code>{url}</code>...",parse_mode="HTML")
    from tools.web.analysis import detect_waf; result=await detect_waf(url)
    await m.delete(); await _send(message,result,"🛡️ WAF Detection")

@router.message(Command("cms"))
@require_not_banned
async def cms_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /cms <url>"); return
    from tools.osint.recon import cms_detector; await _send(message,await cms_detector(url),"🏗️ CMS Detection")

# ── TEXT & DATA ───────────────────────────────────────────────────────────────
@router.message(Command("regex"))
@require_not_banned
async def regex_cmd(message: Message):
    args=_args(message.text,2)
    if len(args)<2: await message.answer("Usage: /regex <pattern> <text>"); return
    from tools.text.analysis import regex_test; await _send(message,regex_test(args[0],args[1]),"🔍 Regex Tester")

@router.message(Command("textstats"))
@require_not_banned
async def textstats_cmd(message: Message):
    text=_rest(message.text)
    if not text: await message.answer("Usage: /textstats <text>"); return
    from tools.text.analysis import text_stats; await _send(message,text_stats(text),"📊 Text Stats")

@router.message(Command("diff"))
@require_not_banned
async def diff_cmd(message: Message):
    rest=_rest(message.text)
    if "|||" not in rest: await message.answer("Usage: /diff <text1> ||| <text2>"); return
    parts=rest.split("|||",1)
    from tools.text.analysis import diff_texts; await _send(message,diff_texts(parts[0].strip(),parts[1].strip()),"📝 Text Diff")

@router.message(Command("jsonformat"))
@require_not_banned
async def jsonformat_cmd(message: Message):
    raw=_rest(message.text)
    if not raw: await message.answer("Usage: /jsonformat <json>"); return
    from tools.text.analysis import format_json; await _send(message,format_json(raw),"📋 JSON Format")

@router.message(Command("json2csv"))
@require_not_banned
async def json2csv_cmd(message: Message):
    raw=_rest(message.text)
    if not raw: await message.answer("Usage: /json2csv <json array>"); return
    from tools.text.analysis import json_to_csv; result=json_to_csv(raw)
    if isinstance(result,str): await message.answer(f"❌ {result}"); return
    await message.answer_document(BufferedInputFile(result["csv"].encode(),filename="output.csv"),caption=f"✅ {result['rows']} rows × {len(result['columns'])} columns")

@router.message(Command("csv2json"))
@require_not_banned
async def csv2json_cmd(message: Message):
    raw=_rest(message.text)
    if not raw: await message.answer("Usage: /csv2json <csv data>"); return
    from tools.text.analysis import csv_to_json; await _send(message,csv_to_json(raw),"📋 CSV to JSON")

@router.message(Command("xmlparse"))
@require_not_banned
async def xmlparse_cmd(message: Message):
    raw=_rest(message.text)
    if not raw: await message.answer("Usage: /xmlparse <xml>"); return
    from tools.text.analysis import parse_xml; await _send(message,parse_xml(raw),"📋 XML Parser")

@router.message(Command("timestamp"))
@require_not_banned
async def timestamp_cmd(message: Message):
    val=_arg(message.text)
    if not val: await message.answer("Usage: /timestamp <unix timestamp>"); return
    from tools.text.analysis import convert_timestamp; await _send(message,convert_timestamp(val),"⏱️ Timestamp")

@router.message(Command("epoch"))
@require_not_banned
async def epoch_cmd(message: Message):
    from tools.text.analysis import current_epoch; await _send(message,current_epoch(),"⏱️ Current Epoch")

@router.message(Command("ipcalc"))
@require_not_banned
async def ipcalc_cmd(message: Message):
    cidr=_arg(message.text)
    if not cidr: await message.answer("Usage: /ipcalc <IP/CIDR>\nExample: /ipcalc 192.168.1.0/24"); return
    from tools.text.analysis import ip_calculator; await _send(message,ip_calculator(cidr),f"🔢 IP Calc — {cidr}")

@router.message(Command("cidr"))
@require_not_banned
async def cidr_cmd(message: Message):
    cidr=_arg(message.text)
    if not cidr: await message.answer("Usage: /cidr <range>\nExample: /cidr 192.168.1.0/28"); return
    from tools.text.analysis import expand_cidr; await _send(message,expand_cidr(cidr),f"📋 CIDR — {cidr}")

@router.message(Command("extractip"))
@require_not_banned
async def extractip_cmd(message: Message):
    text=_rest(message.text)
    if not text: await message.answer("Usage: /extractip <text>"); return
    from tools.text.analysis import extract_ips_from_text; await _send(message,extract_ips_from_text(text),"🔍 IP Extractor")

@router.message(Command("mac"))
@require_not_banned
async def mac_cmd(message: Message):
    mac=_arg(message.text)
    if not mac: await message.answer("Usage: /mac <MAC address>"); return
    from tools.text.analysis import mac_lookup; await _send(message,mac_lookup(mac),f"🔌 MAC — {mac}")

# ── FILE ANALYSIS ─────────────────────────────────────────────────────────────
@router.message(Command("filetype"))
@require_not_banned
async def filetype_cmd(message: Message):
    if not message.reply_to_message or not message.reply_to_message.document: await message.answer("Reply to a file with /filetype"); return
    doc=message.reply_to_message.document; f=await message.bot.get_file(doc.file_id); buf=io.BytesIO(); await message.bot.download_file(f.file_path,buf)
    from tools.filetools.analysis import analyse_file_bytes; await _send(message,analyse_file_bytes(buf.getvalue(),doc.file_name or "file"),"📁 File Analysis")

@router.message(Command("hexdump"))
@require_not_banned
async def hexdump_cmd(message: Message):
    url=_arg(message.text)
    if message.reply_to_message and message.reply_to_message.document:
        doc=message.reply_to_message.document; f=await message.bot.get_file(doc.file_id); buf=io.BytesIO(); await message.bot.download_file(f.file_path,buf)
        from tools.filetools.analysis import hex_dump; result=hex_dump(buf.getvalue())
        await message.answer(f"<b>🔍 Hex Dump — {doc.file_name}</b>\n\n<pre>{result[:3000]}</pre>",parse_mode="HTML")
    elif url:
        from tools.filetools.analysis import fetch_and_analyse_file; await _send(message,await fetch_and_analyse_file(url),"🔍 File Dump")
    else: await message.answer("Usage: /hexdump <url> OR reply to a file with /hexdump")

@router.message(Command("strings"))
@require_not_banned
async def strings_cmd(message: Message):
    if not message.reply_to_message or not message.reply_to_message.document: await message.answer("Reply to a file with /strings"); return
    doc=message.reply_to_message.document; f=await message.bot.get_file(doc.file_id); buf=io.BytesIO(); await message.bot.download_file(f.file_path,buf)
    from tools.filetools.analysis import extract_strings_from_bytes; strings=extract_strings_from_bytes(buf.getvalue())
    lines=[f"<b>📝 Strings — {doc.file_name}</b>",f"Found {len(strings)} strings\n"]+[f"<code>{s[:100]}</code>" for s in strings[:40]]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("entropy"))
@require_not_banned
async def entropy_cmd(message: Message):
    if not message.reply_to_message or not message.reply_to_message.document: await message.answer("Reply to a file with /entropy"); return
    doc=message.reply_to_message.document; f=await message.bot.get_file(doc.file_id); buf=io.BytesIO(); await message.bot.download_file(f.file_path,buf); data=buf.getvalue()
    from tools.filetools.analysis import compute_entropy,_entropy_note; e=compute_entropy(data)
    await message.answer(f"<b>📊 Entropy — {doc.file_name}</b>\n\nEntropy: <b>{e} / 8.0</b>\n{_entropy_note(e)}\nSize: {len(data)} bytes",parse_mode="HTML")

@router.message(Command("zipinfo"))
@require_not_banned
async def zipinfo_cmd(message: Message):
    if not message.reply_to_message or not message.reply_to_message.document: await message.answer("Reply to a ZIP file with /zipinfo"); return
    doc=message.reply_to_message.document; f=await message.bot.get_file(doc.file_id); buf=io.BytesIO(); await message.bot.download_file(f.file_path,buf)
    from tools.filetools.analysis import inspect_zip; await _send(message,inspect_zip(buf.getvalue()),f"📦 ZIP — {doc.file_name}")

@router.message(Command("exif"))
@require_not_banned
async def exif_cmd(message: Message):
    if not message.reply_to_message or not (message.reply_to_message.photo or message.reply_to_message.document): await message.answer("Reply to an image with /exif"); return
    if message.reply_to_message.photo: photo=message.reply_to_message.photo[-1]; f=await message.bot.get_file(photo.file_id); fname="photo.jpg"
    else: doc=message.reply_to_message.document; f=await message.bot.get_file(doc.file_id); fname=doc.file_name or "image"
    buf=io.BytesIO(); await message.bot.download_file(f.file_path,buf)
    from tools.filetools.analysis import extract_exif; await _send(message,await extract_exif(buf.getvalue(),fname),f"📸 EXIF — {fname}")

@router.message(Command("fileanalyse"))
@require_not_banned
async def fileanalyse_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /fileanalyse <url>"); return
    m=await message.answer(f"📥 Downloading <code>{url}</code>...",parse_mode="HTML")
    from tools.filetools.analysis import fetch_and_analyse_file; result=await fetch_and_analyse_file(url)
    await m.delete(); await _send(message,result,"📁 File Analysis")

# ── OSINT ─────────────────────────────────────────────────────────────────────
@router.message(Command("gitosint"))
@require_not_banned
async def gitosint_cmd(message: Message):
    username=_arg(message.text)
    if not username: await message.answer("Usage: /gitosint <github username>"); return
    m=await message.answer(f"🐙 GitHub OSINT <code>{username}</code>...",parse_mode="HTML")
    from tools.osint.recon import github_osint; result=await github_osint(username)
    await m.delete(); await _send(message,result,f"🐙 GitHub — {username}")

@router.message(Command("emailcheck"))
@require_not_banned
async def emailcheck_cmd(message: Message):
    email=_arg(message.text)
    if not email: await message.answer("Usage: /emailcheck <email>"); return
    from tools.osint.recon import email_check; await _send(message,await email_check(email),f"📧 Email Check")

@router.message(Command("archive"))
@require_not_banned
async def archive_cmd(message: Message):
    domain=_arg(message.text)
    if not domain: await message.answer("Usage: /archive <domain>"); return
    m=await message.answer(f"📚 Searching archive <code>{domain}</code>...",parse_mode="HTML")
    from tools.osint.recon import archive_search; result=await archive_search(domain)
    await m.delete(); await _send(message,result,"📚 Archive Search")

@router.message(Command("emailguess"))
@require_not_banned
async def emailguess_cmd(message: Message):
    args=_args(message.text,3)
    if len(args)<3: await message.answer("Usage: /emailguess <firstname> <lastname> <domain>"); return
    from tools.osint.recon import generate_email_patterns; await _send(message,generate_email_patterns(args[0],args[1],args[2]),"📧 Email Patterns")

@router.message(Command("reverseimg"))
@require_not_banned
async def reverseimg_cmd(message: Message):
    url=_arg(message.text)
    if not url: await message.answer("Usage: /reverseimg <image url>"); return
    from tools.osint.recon import reverse_image_search_links; await _send(message,reverse_image_search_links(url),"🔍 Reverse Image Search")

@router.message(Command("paste"))
@require_not_banned
async def paste_cmd(message: Message):
    keyword=_rest(message.text)
    if not keyword: await message.answer("Usage: /paste <keyword>"); return
    m=await message.answer(f"📋 Searching Pastebin <code>{keyword}</code>...",parse_mode="HTML")
    from tools.osint.recon import pastebin_search; result=await pastebin_search(keyword)
    await m.delete(); await _send(message,result,f"📋 Pastebin — {keyword}")

@router.message(Command("gdork"))
@require_not_banned
async def gdork_cmd(message: Message):
    target=_arg(message.text)
    if not target: await message.answer("Usage: /gdork <domain>"); return
    from tools.osint.recon import generate_dorks; result=generate_dorks(target)
    lines=[f"<b>🔍 Google Dorks — {result['target']}</b>\n"]+[f"{i}. <code>{d}</code>" for i,d in enumerate(result["dorks"],1)]+["\n⚠️ For authorised reconnaissance only"]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

# ── CTF ──────────────────────────────────────────────────────────────────────
@router.message(Command("magicbytes"))
@require_not_banned
async def magicbytes_cmd(message: Message):
    from tools.ctf.tools import get_magic_bytes
    for chunk in Formatter.truncate(get_magic_bytes()): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("ports"))
@require_not_banned
async def ports_cmd(message: Message):
    arg=_arg(message.text)
    if arg:
        try:
            from tools.ctf.tools import lookup_port; await _send(message,lookup_port(int(arg)),f"🔌 Port {arg}")
        except ValueError: await message.answer("Usage: /ports [port number]")
    else:
        from tools.ctf.tools import get_ports_table
        for chunk in Formatter.truncate(get_ports_table()): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("httpstatus"))
@require_not_banned
async def httpstatus_cmd(message: Message):
    code=_arg(message.text)
    if not code: await message.answer("Usage: /httpstatus <code>"); return
    try:
        from tools.ctf.tools import lookup_http_status; await _send(message,lookup_http_status(int(code)),f"🌐 HTTP {code}")
    except ValueError: await message.answer("Please provide a numeric status code")

@router.message(Command("owasp"))
@require_not_banned
async def owasp_cmd(message: Message):
    arg=_arg(message.text)
    from tools.ctf.tools import get_owasp; items=get_owasp()
    if arg and arg.isdigit():
        idx=int(arg)-1
        if 0<=idx<len(items):
            item=items[idx]
            await message.answer(f"<b>🔐 {item['id']} — {item['name']}</b>\n\n{item['desc']}\n\n<b>Examples:</b>\n"+"\n".join(f"• {e}" for e in item["examples"]),parse_mode="HTML"); return
    lines=["<b>🔐 OWASP Top 10 (2021)</b>\n"]+[f"<b>{i['rank']}. {i['id']}</b> — {i['name']}\n   <i>{i['desc'][:100]}...</i>" for i in items]+["\nUse /owasp <1-10> for details"]
    for chunk in Formatter.truncate("\n\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("revshell"))
@require_not_banned
async def revshell_cmd(message: Message):
    args=_args(message.text,3)
    if len(args)<2:
        from tools.ctf.tools import REVERSE_SHELLS; await message.answer(f"Usage: /revshell <ip> <port> [type]\nTypes: {', '.join(REVERSE_SHELLS.keys())}"); return
    try: port=int(args[1])
    except ValueError: await message.answer("Port must be a number"); return
    shell=args[2] if len(args)>2 else "bash"
    from tools.ctf.tools import generate_reverse_shell; result=generate_reverse_shell(args[0],port,shell)
    if isinstance(result,str): await message.answer(f"❌ {result}"); return
    await message.answer(f"<b>🐚 Reverse Shell — {shell}</b>\n\n<b>Listener:</b>\n<code>{result['listener']}</code>\n\n<b>Payload:</b>\n<code>{result['command']}</code>\n\n<i>{result['note']}</i>",parse_mode="HTML")

@router.message(Command("sqli"))
@require_not_banned
async def sqli_cmd(message: Message):
    t=_arg(message.text) or "all"
    from tools.ctf.tools import get_sqli_payloads; result=get_sqli_payloads(t)
    if isinstance(result,str): await message.answer(f"❌ {result}"); return
    if t=="all":
        lines=["<b>💉 SQLi Payload Library</b>\n"]
        for pt,payloads in result["payloads"].items(): lines.append(f"\n<b>{pt}:</b>"); lines.extend(f"<code>{p}</code>" for p in payloads[:2])
        lines.append(f"\nTypes: {', '.join(result['types'])}")
    else: lines=[f"<b>💉 SQLi — {t}</b>\n"]+[f"<code>{p}</code>" for p in result["payloads"]]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("xss"))
@require_not_banned
async def xss_cmd(message: Message):
    ctx=_arg(message.text) or "all"
    from tools.ctf.tools import get_xss_payloads; result=get_xss_payloads(ctx)
    if isinstance(result,str): await message.answer(f"❌ {result}"); return
    if ctx=="all":
        lines=["<b>⚡ XSS Payload Library</b>\n"]
        for c,payloads in result["payloads"].items(): lines.append(f"\n<b>{c}:</b>"); lines.extend(f"<code>{p}</code>" for p in payloads[:2])
    else: lines=[f"<b>⚡ XSS — {ctx}</b>\n"]+[f"<code>{p}</code>" for p in result["payloads"]]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("lfi"))
@require_not_banned
async def lfi_cmd(message: Message):
    from tools.ctf.tools import get_lfi_payloads; result=get_lfi_payloads()
    lines=[f"<b>📂 LFI Payloads ({result['count']})</b>\n"]+[f"<code>{p}</code>" for p in result["payloads"]]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("ssti"))
@require_not_banned
async def ssti_cmd(message: Message):
    engine=_arg(message.text) or "detection"
    from tools.ctf.tools import get_ssti_payloads,SSTI; result=get_ssti_payloads(engine)
    if isinstance(result,str): await message.answer(f"❌ {result}\nEngines: {', '.join(SSTI.keys())}"); return
    lines=[f"<b>🧨 SSTI — {engine}</b>\n",f"<i>{result.get('note','')}</i>\n"]+[f"<code>{p}</code>" for p in result["payloads"]]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

# ── UTILITY ───────────────────────────────────────────────────────────────────
@router.message(Command("save"))
@require_not_banned
async def save_cmd(message: Message):
    args=_args(message.text,2)
    if len(args)<2: await message.answer("Usage: /save <key> <value>"); return
    from tools.utility.storage import kv_set; await _send(message,kv_set(message.from_user.id,args[0],args[1]),"💾 Saved")

@router.message(Command("get"))
@require_not_banned
async def get_cmd(message: Message):
    key=_arg(message.text)
    if not key: await message.answer("Usage: /get <key>"); return
    from tools.utility.storage import kv_get; await _send(message,kv_get(message.from_user.id,key),f"📂 {key}")

@router.message(Command("del"))
@require_not_banned
async def del_cmd(message: Message):
    key=_arg(message.text)
    if not key: await message.answer("Usage: /del <key>"); return
    from tools.utility.storage import kv_delete; await _send(message,kv_delete(message.from_user.id,key),"🗑️ Deleted")

@router.message(Command("kvlist"))
@require_not_banned
async def kvlist_cmd(message: Message):
    from tools.utility.storage import kv_list; await _send(message,kv_list(message.from_user.id),"📂 Saved Keys")

@router.message(Command("note"))
@require_not_banned
async def note_cmd(message: Message):
    args=_args(message.text,2)
    if len(args)<2: await message.answer("Usage: /note <id> <content>"); return
    from tools.utility.storage import note_save; await _send(message,note_save(message.from_user.id,args[0],args[1]),"🔐 Note Saved")

@router.message(Command("getnote"))
@require_not_banned
async def getnote_cmd(message: Message):
    nid=_arg(message.text)
    if not nid: await message.answer("Usage: /getnote <id>"); return
    from tools.utility.storage import note_get; await _send(message,note_get(message.from_user.id,nid),f"📝 Note")

@router.message(Command("notes"))
@require_not_banned
async def notes_cmd(message: Message):
    from tools.utility.storage import note_list; await _send(message,note_list(message.from_user.id),"📝 Notes")

@router.message(Command("delnote"))
@require_not_banned
async def delnote_cmd(message: Message):
    nid=_arg(message.text)
    if not nid: await message.answer("Usage: /delnote <id>"); return
    from tools.utility.storage import note_delete; await _send(message,note_delete(message.from_user.id,nid),"🗑️ Note Deleted")

@router.message(Command("tl"))
@require_not_banned
async def timeline_cmd(message: Message):
    args=_args(message.text,2)
    if not args: await message.answer("Usage: /tl add <event> | /tl view | /tl clear"); return
    action=args[0].lower()
    from tools.utility.storage import timeline_add,timeline_view,timeline_clear
    if action=="add":
        content=args[1] if len(args)>1 else ""
        if not content: await message.answer("Usage: /tl add <event>"); return
        await _send(message,timeline_add(message.from_user.id,content),"📅 Timeline")
    elif action=="view":
        result=timeline_view(message.from_user.id)
        lines=[f"<b>📅 Timeline ({result['total']} events)</b>\n"]+[f"<b>[{e['timestamp'][:16].replace('T',' ')}]</b> {e['event']}" for e in result["events"]]
        for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")
    elif action=="clear": await _send(message,timeline_clear(message.from_user.id),"🗑️ Timeline")
    else: await message.answer("Usage: /tl add|view|clear")

@router.message(Command("history"))
@require_not_banned
async def history_cmd(message: Message):
    from tools.utility.storage import history_view; result=history_view(message.from_user.id,20)
    lines=[f"<b>📜 History ({result['total']})</b>\n"]+[f"<code>[{e['timestamp'][:16].replace('T',' ')}]</code> {e['command']}" for e in result["recent"]]
    for chunk in Formatter.truncate("\n".join(lines)): await message.answer(chunk,parse_mode="HTML")

@router.message(Command("scope"))
@require_not_banned
async def scope_cmd(message: Message):
    args=_args(message.text,2); 
    if not args: await message.answer("Usage: /scope add|remove|list|check <target>"); return
    action=args[0].lower(); target=args[1] if len(args)>1 else ""
    from tools.utility.storage import scope_add,scope_remove,scope_list,scope_check
    if action=="add": await _send(message,scope_add(message.from_user.id,target),"🎯 Scope") if target else await message.answer("Usage: /scope add <target>")
    elif action=="remove": await _send(message,scope_remove(message.from_user.id,target),"🎯 Scope") if target else await message.answer("Usage: /scope remove <target>")
    elif action=="list": await _send(message,scope_list(message.from_user.id),"🎯 Scope")
    elif action=="check": await _send(message,scope_check(message.from_user.id,target),"🎯 Scope Check") if target else await message.answer("Usage: /scope check <target>")
    else: await message.answer("Usage: /scope add|remove|list|check")

@router.message(Command("alias"))
@require_not_banned
async def alias_cmd(message: Message):
    args=_args(message.text,3)
    if not args: await message.answer("Usage: /alias set|get|list|del <name>"); return
    action=args[0].lower()
    from tools.utility.storage import alias_set,alias_get,alias_list,alias_delete
    if action=="set":
        if len(args)<3: await message.answer("Usage: /alias set <name> <command>"); return
        await _send(message,alias_set(message.from_user.id,args[1],args[2]),"⚡ Alias Saved")
    elif action=="get": await _send(message,alias_get(message.from_user.id,args[1]),"⚡ Alias") if len(args)>1 else await message.answer("Usage: /alias get <name>")
    elif action=="list": await _send(message,alias_list(message.from_user.id),"⚡ Aliases")
    elif action in ("del","delete","remove"): await _send(message,alias_delete(message.from_user.id,args[1]),"🗑️ Alias") if len(args)>1 else await message.answer("Usage: /alias del <name>")
    else: await message.answer("Usage: /alias set|get|list|del")
