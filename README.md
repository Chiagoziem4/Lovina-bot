# 🤖 Lovina Bot 

Lovina is a Telegram bot built for security researchers, students, and pentesting teams who want fast, on-the-go access to common recon and vulnerability-assessment tools — all from a chat interface.
---

## What This Update Adds

| Feature | Description |
|---|---|
| 6 AI providers | Groq, OpenAI, Anthropic, Google Gemini, Mistral, Ollama |
| Runtime switching | Change providers from Telegram with `/setprovider` |
| Status command | Check what's configured with `/provider` |
| Persistent history | Conversation memory survives bot restarts |
| Graceful fallback | Clear error messages if a key is missing |

---

## Files in This Package

```
lovina-ai-providers/
├── utils/
│   ├── ai_providers.py          ← NEW — provider abstraction layer
│   └── lovina_ai.py             ← REPLACE existing file
├── handlers/
│   └── setprovider_handler.py   ← NEW — /setprovider and /provider commands
├── env_additions.txt            ← Lines to add to .env.example
├── requirements_additions.txt   ← Optional packages to add to requirements.txt
├── README.md                    ← This file
└── MANUS_PROMPT.md              ← Prompt for Manus to implement everything
```

---

## Supported Providers

| Provider | Speed | Cost | Best For | Free? |
|---|---|---|---|---|
| **Groq** | ⚡ Fastest | Free | Default — fast responses | ✅ Yes |
| **OpenAI GPT-4o-mini** | Fast | ~$0.15/1M tokens | Best reasoning quality | ❌ No |
| **Anthropic Claude Haiku** | Fast | ~$0.25/1M tokens | Long context, careful answers | ❌ No |
| **Google Gemini Flash** | Very fast | Free tier generous | Multimodal, image understanding | ✅ Yes |
| **Mistral Medium** | Fast | ~$2.70/1M tokens | European data compliance | ❌ No |
| **Ollama (local)** | Hardware-dependent | Free forever | Privacy, no internet needed | ✅ Free |

---

## Setup Guide

### Step 1 — Get your API keys

You only need keys for the providers you want to use. Groq is the default and already works.

**Groq (already set up)**
- Already in your `.env` as `GROQ_API_KEY`
- Get a free key at https://console.groq.com

**OpenAI (optional)**
1. Go to https://platform.openai.com/api-keys
2. Click `Create new secret key`
3. Copy the key starting with `sk-...`

**Anthropic Claude (optional)**
1. Go to https://console.anthropic.com
2. Click `API Keys` → `Create Key`
3. Copy the key starting with `sk-ant-...`

**Google Gemini (optional)**
1. Go to https://aistudio.google.com/app/apikey
2. Click `Create API Key`
3. Copy the key starting with `AIza...`

**Mistral (optional)**
1. Go to https://console.mistral.ai
2. Click `API Keys` → `Create new key`
3. Copy the key

**Ollama (optional — runs locally, no key needed)**
1. Download from https://ollama.com
2. Install and run: `ollama serve`
3. Pull a model: `ollama pull llama3`
4. Set `OLLAMA_BASE_URL=http://your-laptop-ip:11434` in env vars
5. Note: Ollama only works if your bot is running locally, not on Railway

---

### Step 2 — Add environment variables

#### On Railway (production)

1. Go to your Railway project dashboard
2. Click your service → **Variables** tab
3. Add the variables you need:

```
AI_PROVIDER = groq
```

Then optionally add any of these (only add the ones you have keys for):

```
OPENAI_API_KEY     = sk-...
OPENAI_MODEL       = gpt-4o-mini

ANTHROPIC_API_KEY  = sk-ant-...
ANTHROPIC_MODEL    = claude-3-haiku-20240307

GEMINI_API_KEY     = AIza...
GEMINI_MODEL       = gemini-1.5-flash

MISTRAL_API_KEY    = your_mistral_key
MISTRAL_MODEL      = mistral-medium

OLLAMA_BASE_URL    = http://localhost:11434
OLLAMA_MODEL       = llama3
```

Railway auto-redeploys when you save environment variables — no manual trigger needed.

#### On your laptop (local development)

Open your `.env` file and add the same variables:

```bash
AI_PROVIDER=groq
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
```

---

### Step 3 — Install optional packages

Only install packages for providers you actually use.

```bash
# Activate your virtual environment first
source venv/bin/activate   # Linux/macOS
# OR
venv\Scripts\activate      # Windows

# Install only what you need
pip install openai              # For OpenAI
pip install anthropic           # For Anthropic Claude
pip install google-generativeai # For Google Gemini
# Groq, Mistral, and Ollama use httpx which is already installed
```

---

### Step 4 — Verify the update works

After Manus applies the changes and Railway redeploys:

