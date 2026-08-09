# 🤖 Lovina Bot — Multi-Provider AI Update

This package upgrades Lovina Bot from being locked to Groq only, to supporting **6 different AI providers** that can be switched instantly without redeploying.

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

## Adding a New Provider in the Future

If you want to add a new provider (e.g. Cohere, Together AI, Perplexity):

1. Open `utils/ai_providers.py`
2. Add a new class that subclasses `BaseProvider`
3. Implement `name` property and `chat()` method
4. Add a case to `build_provider()` function
5. Add an entry to `PROVIDER_INFO` in `handlers/setprovider_handler.py`
6. Add the API key env var to `config.py` and `.env.example`

The whole system is designed to make this a 15-minute task.
