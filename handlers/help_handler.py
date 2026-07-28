"""
Complete /help and /commands handler showing ALL bot commands.
Replaces the existing help handler in handlers/start.py
"""
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.permissions import require_not_banned

router = Router()

HELP_SECTIONS = {
    "ai": {
        "icon": "🤖",
        "title": "AI ASSISTANT",
        "commands": [
            ("/ai <message>", "Chat with Lovina AI"),
            ("/clear", "Clear your conversation history"),
            ("/explain <text>", "AI explains any text or tool output"),
            ("/threat <description>", "AI threat model for a target"),
            ("/report <findings>", "Generate a pentest report"),
            ("/dork <target>", "AI-generated Google dork queries"),
        ],
    },
    "scraper": {
        "icon": "🕷️",
        "title": "WEB SCRAPER",
        "commands": [
            ("/scrape <url>", "Crawl and extract structured data"),
            ("/scrape <url> --schema ecommerce", "Extract product data"),
            ("/scrape <url> --depth 2 --pages 10", "Multi-page crawl"),
            ("/scrape <url> --dynamic", "Playwright for JS-heavy sites"),
            ("/extract <url>", "Single-page AI extraction only"),
            ("/extract <url> --schema job", "Job posting extraction"),
            ("/schemas", "List all extraction schemas"),
            ("/spiderexport", "Download last crawl as JSON file"),
            ("/spiderexport --format csv --job 3", "Export specific job as CSV"),
            ("/spiderjobs", "View recent crawl job history"),
            ("/spiderstats", "Spider database statistics"),
        ],
    },
    "network": {
        "icon": "🌐",
        "title": "NETWORK & RECON",
        "commands": [
            ("/portscan <host>", "Scan common TCP ports"),
            ("/ping <host>", "ICMP ping with latency"),
            ("/traceroute <host>", "Hop-by-hop route trace"),
            ("/banner <host> <port>", "Grab service banner"),
            ("/rdns <ip>", "Reverse DNS lookup"),
            ("/asn <ip>", "ASN and organisation lookup"),
            ("/geoip <ip>", "IP geolocation with ISP info"),
            ("/dns <domain>", "DNS record lookup (A/MX/TXT/NS)"),
            ("/zonetransfer <domain>", "Attempt DNS zone transfer"),
            ("/dnsbrute <domain>", "DNS subdomain brute force"),
            ("/whois <domain>", "WHOIS registration data"),
            ("/ssl <domain>", "SSL certificate analyser"),
            ("/subdomain <domain>", "Passive subdomain discovery"),
            ("/httpmethods <url>", "Check allowed HTTP methods"),
            ("/openredirect <url>", "Test for open redirect vulnerability"),
        ],
    },
    "web": {
        "icon": "🔍",
        "title": "WEB ANALYSIS",
        "commands": [
            ("/headers <url>", "Security headers grade A-F"),
            ("/cors <url>", "CORS misconfiguration check"),
            ("/robots <url>", "Fetch and analyse robots.txt"),
            ("/sitemap <url>", "Parse sitemap.xml"),
            ("/techstack <url>", "Fingerprint tech stack"),
            ("/pagemeta <url>", "Extract page title and meta tags"),
            ("/links <url>", "Extract all internal and external links"),
            ("/harvestemail <url>", "Harvest email addresses from page"),
            ("/cookies <url>", "Analyse cookies for security flags"),
            ("/redirectchain <url>", "Follow and map redirect chain"),
            ("/wayback <url>", "Wayback Machine history lookup"),
            ("/forms <url>", "Find all forms and inputs"),
            ("/comments <url>", "Extract HTML comments"),
            ("/jsfiles <url>", "List all JavaScript files"),
            ("/cdn <url>", "Detect CDN provider"),
            ("/waf <url>", "Detect Web Application Firewall"),
            ("/cms <url>", "CMS detection (WP/Drupal/Shopify etc)"),
        ],
    },
    "osint": {
        "icon": "🕵️",
        "title": "OSINT",
        "commands": [
            ("/ip <ip>", "IP geolocation lookup"),
            ("/username <handle>", "Username hunt across 20 platforms"),
            ("/gitosint <username>", "Deep GitHub profile OSINT"),
            ("/emailcheck <email>", "Email validation + MX + disposable check"),
            ("/emailguess <first> <last> <domain>", "Generate email pattern guesses"),
            ("/archive <domain>", "Wayback Machine archive search"),
            ("/paste <keyword>", "Search Pastebin for keyword"),
            ("/reverseimg <url>", "Generate reverse image search links"),
            ("/gdork <target>", "Generate Google dorks for a target"),
        ],
    },
    "crypto": {
        "icon": "🔐",
        "title": "CRYPTOGRAPHY & ENCODING",
        "commands": [
            ("/hash <text>", "Generate MD5/SHA1/SHA256/SHA512"),
            ("/identify <hash>", "Identify hash type by length"),
            ("/encode <format> <text>", "Encode base64/hex/url/html/rot13"),
            ("/decode <format> <text>", "Decode base64/hex/url/html/rot13"),
            ("/extencode <format> <text>", "Extended encode base32/base58/base85/binary"),
            ("/baseconvert <val> <from> <to>", "Convert between number bases"),
            ("/hex2bin <hex>", "Hex to binary/decimal/octal"),
            ("/passgen [length]", "Generate secure password with entropy"),
            ("/passcheck <password>", "Check password strength"),
            ("/gentoken [length]", "Generate random token and UUID"),
            ("/uuidgen", "Generate UUID v4"),
            ("/uuidinfo <uuid>", "Parse and analyse a UUID"),
        ],
    },
    "ciphers": {
        "icon": "🔄",
        "title": "CIPHERS",
        "commands": [
            ("/caesar <text> <shift> [decrypt]", "Caesar cipher encrypt/decrypt"),
            ("/rotbrute <text>", "Brute force all 25 ROT shifts"),
            ("/vigenere <text> <key> [decrypt]", "Vigenere cipher encrypt/decrypt"),
            ("/atbash <text>", "Atbash reverse alphabet cipher"),
            ("/xorcipher <text> <key>", "XOR cipher outputs hex and base64"),
            ("/morse encode <text>", "Text to Morse code"),
            ("/morse decode <morse>", "Morse code to text"),
            ("/railfence <text> <rails> [decrypt]", "Rail fence transposition cipher"),
            ("/freqanalysis <text>", "Character frequency analysis"),
        ],
    },
    "text": {
        "icon": "📊",
        "title": "TEXT & DATA TOOLS",
        "commands": [
            ("/regex <pattern> <text>", "Test regex pattern against text"),
            ("/textstats <text>", "Word/char/sentence count and stats"),
            ("/diff <text1> ||| <text2>", "Compare two texts with separator |||"),
            ("/jsonformat <json>", "Pretty-print and validate JSON"),
            ("/json2csv <json>", "Convert JSON array to CSV file"),
            ("/csv2json <csv>", "Convert CSV data to JSON"),
            ("/xmlparse <xml>", "Parse and display XML structure"),
            ("/timestamp <unix>", "Convert Unix timestamp to readable date"),
            ("/epoch", "Get current Unix timestamp"),
            ("/ipcalc <ip/cidr>", "Subnet calculator network/broadcast/hosts"),
            ("/cidr <range>", "Expand CIDR range to list of IPs"),
            ("/extractip <text>", "Extract all IP addresses from text"),
            ("/mac <address>", "MAC address vendor lookup"),
        ],
    },
    "file": {
        "icon": "📁",
        "title": "FILE & BINARY ANALYSIS",
        "commands": [
            ("/filetype", "Detect file type by magic bytes (reply to file)"),
            ("/hexdump <url>", "Hex dump a file (reply to file or URL)"),
            ("/strings", "Extract printable strings (reply to file)"),
            ("/entropy", "Calculate Shannon entropy (reply to file)"),
            ("/zipinfo", "Inspect ZIP contents (reply to ZIP file)"),
            ("/exif", "Extract EXIF metadata (reply to image)"),
            ("/fileanalyse <url>", "Download and fully analyse any file URL"),
        ],
    },
    "ctf": {
        "icon": "🏁",
        "title": "CTF & LEARNING TOOLS",
        "commands": [
            ("/jwt", "Decode and analyse JWT token"),
            ("/magicbytes", "File signature reference table"),
            ("/ports [number]", "Port service reference or single lookup"),
            ("/httpstatus <code>", "HTTP status code lookup"),
            ("/owasp [1-10]", "OWASP Top 10 reference"),
            ("/revshell <ip> <port> [type]", "Generate reverse shell payload"),
            ("/sqli [type]", "SQL injection payload library"),
            ("/xss [context]", "XSS payload library by context"),
            ("/lfi", "Local file inclusion payload list"),
            ("/ssti [engine]", "SSTI payloads by template engine"),
        ],
    },
    "utility": {
        "icon": "🛠️",
        "title": "PERSONAL TOOLKIT",
        "commands": [
            ("/save <key> <value>", "Save a value to your personal store"),
            ("/get <key>", "Retrieve a saved value"),
            ("/del <key>", "Delete a saved key"),
            ("/kvlist", "List all your saved keys"),
            ("/note <id> <content>", "Save an encrypted note"),
            ("/getnote <id>", "Retrieve an encrypted note"),
            ("/notes", "List all your notes"),
            ("/delnote <id>", "Delete a note"),
            ("/tl add <event>", "Add event to investigation timeline"),
            ("/tl view", "View your investigation timeline"),
            ("/tl clear", "Clear the timeline"),
            ("/history", "View your recent command history"),
            ("/scope add <target>", "Add target to engagement scope"),
            ("/scope remove <target>", "Remove target from scope"),
            ("/scope list", "List all scoped targets"),
            ("/scope check <target>", "Check if target is in scope"),
            ("/alias set <name> <cmd>", "Create a command alias"),
            ("/alias get <name>", "Get an alias command"),
            ("/alias list", "List all aliases"),
            ("/alias del <name>", "Delete an alias"),
        ],
    },
    "admin": {
        "icon": "⚙️",
        "title": "ADMIN (Lord Noctis and Admins only)",
        "commands": [
            ("/ban <user_id>", "Ban a user from the bot"),
            ("/unban <user_id>", "Unban a user"),
            ("/promote <user_id>", "Promote user to sudo"),
            ("/demote <user_id>", "Demote sudo to regular user"),
            ("/broadcast <message>", "Broadcast message to all groups"),
            ("/stats", "Bot usage statistics"),
            ("/status", "Bot uptime and activity summary"),
            ("/addgroup", "Register group for broadcasts"),
        ],
    },
    "research": {
        "icon": "🔬",
        "title": "RESEARCH MODE",
        "commands": [
            ("/research", "Activate research mode (passphrase required)"),
            ("/endresearch", "Deactivate research mode"),
            ("/research_status", "Check if research mode is active"),
        ],
    },
}