1. Open Telegram and send `/provider` to your bot
2. You should see a list of all providers with their status (✅ Ready or ❌ No key)
3. The currently active provider is shown at the top

---

## Using the New Commands

### `/provider` — Check current provider
Available to all users. Shows which provider is active and what is configured.

```
🤖 AI Provider Status

Active: Groq (llama-3.3-70b-versatile)

All providers:
  ⚡ groq — Groq — LLaMA 3.3-70B
      ✅ Ready | Free
  🟢 openai — OpenAI — GPT-4o-mini
      ❌ No key set | Paid ~$0.15/1M tokens
  🟤 anthropic — Anthropic — Claude 3 Haiku
      ❌ No key set | Paid ~$0.25/1M tokens
  🔵 gemini — Google — Gemini 1.5 Flash
      ✅ Ready | Free tier generous
  🟡 mistral — Mistral — Mistral Medium
      ❌ No key set | Paid ~$2.70/1M tokens
  🖥️ ollama — Ollama — Local LLM
      ✅ Ready (always) | Free (runs on device)
```

---

### `/setprovider <name>` — Switch provider instantly
**Lord Noctis only.** Switches immediately with no redeploy needed.

```
/setprovider groq
/setprovider openai
/setprovider anthropic
/setprovider gemini
/setprovider mistral
/setprovider ollama
```

**Important:** The switch is instant but resets on bot restart. To make it permanent, change `AI_PROVIDER` in your Railway environment variables.

---

### `/setprovider` (no argument) — Show available options
Shows what is configured and what needs a key, with usage instructions.

---

## Switching Providers — Decision Guide

**Use Groq when:**
- You want the fastest responses
- You are on a budget (free tier)
- Lovina's personality is the priority

**Use OpenAI when:**
- You need the best reasoning quality
- You are working on complex security analysis
- You can afford ~$5-10/month in API costs

**Use Anthropic when:**
- You want careful, nuanced answers
- You are working with very long documents or conversations
- You need Claude's specific tone

**Use Gemini when:**
- You want a second free option
- You plan to add image analysis features later
- Groq is down or rate-limited

**Use Mistral when:**
- Your data must stay in EU jurisdiction
- You need French/European language support

**Use Ollama when:**
- Running the bot locally (not on Railway)
- You need complete privacy (no data leaves your machine)
- You want to experiment with different open-source models

---

## Troubleshooting

**"OPENAI_API_KEY not set" error**
→ Add the key to Railway environment variables and wait for auto-redeploy

**"Error switching provider" after setting key**
→ Make sure you spelled the key variable name correctly (uppercase, with underscore)
→ Make sure you saved the variable in Railway and the service redeployed

**Ollama not working on Railway**
→ Ollama runs locally — it cannot run on Railway's servers
→ Ollama only works when running the bot on your own laptop
→ Set OLLAMA_BASE_URL to your laptop's local IP: http://192.168.x.x:11434

**Responses are suddenly worse after switching**
→ Use /setprovider groq to switch back to the default
→ Different providers have different capabilities — Groq with LLaMA 3.3-70B is generally best for Lovina's personality

**Provider switched but /ai still uses old provider**
→ The switch is applied to the singleton immediately — all new /ai messages use the new provider
→ Old conversations in memory are not affected

---

## How It Works Technically

All 6 providers implement the same `BaseProvider` interface with a single `chat(messages, max_tokens, temperature)` method. The `LovinaAI` class calls `self.provider.chat()` without knowing or caring which provider is underneath. Switching providers just swaps the `self.provider` object on the singleton — no restart needed.

```
/ai message
    ↓
lovina_ai.chat(user_id, message)
    ↓
self.provider.chat(messages)  ← this is swappable
    ↓
GroqProvider / OpenAIProvider / AnthropicProvider / ...
    ↓
API call to the selected service
    ↓
response back to Telegram
```

---

## 📋 Complete Command Reference

Lovina Bot provides **142 commands** across 13 categories. Use `/help` for interactive help, `/help <category>` for a category overview, or `/help all` for the full reference.

### 🤖 AI ASSISTANT

| Command | Description |
|---------|-------------|
| `/ai <message>` | Chat with Lovina AI |
| `/clear` | Clear your conversation history |
| `/explain <text>` | AI explains any text or tool output |
| `/threat <description>` | AI threat model for a target |
| `/report <findings>` | Generate a pentest report |
| `/dork <target>` | AI-generated Google dork queries |

### 🕷️ WEB SCRAPER

