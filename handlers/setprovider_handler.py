"""
handlers/setprovider_handler.py
/setprovider — Switch AI provider at runtime (Lord Noctis only)
/provider    — Show current provider and what is configured (all users)
"""
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from utils.permissions import require_not_banned

router = Router()

VALID_PROVIDERS = ["groq", "openai", "anthropic", "gemini", "mistral", "ollama"]

PROVIDER_INFO = {
    "groq":      {"icon": "⚡", "desc": "Groq — LLaMA 3.3-70B",        "cost": "Free",                   "key_var": "GROQ_API_KEY",      "url": "https://console.groq.com"},
    "openai":    {"icon": "🟢", "desc": "OpenAI — GPT-4o-mini",         "cost": "Paid ~$0.15/1M tokens",  "key_var": "OPENAI_API_KEY",    "url": "https://platform.openai.com/api-keys"},
    "anthropic": {"icon": "🟤", "desc": "Anthropic — Claude 3 Haiku",   "cost": "Paid ~$0.25/1M tokens",  "key_var": "ANTHROPIC_API_KEY", "url": "https://console.anthropic.com"},
    "gemini":    {"icon": "🔵", "desc": "Google — Gemini 1.5 Flash",    "cost": "Free tier generous",     "key_var": "GEMINI_API_KEY",    "url": "https://aistudio.google.com/app/apikey"},
    "mistral":   {"icon": "🟡", "desc": "Mistral — Mistral Medium",     "cost": "Paid ~$2.70/1M tokens",  "key_var": "MISTRAL_API_KEY",   "url": "https://console.mistral.ai"},
    "ollama":    {"icon": "🖥️", "desc": "Ollama — Local LLM",           "cost": "Free (runs on device)",  "key_var": "None required",     "url": "https://ollama.com"},
}

def _is_lord_noctis(user_id: int) -> bool:
    from config import LORD_NOCTIS_ID
    return user_id == LORD_NOCTIS_ID


@router.message(Command("provider"))
@require_not_banned
async def provider_status_command(message: Message):
    import utils.lovina_ai as lai
    from utils.ai_providers import list_available_providers
    current = lai.lovina_ai.provider.name
    available = list_available_providers()
    lines = [f"<b>🤖 AI Provider Status</b>\n\n<b>Active:</b> {current}\n\n<b>All providers:</b>"]
    for key, info in PROVIDER_INFO.items():
        status = "✅ Ready" if available.get(key) else "❌ No key set"
        lines.append(f"  {info['icon']} <b>{key}</b> — {info['desc']}\n      {status} | {info['cost']}")
    lines.append("\n<i>Use /setprovider &lt;name&gt; to switch (Lord Noctis only)</i>")
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("setprovider"))
@require_not_banned
async def setprovider_command(message: Message):
    if not _is_lord_noctis(message.from_user.id):
        await message.answer("❌ Only Lord Noctis can switch AI providers.", parse_mode="HTML")
        return

    import utils.lovina_ai as lai
    from utils.ai_providers import build_provider, list_available_providers

    args = message.text.split()

    if len(args) < 2:
        available = list_available_providers()
        current = lai.lovina_ai.provider.name
        lines = [f"<b>🔄 Switch AI Provider</b>\n\n<b>Current:</b> {current}\n\n<b>Usage:</b> <code>/setprovider &lt;name&gt;</code>\n"]
        for key, info in PROVIDER_INFO.items():
            status = "✅" if available.get(key) else "⚠️ needs key"
            lines.append(f"  {info['icon']} <code>/setprovider {key}</code> — {info['desc']} [{status}]")
        lines.append("\n<i>Changes are instant but revert on restart.\nSet AI_PROVIDER env var for permanent change.</i>")
        await message.answer("\n".join(lines), parse_mode="HTML")
        return

    provider_name = args[1].lower().strip()
    if provider_name not in VALID_PROVIDERS:
        await message.answer(f"❌ Unknown provider: <code>{provider_name}</code>\nValid: {', '.join(VALID_PROVIDERS)}", parse_mode="HTML")
        return

    try:
        new_provider = build_provider(provider_name)
        old_name = lai.lovina_ai.provider.name
        lai.lovina_ai.provider = new_provider
        info = PROVIDER_INFO[provider_name]
        await message.answer(
            f"✅ <b>Provider Switched</b>\n\n"
            f"<b>Before:</b> {old_name}\n"
            f"<b>Now:</b> {new_provider.name}\n\n"
            f"{info['icon']} {info['desc']}\n"
            f"Cost: {info['cost']}\n\n"
            f"<i>All /ai calls now use {provider_name}.\n"
            f"To make permanent: set AI_PROVIDER={provider_name} in Railway env vars.</i>",
            parse_mode="HTML"
        )
    except EnvironmentError as e:
        info = PROVIDER_INFO.get(provider_name, {})
        await message.answer(
            f"❌ <b>Cannot switch to {provider_name}</b>\n\n"
            f"<code>{str(e)[:200]}</code>\n\n"
            f"<b>Fix:</b>\n"
            f"1. Get API key from {info.get('url', 'provider website')}\n"
            f"2. Add <code>{info.get('key_var', 'API_KEY')}=your_key</code> to Railway env vars\n"
            f"3. Redeploy, then run /setprovider {provider_name} again",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Error: <code>{str(e)[:300]}</code>", parse_mode="HTML")