def _build_section(section_key: str) -> str:
    section = HELP_SECTIONS[section_key]
    icon = section["icon"]
    title = section["title"]
    lines = [f"{icon} <b>{title}</b>"]
    for cmd, desc in section["commands"]:
        lines.append(f"  <code>{cmd}</code>\n    <i>{desc}</i>")
    return "\n".join(lines)


def _split_chunks(text: str, limit: int = 4000) -> list[str]:
    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n\n", 0, limit)
        if split_at == -1:
            split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        chunks.append(text)
    return chunks


def _build_full_help() -> list[str]:
    all_sections = "\n\n".join(_build_section(k) for k in HELP_SECTIONS)
    header = (
        "🤖 <b>LOVINA BOT — FULL COMMAND REFERENCE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Cybersecurity AI assistant by Lord Noctis\n"
        "All tools are for <b>authorised use only</b>.\n\n"
    )
    return _split_chunks(header + all_sections)


def _build_category_list() -> str:
    lines = [
        "🤖 <b>LOVINA BOT</b> — Cybersecurity AI Assistant\n",
        "Use /help <category> for detailed command list:\n",
    ]
    for key, section in HELP_SECTIONS.items():
        lines.append(f"  {section['icon']} <code>/help {key}</code> — {section['title']}")
    lines.append("\n<code>/help all</code> — Show every command at once")
    lines.append("<code>/commands</code> — Compact quick-reference list")
    return "\n".join(lines)


@router.message(Command("help"))
@require_not_banned
async def help_cmd(message: Message):
    arg = (message.text or "").split(maxsplit=1)
    category = arg[1].strip().lower() if len(arg) > 1 else ""

    if category == "all":
        for chunk in _build_full_help():
            await message.answer(chunk, parse_mode="HTML")
        return

    if category in HELP_SECTIONS:
        await message.answer(_build_section(category), parse_mode="HTML")
        return

    await message.answer(_build_category_list(), parse_mode="HTML")


@router.message(Command("commands"))
@require_not_banned
async def commands_cmd(message: Message):
    lines = ["<b>⚡ QUICK COMMAND REFERENCE</b>\n"]
    for section in HELP_SECTIONS.values():
        lines.append(f"\n{section['icon']} <b>{section['title']}</b>")
        for cmd, desc in section["commands"]:
            cmd_short = cmd.split()[0]
            lines.append(f"  {cmd_short} — {desc}")
    lines.append("\n\nUse /help <category> for usage details")
    lines.append("Categories: " + ", ".join(HELP_SECTIONS.keys()))
    for chunk in _split_chunks("\n".join(lines)):
        await message.answer(chunk, parse_mode="HTML")
