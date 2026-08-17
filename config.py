"""
Lovina Bot Configuration
All environment variables and settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

import time
BOT_START_TIME = time.time()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TELEGRAM BOT SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "Lovina"
CREATOR = "Lord Noctis"

# User IDs
LORD_NOCTIS_ID_STR = os.getenv("LORD_NOCTIS_ID")
LORD_NOCTIS_ID = int(LORD_NOCTIS_ID_STR) if LORD_NOCTIS_ID_STR else None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AI SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── AI Provider Selection ─────────────────────────────────────────────────────
# Set to one of: groq, openai, anthropic, gemini, mistral, ollama
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Anthropic Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium")

# Ollama (local — no API key needed)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RATE LIMITING (per action, outside sudo)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RATE_LIMITS = {
    "default": (10, 60),          # 10 requests per 60 seconds
    "portscan": (3, 120),         # 3 requests per 120 seconds
    "ai": (20, 3600),             # 20 requests per 3600 seconds
    "username": (5, 60),          # 5 requests per 60 seconds
    "subdomain": (3, 120),        # 3 requests per 120 seconds
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PATHS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Data file paths
SUDO_FILE = os.path.join(DATA_DIR, "sudo.json")
BANNED_FILE = os.path.join(DATA_DIR, "banned.json")
ROLES_FILE = os.path.join(DATA_DIR, "roles.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
RESEARCH_STATES_FILE = os.path.join(DATA_DIR, "research_states.json")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
CONVERSATIONS_FILE = os.path.join(DATA_DIR, "conversations.json")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WEB SCRAPING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# User agents for web scraping (rotation to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
]

# HTTP Timeout
HTTP_TIMEOUT = 10.0
SCRAPE_TIMEOUT = 15.0

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OPTIONAL API KEYS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
HIBP_API_KEY = os.getenv("HIBP_API_KEY", "")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESEARCH MODE PASSPHRASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESEARCH_PASSPHRASE = os.getenv("RESEARCH_PASSPHRASE")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BOT VERSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOT_VERSION = "1.0.0"


def validate_config():
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not LORD_NOCTIS_ID:
        missing.append("LORD_NOCTIS_ID")
    if not RESEARCH_PASSPHRASE:
        missing.append("RESEARCH_PASSPHRASE")

    provider_keys = {
        "groq": ("GROQ_API_KEY", GROQ_API_KEY),
        "openai": ("OPENAI_API_KEY", OPENAI_API_KEY),
        "anthropic": ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
        "gemini": ("GEMINI_API_KEY", GEMINI_API_KEY),
        "mistral": ("MISTRAL_API_KEY", MISTRAL_API_KEY),
    }
    provider = AI_PROVIDER.lower().strip()
    if provider not in {"groq", "openai", "anthropic", "gemini", "mistral", "ollama"}:
        missing.append(f"AI_PROVIDER (unsupported: {AI_PROVIDER})")
    elif provider in provider_keys and not provider_keys[provider][1]:
        missing.append(provider_keys[provider][0])

    if missing:
        raise EnvironmentError(f"Missing or invalid configuration: {', '.join(missing)}")