| Command | Description |
|---------|-------------|
| `/scrape <url>` | Crawl and extract structured data |
| `/scrape <url> --schema ecommerce` | Extract product data |
| `/scrape <url> --depth 2 --pages 10` | Multi-page crawl |
| `/scrape <url> --dynamic` | Playwright for JS-heavy sites |
| `/extract <url>` | Single-page AI extraction only |
| `/extract <url> --schema job` | Job posting extraction |
| `/schemas` | List all extraction schemas |
| `/spiderexport` | Download last crawl as JSON file |
| `/spiderexport --format csv --job 3` | Export specific job as CSV |
| `/spiderjobs` | View recent crawl job history |
| `/spiderstats` | Spider database statistics |

### 🌐 NETWORK & RECON

| Command | Description |
|---------|-------------|
| `/portscan <host>` | Scan common TCP ports |
| `/ping <host>` | ICMP ping with latency |
| `/traceroute <host>` | Hop-by-hop route trace |
| `/banner <host> <port>` | Grab service banner |
| `/rdns <ip>` | Reverse DNS lookup |
| `/asn <ip>` | ASN and organisation lookup |
| `/geoip <ip>` | IP geolocation with ISP info |
| `/dns <domain>` | DNS record lookup (A/MX/TXT/NS) |
| `/zonetransfer <domain>` | Attempt DNS zone transfer |
| `/dnsbrute <domain>` | DNS subdomain brute force |
| `/whois <domain>` | WHOIS registration data |
| `/ssl <domain>` | SSL certificate analyser |
| `/subdomain <domain>` | Passive subdomain discovery |
| `/httpmethods <url>` | Check allowed HTTP methods |
| `/openredirect <url>` | Test for open redirect vulnerability |

### 🔍 WEB ANALYSIS

| Command | Description |
|---------|-------------|
| `/headers <url>` | Security headers grade A-F |
| `/cors <url>` | CORS misconfiguration check |
| `/robots <url>` | Fetch and analyse robots.txt |
| `/sitemap <url>` | Parse sitemap.xml |
| `/techstack <url>` | Fingerprint tech stack |
| `/pagemeta <url>` | Extract page title and meta tags |
| `/links <url>` | Extract all internal and external links |
| `/harvestemail <url>` | Harvest email addresses from page |
| `/cookies <url>` | Analyse cookies for security flags |
| `/redirectchain <url>` | Follow and map redirect chain |
| `/wayback <url>` | Wayback Machine history lookup |
| `/forms <url>` | Find all forms and inputs |
| `/comments <url>` | Extract HTML comments |
| `/jsfiles <url>` | List all JavaScript files |
| `/cdn <url>` | Detect CDN provider |
| `/waf <url>` | Detect Web Application Firewall |
| `/cms <url>` | CMS detection (WP/Drupal/Shopify etc) |

### 🕵️ OSINT

| Command | Description |
|---------|-------------|
| `/ip <ip>` | IP geolocation lookup |
| `/username <handle>` | Username hunt across 20 platforms |
| `/gitosint <username>` | Deep GitHub profile OSINT |
| `/emailcheck <email>` | Email validation + MX + disposable check |
| `/emailguess <first> <last> <domain>` | Generate email pattern guesses |
| `/archive <domain>` | Wayback Machine archive search |
| `/paste <keyword>` | Search Pastebin for keyword |
| `/reverseimg <url>` | Generate reverse image search links |
| `/gdork <target>` | Generate Google dorks for a target |

### 🔐 CRYPTOGRAPHY & ENCODING

| Command | Description |
|---------|-------------|
| `/hash <text>` | Generate MD5/SHA1/SHA256/SHA512 |
| `/identify <hash>` | Identify hash type by length |
| `/encode <format> <text>` | Encode base64/hex/url/html/rot13 |
| `/decode <format> <text>` | Decode base64/hex/url/html/rot13 |
| `/extencode <format> <text>` | Extended encode base32/base58/base85/binary |
| `/baseconvert <val> <from> <to>` | Convert between number bases |
| `/hex2bin <hex>` | Hex to binary/decimal/octal |
| `/passgen [length]` | Generate secure password with entropy |
| `/passcheck <password>` | Check password strength |
| `/gentoken [length]` | Generate random token and UUID |
| `/uuidgen` | Generate UUID v4 |
| `/uuidinfo <uuid>` | Parse and analyse a UUID |

### 🔄 CIPHERS

| Command | Description |
|---------|-------------|
| `/caesar <text> <shift> [decrypt]` | Caesar cipher encrypt/decrypt |
| `/rotbrute <text>` | Brute force all 25 ROT shifts |
| `/vigenere <text> <key> [decrypt]` | Vigenere cipher encrypt/decrypt |
| `/atbash <text>` | Atbash reverse alphabet cipher |
| `/xorcipher <text> <key>` | XOR cipher outputs hex and base64 |
| `/morse encode <text>` | Text to Morse code |
| `/morse decode <morse>` | Morse code to text |
| `/railfence <text> <rails> [decrypt]` | Rail fence transposition cipher |
| `/freqanalysis <text>` | Character frequency analysis |

