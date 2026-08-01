# Lovina Bot — AI-Powered Cybersecurity Assistant

<div align="center">

**Lovina** is a production-ready Telegram bot that combines a strategic AI assistant, 140+ cybersecurity tools, a stealth web scraper, and a personal investigation toolkit — all accessible from Telegram with no browser required.

---

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.4.1-green?style=flat-square)](https://aiogram.dev)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange?style=flat-square)](https://groq.com)
[![Railway](https://img.shields.io/badge/Deployed_on-Railway-purple?style=flat-square)](https://railway.app)

</div>

---

## 📖 Table of Contents

1. [What Lovina Can Do](#-what-lovina-can-do)
2. [Tech Stack](#-tech-stack)
3. [Quick Start — Local](#-quick-start--local-setup)
4. [Deploy to Railway](#-deploy-to-railway)
5. [Environment Variables](#-environment-variables)
6. [All Commands Reference](#-all-commands-reference)
   - [AI Assistant](#-ai-assistant)
   - [Web Scraper](#️-web-scraper)
   - [OSINT](#️-osint)
   - [Network & Recon](#-network--recon)
   - [Web Analysis](#-web-analysis)
   - [Cryptography & Encoding](#-cryptography--encoding)
   - [Ciphers](#-ciphers)
   - [Text & Data Tools](#-text--data-tools)
   - [File & Binary Analysis](#-file--binary-analysis)
   - [CTF & Learning Tools](#-ctf--learning-tools)
   - [Personal Toolkit](#️-personal-toolkit)
   - [Research Mode](#-research-mode)
   - [Admin Commands](#️-admin-commands)
7. [Permission System](#-permission-system)
8. [Rate Limiting](#-rate-limiting)
9. [Project Structure](#-project-structure)
10. [Security Notes](#-security-notes)
11. [Disclaimer](#️-disclaimer)

---

## 🔥 What Lovina Can Do

Lovina is not a simple command bot. It is a full cybersecurity research platform inside Telegram:

- **Talk to an AI** that thinks like a strategic analyst — dark academia personality, cybersecurity-aware, never generic
- **Scrape any website** from Telegram using Chrome TLS impersonation that bypasses most bot detection, with AI-powered structured data extraction
- **Run 140+ security tools** — from port scanning and SSL analysis to JWT decoding, SSTI payloads, and reverse shell generation
- **Investigate targets** using OSINT tools that require zero API keys — subdomain discovery, email harvesting, GitHub profiling, Wayback Machine, Pastebin search
- **Store your work** — save notes (encrypted), build investigation timelines, manage engagement scope, create command aliases
- **Learn security concepts** — OWASP Top 10 reference, payload libraries for SQLi/XSS/LFI/SSTI, reverse shell generators, cipher tools
- **Analyse files** — detect file types by magic bytes, extract EXIF from photos, compute entropy, inspect ZIP contents, hex dump binaries

Everything works from your phone. No VPN, no terminal, no setup after deployment.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Bot framework | aiogram 3.4.1 (async) |
| AI backend | Groq API — LLaMA 3.3-70B Versatile |
| HTTP client | curl-cffi (Chrome TLS fingerprint impersonation) + httpx fallback |
| HTML parsing | BeautifulSoup4 + lxml |
| DNS tools | dnspython 2.6.1 |
| WHOIS | python-whois 0.9.4 |
| Image processing | Pillow 11.1.0 |
| Encryption | cryptography 42.0.0 (Fernet for notes) |
| Data validation | pydantic 2.7+ |
| User-agent spoofing | fake-useragent |
| State management | aiogram FSM with MemoryStorage |
| Storage | JSON files (users, bans, sudo, stats) + SQLite (spider jobs) |
| Deployment | Railway (via Procfile) |
| Language | Python 3.11+ |

---

## 🚀 Quick Start — Local Setup

### Prerequisites

- Python 3.11 or higher
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A free Groq API key from [console.groq.com](https://console.groq.com)
- Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot))

### Step 1 — Clone the repository

```bash
git clone https://github.com/Chiagoziem4/Lovina-bot.git
cd Lovina-bot
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

```bash
cp .env.example .env
nano .env   # or use any text editor
```

Fill in your `.env` file (see [Environment Variables](#-environment-variables) section below).

### Step 5 — Run the bot

```bash
python main.py
```

You should see the startup banner in your terminal. Open Telegram, find your bot, and send `/start`.

---

## ☁️ Deploy to Railway

Railway gives you a free hosted server that keeps the bot running 24/7.

### Step 1 — Push your code to GitHub

```bash
git init
git add .
git commit -m "Initial Lovina bot deployment"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — Create a Railway project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your Lovina bot repository
4. Railway automatically detects the `Procfile` and starts the build

### Step 3 — Add environment variables

In your Railway project dashboard:
1. Click on your service → **Variables** tab
2. Click **New Variable** and add each of the following:

```
BOT_TOKEN              = your Telegram bot token
LORD_NOCTIS_ID         = your Telegram user ID (number only)
GROQ_API_KEY           = your Groq API key
RESEARCH_PASSPHRASE    = a secret phrase only you know
SPIDER_DATA_DIR        = data/spider
MAX_CONTENT_CHARS      = 12000
SPIDER_MAX_PAGES       = 20
SPIDER_DELAY           = 2.0
SPIDER_RANDOMISE_DELAY = true
```

### Step 4 — Deploy

Railway auto-deploys when you push to main. Every `git push` triggers a new deploy. View logs live in the Railway dashboard under the **Deployments** tab.

---

## 🔑 Environment Variables

### Required

| Variable | Description | Example |
|---|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `8627899799:AAH...` |
| `LORD_NOCTIS_ID` | Your Telegram user ID — gives you owner-level access | `123456789` |
| `GROQ_API_KEY` | Free API key from console.groq.com | `gsk_...` |
| `RESEARCH_PASSPHRASE` | Secret passphrase to activate Research Mode | `your_secret_here` |

### Spider / Scraper Settings (Optional — have sensible defaults)

| Variable | Default | Description |
|---|---|---|
| `SPIDER_DATA_DIR` | `data/spider` | Directory for spider SQLite DB and user data |
| `MAX_CONTENT_CHARS` | `12000` | Max characters of page text sent to AI for extraction |
| `SPIDER_MAX_PAGES` | `20` | Max pages per crawl job |
| `SPIDER_DELAY` | `2.0` | Delay between requests in seconds |
| `SPIDER_RANDOMISE_DELAY` | `true` | Add random jitter to request delays |

### Optional API Keys (Enable extra features if provided)

| Variable | Description |
|---|---|
| `SHODAN_API_KEY` | Shodan.io API key for host intelligence |
| `ABUSEIPDB_API_KEY` | AbuseIPDB API key for IP reputation |
| `HIBP_API_KEY` | HaveIBeenPwned API key for breach checks |

> **Never commit your `.env` file to GitHub.** It is already in `.gitignore`. Always set real credentials as Railway environment variables, never in the codebase.

---

## 📋 All Commands Reference

Use `/help` to see commands organised by category in Telegram.
Use `/help <category>` for details on one category.
Use `/help all` to see every command at once.
Use `/commands` for a compact quick-reference list.

---

### 🤖 AI Assistant

Lovina is an AI with a defined personality — strategic, analytical, cybersecurity-aware, dark academia aesthetic. She does not give generic answers.

| Command | Description |
|---|---|
| `/ai <message>` | Chat with Lovina AI — persistent conversation memory per user |
| `/clear` | Wipe your conversation history and start fresh |
| `/explain <text>` | Paste any security tool output and get an AI analysis |
| `/threat <description>` | Generate a structured threat model for a target or system |
| `/report <findings>` | Turn raw pentest findings into a professional report |
| `/dork <target>` | AI-generated Google dork queries for recon on a target |

**Examples:**
```
/ai What are the most common misconfigurations in AWS S3?
/explain 443/tcp open ssl/https Nginx 1.18.0 Ubuntu
/threat A Node.js REST API with JWT auth deployed on AWS
/report Found open RDP on port 3389, no lockout policy, weak credentials
/dork example.com
```

---

### 🕷️ Web Scraper

Lovina has a full stealth web scraping engine (Hungry Spider) integrated directly. It uses Chrome TLS fingerprint impersonation via `curl-cffi`, which bypasses most bot detection systems including basic Cloudflare checks. Each crawl job is stored in a local SQLite database so results can be exported later.

| Command | Description |
|---|---|
| `/scrape <url>` | Crawl a website and extract structured data with AI |
| `/scrape <url> --schema ecommerce` | Extract product data (name, price, brand, rating, SKU) |
| `/scrape <url> --schema news` | Extract news article data (headline, author, date, topics) |
| `/scrape <url> --schema job` | Extract job posting data (title, company, salary, skills) |
| `/scrape <url> --schema social` | Extract social profile data (name, bio, followers) |
| `/scrape <url> --depth 2` | Follow links up to 2 levels deep (max 3) |
| `/scrape <url> --pages 10` | Crawl up to 10 pages (max 20) |
| `/scrape <url> --dynamic` | Use Playwright for JavaScript-rendered sites |
| `/extract <url>` | Extract structured data from a single page (no link following) |
| `/extract <url> --schema job` | Single-page extraction with a specific schema |
| `/schemas` | List all available extraction schemas with field descriptions |
| `/spiderexport` | Download the last crawl job results as a JSON file |
| `/spiderexport --format csv` | Download as CSV |
| `/spiderexport --format jsonl` | Download as JSONL (one JSON object per line) |
| `/spiderexport --job 3` | Download results from a specific job ID |
| `/spiderexport --format csv --job 3` | Specific job in a specific format |
| `/spiderjobs` | View 10 most recent crawl jobs with status |
| `/spiderstats` | Spider database statistics (total jobs, items, success/fail) |

**Available Schemas:**
- `generic` — title, description, author, date, tags, summary, sentiment, language, emails
- `ecommerce` — product_name, price, currency, brand, rating, review_count, availability, sku
- `news` / `article` — headline, subheadline, author, published_date, outlet, topics, summary
- `job` / `job_posting` — job_title, company, location, remote, salary_range, skills, apply_url
- `social` / `profile` — full_name, username, bio, location, followers, following, company

**Anti-detection features:**
- Chrome TLS/HTTP2 fingerprint impersonation (curl-cffi) — defeats TLS-level bot detection
- Rotating user-agents from real browser pool
- Realistic HTTP headers (Accept, Accept-Language, DNT, Cache-Control)
- Referer chain simulation (starts from Google, passes parent URL to child pages)
- Configurable delays with random jitter
- 429/503 automatic backoff — reads Retry-After header, retries up to 3 times
- Proxy rotation with automatic ban detection

**Examples:**
```
/scrape https://news.ycombinator.com --schema news --pages 5
/scrape https://amazon.com/dp/B09XYZ --schema ecommerce
/extract https://linkedin.com/jobs/view/1234567 --schema job
/spiderexport --format csv --job 1
```

---

### 🕵️ OSINT

All OSINT tools require zero API keys unless noted.

| Command | Description |
|---|---|
| `/ip <IP>` | IP geolocation — country, city, ISP, ASN, timezone |
| `/dns <domain> [type]` | DNS record lookup — A, AAAA, MX, TXT, NS, CNAME |
| `/whois <domain>` | WHOIS registration data — registrar, dates, nameservers |
| `/subdomains <domain>` | Passive subdomain discovery via certificate transparency (crt.sh) |
| `/username <handle>` | Check username across 20 social platforms |
| `/gitosint <username>` | Deep GitHub profile — repos, languages, stars, email, bio |
| `/emailcheck <email>` | Validate email format + MX record check + disposable email detection |
| `/emailguess <first> <last> <domain>` | Generate 12 common email format patterns for a person |
| `/archive <domain>` | Search Wayback Machine archive history for a domain |
| `/paste <keyword>` | Search Pastebin for a keyword (public pastes) |
| `/reverseimg <url>` | Generate reverse image search links (Google, Yandex, TinEye, Bing) |
| `/gdork <target>` | Generate 12 targeted Google dork queries for a domain |

**Examples:**
```
/ip 8.8.8.8
/dns google.com MX
/whois github.com
/subdomains tesla.com
/username lord_noctis
/gitosint torvalds
/emailcheck contact@example.com
/emailguess John Doe example.com
/archive example.com
/gdork example.com
```

---

### 🌐 Network & Recon

| Command | Description |
|---|---|
| `/scan <host> [ports]` | Async TCP port scanner — common 17 ports or custom list |
| `/ssl <domain>` | SSL/TLS certificate analyser — validity, expiry, cipher, SANs |
| `/ping <host>` | ICMP ping with latency and alive/dead status |
| `/traceroute <host>` | Hop-by-hop route trace (max 20 hops) |
| `/banner <host> <port>` | Grab the service banner from an open port |
| `/rdns <IP>` | Reverse DNS lookup — hostname from IP |
| `/asn <IP>` | ASN and organisation lookup |
| `/geoip <IP>` | Full IP geolocation with ISP info |
| `/zonetransfer <domain>` | Attempt DNS zone transfer (AXFR) against all nameservers |
| `/dnsbrute <domain>` | DNS subdomain brute force using a 25-word built-in wordlist |
| `/httpmethods <url>` | Check which HTTP methods the server allows (OPTIONS) |
| `/openredirect <url>` | Test for open redirect vulnerability with common payloads |

**Examples:**
```
/scan example.com 80,443,8080,3306
/ssl github.com
/ping 1.1.1.1
/banner smtp.example.com 25
/zonetransfer zonetransfer.me
/httpmethods https://example.com
```

---

### 🔍 Web Analysis

| Command | Description |
|---|---|
| `/headers <url>` | Security headers audit — grades A to F (checks 7 critical headers) |
| `/cors <url>` | CORS misconfiguration check — tests wildcard and credential exposure |
| `/robots <url>` | Fetch and parse robots.txt — highlights interesting disallowed paths |
| `/sitemap <url>` | Parse sitemap.xml and list all URLs (first 50) |
| `/techstack <url>` | Fingerprint tech stack — CMS, framework, CDN, analytics |
| `/pagemeta <url>` | Extract page title, meta description, OG tags, canonical URL |
| `/links <url>` | Extract all internal and external links from a page |
| `/harvestemail <url>` | Harvest email addresses from a page using regex |
| `/cookies <url>` | Analyse cookies for missing Secure, HttpOnly, SameSite flags |
| `/redirectchain <url>` | Follow redirect chain step by step, showing each hop |
| `/wayback <url>` | Wayback Machine snapshot history for a URL |
| `/forms <url>` | Find all HTML forms, inputs, and flag password/file upload fields |
| `/comments <url>` | Extract all HTML comments — flags TODO, password, key, debug mentions |
| `/jsfiles <url>` | List all external JavaScript files loaded by a page |
| `/cdn <url>` | Detect CDN provider (Cloudflare, Akamai, Fastly, CloudFront) |
| `/waf <url>` | Detect Web Application Firewall by sending common probe payloads |
| `/cms <url>` | CMS detection — WordPress, Drupal, Joomla, Shopify, Wix, Magento, Ghost |

**Examples:**
```
/headers https://example.com
/cors https://api.example.com
/robots https://example.com
/waf https://cloudflare-demo.com
/cms https://wordpress-site.com
/techstack https://nextjs-app.vercel.app
```

---

### 🔐 Cryptography & Encoding

| Command | Description |
|---|---|
| `/hash <text>` | Generate MD5, SHA-1, SHA-256, SHA-512, SHA3-256, BLAKE2b simultaneously |
| `/hashid <hash>` | Identify hash type by length (MD5, SHA-1, SHA-256, etc.) |
| `/encode <format> <text>` | Encode: base64, hex, url, html, rot13 |
| `/decode <format> <text>` | Decode: base64, hex, url, html, rot13 |
| `/extencode <format> <text>` | Extended encode: base32, base85, binary, decimal |
| `/baseconvert <value> <from> <to>` | Convert between any number bases (2, 8, 10, 16, etc.) |
| `/hex2bin <hex>` | Convert hex to binary, decimal, and octal simultaneously |
| `/passgen [length]` | Generate cryptographically secure password with entropy rating |
| `/passcheck <password>` | Check password strength — entropy, score, specific issues |
| `/gentoken [length]` | Generate random hex token, URL-safe token, UUID, and 6-digit PIN |
| `/uuidgen` | Generate a UUID v4 |
| `/uuidinfo <uuid>` | Parse UUID — extract version, variant, timestamp (v1), node |
| `/jwt <token>` | Decode JWT — show algorithm, claims, expiry, and security warnings |

**Examples:**
```
/hash hello world
/hashid 5d41402abc4b2a76b9719d911017c592
/encode base64 Hello, Lord Noctis
/decode hex 48656c6c6f
/baseconvert FF 16 10
/passgen 32
/passcheck MyP@ssword123!
/jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 🔄 Ciphers

| Command | Description |
|---|---|
| `/caesar <text> <shift>` | Caesar cipher encryption |
| `/caesar <text> <shift> decrypt` | Caesar cipher decryption |
| `/rotbrute <text>` | Try all 25 ROT shifts and display every result |
| `/vigenere <text> <key>` | Vigenère cipher encryption |
| `/vigenere <text> <key> decrypt` | Vigenère cipher decryption |
| `/atbash <text>` | Atbash reverse-alphabet substitution cipher |
| `/xorcipher <text> <key>` | XOR cipher — outputs result as hex and base64 |
| `/morse encode <text>` | Text to Morse code |
| `/morse decode <morse>` | Morse code to text (use `/` for word boundaries) |
| `/railfence <text> <rails>` | Rail fence transposition cipher encryption |
| `/railfence <text> <rails> decrypt` | Rail fence transposition cipher decryption |
| `/freqanalysis <text>` | Character frequency analysis — useful for breaking substitution ciphers |

**Examples:**
```
/caesar HELLO 13
/caesar URYYB 13 decrypt
/rotbrute Gur dhvpx oebja sbk
/vigenere HELLO KEY
/morse encode SOS
/morse decode ... --- ...
/railfence HELLOWORLD 3
/freqanalysis Gur dhvpx oebja sbk whzcf bire gur ynml qbt
```

---

### 📊 Text & Data Tools

| Command | Description |
|---|---|
| `/regex <pattern> <text>` | Test a regex pattern — shows all matches, spans, and match count |
| `/textstats <text>` | Count words, characters, sentences, paragraphs, unique words |
| `/diff <text1> \|\|\| <text2>` | Compare two texts — shows similarity %, lines added/removed, diff |
| `/jsonformat <json>` | Validate and pretty-print JSON with type and key info |
| `/json2csv <json>` | Convert JSON array to CSV file — sends as downloadable file |
| `/csv2json <csv>` | Convert CSV data to JSON |
| `/xmlparse <xml>` | Parse and display XML structure as a tree |
| `/timestamp <unix>` | Convert Unix timestamp to UTC, ISO8601, and human-readable date |
| `/epoch` | Get the current Unix timestamp in seconds and milliseconds |
| `/ipcalc <IP/CIDR>` | Subnet calculator — network address, broadcast, host range, usable hosts |
| `/cidr <range>` | Expand CIDR range to full list of IP addresses |
| `/extractip <text>` | Extract all valid IPv4 addresses from any block of text |
| `/mac <address>` | MAC address vendor lookup — identifies manufacturer from OUI prefix |

**Examples:**
```
/regex \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b This IP is 192.168.1.1 and that is 10.0.0.1
/diff Hello world ||| Hello earth
/jsonformat {"name":"Noctis","role":"admin"}
/ipcalc 192.168.1.0/24
/cidr 10.0.0.0/28
/timestamp 1716825600
/mac 00:1A:2B:3C:4D:5E
```

---

### 📁 File & Binary Analysis

All file commands work by replying to an uploaded file in Telegram, except `/hexdump` and `/fileanalyse` which also accept a URL.

| Command | How to use | Description |
|---|---|---|
| `/filetype` | Reply to any file | Detect file type by magic bytes — shows type, size, entropy, hashes, suspicious strings |
| `/hexdump` | Reply to file OR `/hexdump <url>` | Classic hex dump (first 256 bytes shown) |
| `/strings` | Reply to any file | Extract all printable ASCII strings (min 4 chars) from binary |
| `/entropy` | Reply to any file | Calculate Shannon entropy — high entropy suggests encryption or compression |
| `/zipinfo` | Reply to ZIP file | List ZIP contents — file names, sizes, encryption status |
| `/exif` | Reply to photo or image file | Extract EXIF metadata — camera, GPS coordinates, timestamp, device |
| `/fileanalyse <url>` | URL of any file | Download and fully analyse a remote file — type, hashes, entropy, strings, hex dump |

**Examples:**
```
# Upload a file in Telegram, then reply to it with:
/filetype
/strings
/entropy
/exif

# Or analyse by URL:
/fileanalyse https://example.com/suspicious.bin
/hexdump https://example.com/file.exe
```

> **GPS Note:** If an image has GPS EXIF data, `/exif` generates a direct Google Maps link to the coordinates.

---

### 🏁 CTF & Learning Tools

| Command | Description |
|---|---|
| `/jwt <token>` | Decode JWT — algorithm, claims, expiry, security warnings (also in Crypto section) |
| `/magicbytes` | File magic bytes reference table (20+ file types) |
| `/ports` | Full well-known ports reference table (80+ ports) |
| `/ports <number>` | Look up the service for a specific port number |
| `/httpstatus <code>` | Look up any HTTP status code with description and category |
| `/owasp` | OWASP Top 10 2021 — all 10 with descriptions and examples |
| `/owasp <1-10>` | Detailed view of one specific OWASP vulnerability |
| `/revshell <ip> <port>` | Generate bash reverse shell payload with listener command |
| `/revshell <ip> <port> <type>` | Generate reverse shell in specific language |
| `/sqli` | SQL injection payload library — all categories |
| `/sqli <type>` | SQLi payloads for a specific type |
| `/xss` | XSS payload library — all contexts |
| `/xss <context>` | XSS payloads for a specific context |
| `/lfi` | Local File Inclusion payload list |
| `/ssti` | SSTI detection payloads (auto-detect template engine) |
| `/ssti <engine>` | SSTI payloads for a specific template engine |

**Reverse shell types:** `bash`, `python3`, `php`, `netcat`, `netcat_noe`, `powershell`, `perl`, `ruby`, `socat`

**SQLi types:** `union`, `error_based`, `blind_boolean`, `blind_time`, `auth_bypass`

**XSS contexts:** `html_context`, `attribute_context`, `js_context`, `filter_bypass`

**SSTI engines:** `jinja2`, `twig`, `freemarker`, `smarty`, `detection`

**Examples:**
```
/ports 3306
/httpstatus 429
/owasp 3
/revshell 10.10.10.1 4444
/revshell 10.10.10.1 4444 python3
/sqli auth_bypass
/xss filter_bypass
/ssti jinja2
```

> ⚠️ All payloads and shells are for **authorised penetration testing and CTF use only**.

---

### 🛠️ Personal Toolkit

These tools are personal to each user — your data is separate from everyone else's.

#### Key-Value Store — Save anything

| Command | Description |
|---|---|
| `/save <key> <value>` | Save a value under a key |
| `/get <key>` | Retrieve a saved value |
| `/del <key>` | Delete a saved key |
| `/kvlist` | List all your saved keys with previews |

```
/save target_ip 192.168.1.100
/save shodan_key abc123def456
/get target_ip
/kvlist
```

#### Encrypted Notes

Notes are encrypted with Fernet (AES-128-CBC) using a key derived from your user ID.

| Command | Description |
|---|---|
| `/note <id> <content>` | Save an encrypted note |
| `/getnote <id>` | Retrieve and decrypt a note |
| `/notes` | List all your note IDs |
| `/delnote <id>` | Delete a note permanently |

```
/note recon Found admin panel at /wp-admin with default creds
/getnote recon
/notes
```

#### Investigation Timeline

Build a chronological log of events during an investigation.

| Command | Description |
|---|---|
| `/tl add <event>` | Add a timestamped event to your timeline |
| `/tl view` | View all timeline events newest first |
| `/tl clear` | Clear the entire timeline |

```
/tl add Started recon on target.com
/tl add Found subdomain dev.target.com via crt.sh
/tl add Port 3306 open — MySQL running 5.7.32
/tl view
```

#### Engagement Scope Manager

Define your authorised targets and validate every command against them.

| Command | Description |
|---|---|
| `/scope add <target>` | Add a domain/IP to your scope |
| `/scope remove <target>` | Remove a target from scope |
| `/scope list` | List all scoped targets |
| `/scope check <target>` | Check if a target is in your defined scope |

```
/scope add example.com
/scope add 192.168.1.0/24
/scope list
/scope check dev.example.com
```

#### Command History

| Command | Description |
|---|---|
| `/history` | View your 20 most recent commands with timestamps |

#### Alias System

Create short names for long commands you run frequently.

| Command | Description |
|---|---|
| `/alias set <name> <command>` | Create an alias |
| `/alias get <name>` | Look up an alias |
| `/alias list` | List all your aliases |
| `/alias del <name>` | Delete an alias |

```
/alias set myscan /scan 192.168.1.1 22,80,443,3306,5432
/alias get myscan
/alias list
```

---

### 🔬 Research Mode

Research Mode is a passphrase-gated elevated access level for authorised security researchers.

**What it changes:**
- Enhanced AI system prompt with deeper technical context
- No rate limits for any tool
- Full access to all commands

**Activation:**
```
/research
```
The bot will ask you a question. Reply with your `RESEARCH_PASSPHRASE` (set in your `.env` or Railway environment).

The passphrase is stored hashed (SHA-256) — it is never stored in plain text.

| Command | Permission | Description |
|---|---|---|
| `/research` | Sudo+ | Activate research mode (passphrase challenge) |
| `/endresearch` | Any | Deactivate research mode |
| `/research_status` | Any | Check if research mode is currently active |

Research mode state persists across bot restarts (stored in `data/research_states.json`).

---

### ⚙️ Admin Commands

These commands require elevated permissions. See [Permission System](#-permission-system) below.

#### User Management (Lord Noctis only)

| Command | Description |
|---|---|
| `/addsudo <user_id>` | Grant a user sudo-level access |
| `/removesudo <user_id>` | Revoke sudo access |
| `/broadcast <message>` | Send a message to all registered groups |

#### Moderation (Sudo+)

| Command | Description |
|---|---|
| `/ban <user_id>` | Ban a user from using the bot |
| `/unban <user_id>` | Unban a user |
| `/role <user_id> <role>` | Assign a role: `public`, `researcher`, `sudo` |
| `/sudolist` | List all current sudo users |
| `/stats` | View bot usage statistics — top commands, unique users |

#### Groups

| Command | Description |
|---|---|
| `/addgroup` | Register the current group for broadcasts |

---

## 👑 Permission System

Lovina uses a 4-tier access system. Each tier inherits all permissions of the tiers below it.

| Tier | Who | Capabilities |
|---|---|---|
| **Lord Noctis** | Bot owner (set via `LORD_NOCTIS_ID`) | Everything. No limits. Can add/remove sudo users. Can broadcast. Cannot be banned. |
| **Sudo** | Users added via `/addsudo` | All commands. No rate limits. Can ban/unban users and assign roles. Can activate research mode. |
| **Researcher** | Users assigned researcher role | OSINT, network, analysis, scraper tools. Subject to rate limits. |
| **Public** | Everyone else | Basic tools only. Strictest rate limits. |

To make someone a sudo user, send their Telegram user ID to the bot:
```
/addsudo 987654321
```

---

## ⏱️ Rate Limiting

Rate limits apply to all users **except** Lord Noctis and Sudo users. Limits reset on a rolling window.

| Action | Limit | Window |
|---|---|---|
| Default (most commands) | 10 requests | 60 seconds |
| Port scanning (`/scan`) | 3 requests | 120 seconds |
| AI chat (`/ai`) | 20 requests | 1 hour |
| Username hunt (`/username`) | 5 requests | 60 seconds |
| Subdomain discovery (`/subdomains`) | 3 requests | 120 seconds |

Research Mode and Sudo access bypass all rate limits.

---

## 📁 Project Structure

```
Lovina-bot/
│
├── main.py                          # Bot entry point — registers middleware, routers, BotFather commands
├── config.py                        # All settings, paths, API keys, rate limits
├── requirements.txt                 # Python dependencies
├── Procfile                         # Railway: web: python main.py
├── .env.example                     # Template for environment variables
├── .python-version                  # Python 3.11
│
├── data/                            # Persistent JSON storage (gitignored)
│   ├── sudo.json                    # Sudo user list
│   ├── banned.json                  # Banned user list
│   ├── roles.json                   # User role assignments
│   ├── stats.json                   # Command usage statistics
│   ├── groups.json                  # Registered broadcast groups
│   ├── conversations.json           # AI conversation history
│   ├── research_states.json         # Research mode activation states
│   └── spider/                      # Spider SQLite DB + per-user data
│       ├── spider.db                # Crawl jobs and extracted items
│       └── users/                   # Per-user kv store, notes, timeline, scope, aliases
│
├── handlers/                        # Telegram command handlers
│   ├── start.py                     # /start, /about, /status
│   ├── admin.py                     # /ban, /unban, /addsudo, /stats, /broadcast
│   ├── ai_handler.py                # /ai, /explain, /threat, /dork, /report, /clear
│   ├── osint_handlers.py            # /ip, /dns, /whois, /subdomains, /username, /whois
│   ├── analysis_handlers.py         # /hash, /hashid, /encode, /decode, /jwt
│   ├── network_handlers.py          # /scan, /ssl
│   ├── research_mode.py             # /research, /endresearch, /research_status (FSM)
│   ├── scraper_handlers.py          # /scrape, /extract, /spiderexport, /spiderjobs, /spiderstats, /schemas
│   ├── tools_handlers.py            # All 100+ additional tool commands
│   └── help_handler.py              # /help, /commands
│
├── middleware/                      # Request middleware
│   ├── ban_check.py                 # Blocks banned users before any handler runs
│   ├── rate_limit.py                # Enforces per-user rate limits
│   └── stats_tracker.py             # Logs command usage to stats.json
│
├── utils/                           # Shared utilities
│   ├── storage.py                   # JSON file read/write with atomic writes
│   ├── permissions.py               # 4-tier permission system and decorators
│   ├── rate_limiter.py              # Sliding window rate limiter
│   ├── formatter.py                 # Telegram HTML message formatting helpers
│   └── lovina_ai.py                 # Groq AI client — AsyncGroq, conversation history
│
└── tools/                           # Tool implementations
    ├── analysis/                    # Legacy analysis tools
    │   ├── hash_tool.py             # generate_hashes(), hash_identify()
    │   ├── encoder.py               # encode(), decode()
    │   └── jwt_analyzer.py          # analyze_jwt()
    ├── crypto/
    │   └── ciphers.py               # Caesar, Vigenere, Atbash, XOR, Morse, Rail Fence, etc.
    ├── ctf/
    │   └── tools.py                 # OWASP, revshell, SQLi, XSS, LFI, SSTI, magic bytes, ports
    ├── filetools/
    │   └── analysis.py              # File type detection, hex dump, strings, entropy, ZIP, EXIF
    ├── network/
    │   ├── port_scanner.py          # Async TCP port scanner
    │   ├── ssl_analyzer.py          # SSL certificate analyser
    │   └── recon.py                 # ping, traceroute, banner grab, rdns, asn, dns brute, etc.
    ├── osint/
    │   ├── ip_lookup.py             # ip-api.com geolocation
    │   ├── dns_tool.py              # dnspython DNS resolver
    │   ├── subdomain.py             # crt.sh certificate transparency
    │   ├── username_hunt.py         # 20-platform username checker
    │   ├── whois_tool.py            # python-whois wrapper
    │   └── recon.py                 # GitHub OSINT, email check, archive, dorks, CMS detect
    ├── scraper/                     # Hungry Spider — full stealth scraping engine
    │   ├── engine.py                # Orchestrates crawl + extract, SQLite storage
    │   ├── static_crawler.py        # curl-cffi httpx crawler with referer chain + 429 backoff
    │   ├── dynamic_crawler.py       # Playwright crawler for JS-rendered sites
    │   ├── queue_manager.py         # BFS URL queue with deduplication
    │   ├── validators.py            # URL validation and normalisation
    │   ├── exporter.py              # JSON/CSV/JSONL export
    │   ├── ai/
    │   │   ├── schemas.py           # 5 Pydantic extraction schemas
    │   │   └── extractor.py         # Groq-powered AI data extraction
    │   ├── antidetect/
    │   │   ├── proxy_manager.py     # Proxy pool + ban tracking
    │   │   ├── useragent_rotator.py # Real browser UA rotation
    │   │   ├── header_factory.py    # Realistic HTTP header builder
    │   │   └── behaviour.py         # Human delays, mouse simulation, scroll simulation
    │   └── parsers/
    │       ├── html_cleaner.py      # Remove noise tags from HTML
    │       └── text_extractor.py    # Clean text from HTML
    ├── text/
    │   └── analysis.py              # Regex, diff, JSON/CSV/XML tools, IP calc, MAC lookup
    ├── utility/
    │   └── storage.py               # KV store, encrypted notes, timeline, history, scope, alias
    └── web/
        └── analysis.py              # Security headers, CORS, robots, sitemap, WAF, CDN, etc.
```

---

## 🔒 Security Notes

### Credentials
- Never hardcode API keys or the bot token anywhere in the codebase
- Set all credentials as Railway environment variables or in a local `.env` file that is gitignored
- If credentials were ever committed, rotate them immediately (BotFather revoke + Groq delete)

### Research Mode
- The `RESEARCH_PASSPHRASE` is never stored in plain text — it is compared as a SHA-256 hash
- Do not share the passphrase or put it in the README, comments, or any code file
- Only Sudo users and Lord Noctis can initiate the passphrase challenge

### User Data
- All user-specific data (notes, KV store, timeline, scope) is stored in `data/spider/users/<user_id>/`
- Notes are encrypted with Fernet (AES-128-CBC) using a key derived from the user ID
- The `data/` directory is gitignored and should never be committed

### Bot Security
- The 4-tier permission system ensures public users cannot access sensitive tools
- The BanCheckMiddleware runs before any handler — banned users are silently dropped
- RateLimitMiddleware prevents spam and abuse from public-level users
- Input validation is applied in all tool handlers before passing to tool functions

---

## ⚠️ Disclaimer

Lovina Bot is an academic cybersecurity research assistant built for **authorised security research and educational purposes only**.

- All tools must be used only on systems you own or have explicit written permission to test
- Unauthorised access to computer systems is illegal in most jurisdictions
- The creator (Lord Noctis) is not responsible for any misuse of this tool
- Payload libraries (SQLi, XSS, LFI, SSTI, reverse shells) are provided for CTF and authorised pentest contexts only
- The web scraper must only be used on websites you are authorised to scrape

**Use ethically. Stay legal. Hack responsibly.**

---

<div align="center">

**Made with 🌙 for security researchers and ethical hackers**

*v2.0.0 — 140+ commands · Groq LLaMA 3.3-70B · Hungry Spider Integration*

</div>
