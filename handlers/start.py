"""
Start, Help, About commands
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from config import BOT_NAME, CREATOR, BOT_VERSION
from utils.permissions import get_user_permission, Permission

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    """
    /start - Welcome message
    """
    user_perm = await get_user_permission(message.from_user.id)
    perm_level = user_perm.name
    
    welcome = (
        f"<b>🌙 Welcome to {BOT_NAME}</b>\n\n"
        f"<i>An AI-powered cybersecurity research assistant created by {CREATOR}</i>\n\n"
        f"<b>Your Access Level:</b> <code>{perm_level}</code>\n\n"
        f"<b>Core Capabilities:</b>\n"
        f"✓ OSINT & Reconnaissance\n"
        f"✓ Network Analysis\n"
        f"✓ Security Intelligence\n"
        f"✓ AI-powered Insights\n"
        f"✓ Cryptography Tools\n\n"
        f"<b>Use /help to see all commands</b>"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Commands", callback_data="help_menu")],
        [InlineKeyboardButton(text="ℹ️ About", callback_data="about_bot")],
    ])
    
    await message.answer(welcome, parse_mode="HTML", reply_markup=keyboard)

@router.message(Command("help"))
async def help_command(message: Message):
    """
    /help [category] - Show available commands
    """
    args = message.text.split()
    category = args[1].lower() if len(args) > 1 else None
    
    help_text = ""
    
    if category in [None, "osint"]:
        help_text += (
            "<b>🔍 OSINT Tools:</b>\n"
            "/ip <address> - IP geolocation lookup\n"
            "/dns <domain> [type] - DNS record lookup\n"
            "/whois <domain|ip> - WHOIS information\n"
            "/ssl <domain> - SSL/TLS certificate analysis\n"
            "/subdomains <domain> - Passive subdomain discovery\n"
            "/username <username> - Search across 27+ platforms\n\n"
        )
    
    if category in [None, "network"]:
        help_text += (
            "<b>🌐 Network Tools:</b>\n"
            "/scan <host> [ports] - TCP port scanner\n"
            "/tech <url> - Web technology fingerprinting\n"
            "/headers <url> - HTTP security header audit\n\n"
        )
    
    if category in [None, "analysis"]:
        help_text += (
            "<b>🔬 Analysis Tools:</b>\n"
            "/hash <text> - Generate all hash types\n"
            "/hashid <hash> - Identify hash type\n"
            "/encode <format> <text> - Encode text\n"
            "/decode <format> <text> - Decode text\n"
            "/jwt <token> - JWT token analyzer\n"
            "/cve <CVE-ID> - CVE vulnerability lookup\n\n"
        )
    
    if category in [None, "crypto"]:
        help_text += (
            "<b>🔐 Crypto Tools:</b>\n"
            "/encrypt <algo> <text> [key] - Encrypt text\n"
            "/decrypt <algo> <text> [key] - Decrypt text\n"
            "/convert <format> <value> - Convert number bases\n\n"
        )
    
    if category in [None, "ai"]:
        help_text += (
            "<b>🧠 AI Tools:</b>\n"
            "/ai <question> - Chat with Lovina AI\n"
            "/explain <text> - Explain security output\n"
            "/threat <description> - Generate threat model\n"
            "/report - Synthesize findings into report\n"
            "/dork <topic> - Generate Google dork queries\n"
            "/clear - Clear conversation memory\n\n"
        )
    
    user_perm = await get_user_permission(message.from_user.id)
    
    if user_perm.value >= Permission.SUDO.value:
        help_text += (
            "<b>👑 Admin Commands:</b>\n"
            "/addsudo <user_id> - Add sudo user\n"
            "/removesudo <user_id> - Remove sudo user\n"
            "/sudolist - List sudo users\n"
            "/ban <user_id> - Ban user\n"
            "/unban <user_id> - Unban user\n"
            "/role <user_id> <role> - Assign researcher role\n"
            "/stats - View bot statistics\n"
            "/groups - Manage group monitoring\n\n"
        )
    
    if category in [None, "research"]:
        help_text += (
            "<b>🔐 Research Mode:</b>\n"
            "/research - Activate research mode\n"
            "/endresearch - Deactivate research mode\n\n"
        )
    
    help_text += f"<i>v{BOT_VERSION}</i>"
    
    await message.answer(help_text, parse_mode="HTML")

@router.message(Command("about"))
async def about_command(message: Message):
    """
    /about - Bot information
    """
    about_text = (
        f"<b>About {BOT_NAME}</b>\n\n"
        f"<b>Creator:</b> {CREATOR}\n"
        f"<b>Version:</b> {BOT_VERSION}\n"
        f"<b>Telegram:</b> @VilegurlBot\n\n"
        f"<b>Purpose:</b>\n"
        f"An academic cybersecurity research assistant demonstrating "
        f"professional security analysis tools integrated with Telegram.\n\n"
        f"<b>Tech Stack:</b>\n"
        f"• Python 3.11+\n"
        f"• Aiogram 3 (Async Telegram Framework)\n"
        f"• Groq API (LLM Integration)\n"
        f"• 27+ No-API Security Tools\n\n"
        f"<b>⚠️ Disclaimer:</b>\n"
        f"<i>For authorized security research and educational purposes only. "
        f"All tools should be used ethically and legally. Unauthorized access "
        f"to computer systems is illegal.</i>\n\n"
        f"<b>🔐 Features:</b>\n"
        f"✓ 4-tier permission system\n"
        f"✓ Research mode activation\n"
        f"✓ Rate limiting\n"
        f"✓ Group monitoring\n"
        f"✓ AI-powered analysis\n"
    )
    
    await message.answer(about_text, parse_mode="HTML")

@router.message(Command("status"))
async def status_command(message: Message):
    """
    /status - Bot status and statistics
    """
    # This would require tracking uptime and stats
    status_text = (
        "<b>📊 Bot Status</b>\n\n"
        "🟢 <b>Online</b>\n"
        "⏱️ Uptime: Calculating...\n"
        "👥 Active Users: Tracking...\n"
        "📈 Total Commands: Monitoring...\n\n"
        "<i>Statistics tracking enabled</i>"
    )
    
    await message.answer(status_text, parse_mode="HTML")
