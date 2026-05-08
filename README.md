# Lovina Bot - AI-Powered Cybersecurity Research Assistant

**Lovina** is a production-ready Telegram bot designed as an academic cybersecurity research assistant. It combines OSINT tools, security analysis, and AI-powered insights via Groq API.

## ✨ Features

### 🔍 OSINT Tools (No API Keys Required)
- **IP Lookup** - Geolocation, ASN, ISP data
- **DNS Records** - All record types (A, AAAA, MX, NS, TXT, etc.)
- **Subdomain Discovery** - Passive discovery via certificate transparency
- **Username Search** - Check 27+ social platforms
- **SSL Analysis** - Certificate validity, expiration, cipher suites

### 🌐 Network Tools
- **Port Scanner** - Async TCP scanner with service identification
- **SSL/TLS** - Deep certificate analysis
- **Technology Fingerprinting** - Detect web technologies
- **Security Headers** - HTTP header audit

### 🔬 Analysis Tools
- **Hash Generation** - MD5, SHA1-512, BLAKE2b, SHA3-256
- **Hash Identification** - Identify hash types by length
- **Encoding/Decoding** - Base64, Hex, URL, HTML, ROT13
- **JWT Analyzer** - Decode and analyze JWT tokens
- **CVE Lookup** - Vulnerability database search

### 🧠 AI Integration
- **Lovina AI** - Strategic, analytical AI assistant (Groq LLama 3.1)
- **Threat Modeling** - Generate structured threat models
- **Google Dorking** - Generate reconnaissance queries
- **Report Generation** - Synthesize findings into reports

### 👑 Admin Features
- **4-Tier Permission System** - Lord Noctis → Sudo → Researcher → Public
- **Research Mode** - Passphrase-protected advanced access
- **Rate Limiting** - Per-user, per-action rate limits
- **Group Monitoring** - Daily updates to monitored groups
- **User Management** - Ban/unban, role assignment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token
- Groq API Key (free)
- GitHub account (for Railway deployment)

### Local Development

```bash
# 1. Clone repository
cd lovina_bot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your credentials
nano .env

# 5. Run bot
python main.py
```

### Railway Deployment

1. **Connect GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial Lovina bot commit"
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub account
   - Select this repository
   - Railway auto-detects Procfile
   - Add environment variables in Railway dashboard:
     - `BOT_TOKEN`
     - `LORD_NOCTIS_ID`
     - `GROQ_API_KEY`

3. **Bot runs 24/7** on Railway's free tier

## 📋 Available Commands

### OSINT Tools
```
/ip <address>              - IP geolocation lookup
/dns <domain> [type]       - DNS record lookup
/whois <domain|ip>         - WHOIS information
/ssl <domain>              - SSL certificate analysis
/subdomains <domain>       - Passive subdomain discovery
/username <username>       - Search 27+ platforms
```

### Network Analysis
```
/scan <host> [ports]       - TCP port scanner
/tech <url>                - Web technology fingerprinting
/headers <url>             - HTTP security header audit
```

### Analysis Tools
```
/hash <text>               - Generate all hash types
/hashid <hash>             - Identify hash type
/encode <format> <text>    - Encode text (base64, hex, url, html, rot13)
/decode <format> <text>    - Decode text
/jwt <token>               - Analyze JWT token
/cve <CVE-ID>              - CVE vulnerability lookup
```

### AI Tools
```
/ai <question>             - Chat with Lovina AI
/explain <text>            - Explain security output
/threat <description>      - Generate threat model
/dork <topic>              - Generate Google dork queries
/report                    - Synthesize findings into report
/clear                     - Clear conversation memory
```

### Admin Commands (Sudo+)
```
/addsudo <user_id>         - Add sudo user (Lord Noctis only)
/removesudo <user_id>      - Remove sudo user (Lord Noctis only)
/sudolist                  - List all sudo users
/ban <user_id>             - Ban user
/unban <user_id>           - Unban user
/role <user_id> <role>     - Assign researcher role
/stats                     - Bot statistics
/broadcast <message>       - Send message to monitored groups (Lord Noctis only)
```

### Research Mode
```
/research                  - Activate research mode (passphrase required)
/endresearch               - Deactivate research mode
/research_status           - Check research mode status
```

## 🔐 Research Mode

**Passphrase:** `knowledge`

Activates advanced features:
- No rate limiting for operators
- Enhanced AI analysis
- Full tool access
- Sudo+ users only

## 🗂️ Project Structure

```
lovina_bot/
├── main.py                 - Bot entry point
├── config.py               - Configuration & settings
├── requirements.txt        - Python dependencies
├── .env                    - Credentials (keep secret!)
├── .env.example            - Template
├── Procfile                - Railway deployment
│
├── data/                   - JSON storage (persistent)
│   ├── sudo.json
│   ├── banned.json
│   ├── roles.json
│   ├── stats.json
│   └── research_states.json
│
├── utils/
│   ├── storage.py          - JSON file handling
│   ├── permissions.py      - 4-tier permission system
│   ├── rate_limiter.py     - Sliding window rate limiter
│   ├── formatter.py        - Telegram message formatting
│   └── lovina_ai.py        - Groq AI integration
│
├── middleware/
│   ├── ban_check.py        - Ban enforcement
│   ├── rate_limit.py       - Rate limit enforcement
│   └── stats_tracker.py    - Usage statistics
│
├── tools/
│   ├── osint/              - OSINT tools
│   ├── network/            - Network analysis tools
│   ├── analysis/           - Data analysis tools
│   └── crypto/             - Encryption tools
│
└── handlers/
    ├── start.py            - /start, /help, /about
    ├── admin.py            - Admin commands
    ├── ai_handler.py       - AI commands
    ├── osint_handlers.py   - OSINT handlers
    ├── analysis_handlers.py- Analysis handlers
    ├── network_handlers.py - Network handlers
    └── research_mode.py    - Research mode handler
```

## 🔧 Configuration

Edit `config.py` to customize:
- Bot name and creator
- Rate limit thresholds
- Research mode passphrase
- API keys (optional)

## 🛡️ Security & OPSEC

### ✅ Best Practices
- All credentials in `.env` (never commit)
- User IDs stored as integers
- Rate limiting prevents abuse
- Ban system for malicious users
- Research mode for sensitive features
- Input sanitization on all tools

### ⚠️ Disclaimer
For **authorized security research and educational purposes only**. All tools should be used ethically and legally. Unauthorized access is illegal.

## 📊 Permissions System

| Level | Access |
|-------|--------|
| **Lord Noctis** | Everything, no limits |
| **Sudo** | All commands, no rate limits |
| **Researcher** | OSINT, network, analysis tools |
| **Public** | Basic tools only |

## 🚧 Future Enhancements

- [ ] Backend server for advanced tools (Nmap, Metasploit, Hashcat)
- [ ] Database integration (PostgreSQL)
- [ ] Webhook support for real-time scanning
- [ ] Multi-language support
- [ ] Web dashboard
- [ ] Advanced reporting

## 📝 License

Academic Project - Use responsibly.

## 👨‍💻 Creator

**Lord Noctis** - Cybersecurity Research & Development

---

**Made with ❤️ for security researchers and ethical hackers**