### 📊 TEXT & DATA TOOLS

| Command | Description |
|---------|-------------|
| `/regex <pattern> <text>` | Test regex pattern against text |
| `/textstats <text>` | Word/char/sentence count and stats |
| `/diff <text1> \|\|\| <text2>` | Compare two texts with separator \|\|\| |
| `/jsonformat <json>` | Pretty-print and validate JSON |
| `/json2csv <json>` | Convert JSON array to CSV file |
| `/csv2json <csv>` | Convert CSV data to JSON |
| `/xmlparse <xml>` | Parse and display XML structure |
| `/timestamp <unix>` | Convert Unix timestamp to readable date |
| `/epoch` | Get current Unix timestamp |
| `/ipcalc <ip/cidr>` | Subnet calculator network/broadcast/hosts |
| `/cidr <range>` | Expand CIDR range to list of IPs |
| `/extractip <text>` | Extract all IP addresses from text |
| `/mac <address>` | MAC address vendor lookup |

### 📁 FILE & BINARY ANALYSIS

| Command | Description |
|---------|-------------|
| `/filetype` | Detect file type by magic bytes (reply to file) |
| `/hexdump <url>` | Hex dump a file (reply to file or URL) |
| `/strings` | Extract printable strings (reply to file) |
| `/entropy` | Calculate Shannon entropy (reply to file) |
| `/zipinfo` | Inspect ZIP contents (reply to ZIP file) |
| `/exif` | Extract EXIF metadata (reply to image) |
| `/fileanalyse <url>` | Download and fully analyse any file URL |

### 🏁 CTF & LEARNING TOOLS

| Command | Description |
|---------|-------------|
| `/jwt` | Decode and analyse JWT token |
| `/magicbytes` | File signature reference table |
| `/ports [number]` | Port service reference or single lookup |
| `/httpstatus <code>` | HTTP status code lookup |
| `/owasp [1-10]` | OWASP Top 10 reference |
| `/revshell <ip> <port> [type]` | Generate reverse shell payload |
| `/sqli [type]` | SQL injection payload library |
| `/xss [context]` | XSS payload library by context |
| `/lfi` | Local file inclusion payload list |
| `/ssti [engine]` | SSTI payloads by template engine |

### 🛠️ PERSONAL TOOLKIT

| Command | Description |
|---------|-------------|
| `/save <key> <value>` | Save a value to your personal store |
| `/get <key>` | Retrieve a saved value |
| `/del <key>` | Delete a saved key |
| `/kvlist` | List all your saved keys |
| `/note <id> <content>` | Save an encrypted note |
| `/getnote <id>` | Retrieve an encrypted note |
| `/notes` | List all your notes |
| `/delnote <id>` | Delete a note |
| `/tl add <event>` | Add event to investigation timeline |
| `/tl view` | View your investigation timeline |
| `/tl clear` | Clear the timeline |
| `/history` | View your recent command history |
| `/scope add <target>` | Add target to engagement scope |
| `/scope remove <target>` | Remove target from scope |
| `/scope list` | List all scoped targets |
| `/scope check <target>` | Check if target is in scope |
| `/alias set <name> <cmd>` | Create a command alias |
| `/alias get <name>` | Get an alias command |
| `/alias list` | List all aliases |
| `/alias del <name>` | Delete an alias |

### ⚙️ ADMIN (Admins only)

| Command | Description |
|---------|-------------|
| `/ban <user_id>` | Ban a user from the bot |
| `/unban <user_id>` | Unban a user |
| `/promote <user_id>` | Promote user to sudo |
| `/demote <user_id>` | Demote sudo to regular user |
| `/broadcast <message>` | Broadcast message to all groups |
| `/stats` | Bot usage statistics |
| `/status` | Bot uptime and activity summary |
| `/addgroup` | Register group for broadcasts |
| `/provider` | Show current AI provider and what is configured |
| `/setprovider <name>` | Switch AI provider instantly (Lord Noctis only) |

### 🔬 RESEARCH MODE

| Command | Description |
|---------|-------------|
| `/research` | Activate research mode (passphrase required) |
| `/endresearch` | Deactivate research mode |
| `/research_status` | Check if research mode is active |

---

## Adding a New Provider in the Future

If you want to add a new provider (e.g. Cohere, Together AI, Perplexity):

1. Open `utils/ai_providers.py`
2. Add a new class that subclasses `BaseProvider`
3. Implement `name` property and `chat()` method
4. Add a case to `build_provider()` function
5. Add an entry to `PROVIDER_INFO` in `handlers/setprovider_handler.py`
6. Add the API key env var to `config.py` and `.env.example`


