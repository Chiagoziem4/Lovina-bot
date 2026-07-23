"""
OSINT Tool Handlers
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.permissions import require_not_banned
from utils.formatter import Formatter
from tools.osint.ip_lookup import ip_lookup
from tools.osint.dns_tool import dns_lookup
from tools.osint.subdomain import discover_subdomains
from tools.osint.username_hunt import check_username
from tools.osint.whois_tool import whois_lookup

router = Router()

@router.message(Command("ip"))
@require_not_banned
async def ip_command(message: Message):
    """
    /ip <address> - IP geolocation lookup
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /ip <IP_address>")
        return
    
    ip_address = args[1]
    msg = await message.answer(Formatter.loading_message("Resolving IP", ip_address))
    
    result = await ip_lookup(ip_address)
    
    if isinstance(result, dict):
        formatted = Formatter.format_ip_result(
            result["ip"],
            result["location"],
            result["asn"],
            result["isp"],
            result["timezone"],
            f"{result['latitude']}, {result['longitude']}",
            result.get("hostname", "")
        )
    else:
        formatted = Formatter.error_message(result)
    
    await msg.edit_text(formatted, parse_mode="HTML")

@router.message(Command("dns"))
@require_not_banned
async def dns_command(message: Message):
    """
    /dns <domain> [type] - DNS record lookup
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /dns <domain> [A|AAAA|MX|NS|TXT]")
        return
    
    domain = args[1]
    record_type = args[2].upper() if len(args) > 2 else "A"
    
    msg = await message.answer(Formatter.loading_message("Looking up DNS records", domain))
    
    result = await dns_lookup(domain, record_type)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔍", "DNS RECORDS", domain)
        formatted += f"\n<b>Record Type:</b> {result['type']}\n"
        formatted += Formatter.section_divider() + "\n"
        
        for record in result['records']:
            formatted += f"• <code>{record}</code>\n"
        
        formatted += f"\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    
    await msg.edit_text(formatted, parse_mode="HTML")

@router.message(Command("subdomains"))
@require_not_banned
async def subdomains_command(message: Message):
    """
    /subdomains <domain> - Passive subdomain discovery
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /subdomains <domain>")
        return
    
    domain = args[1]
    msg = await message.answer(Formatter.loading_message("Discovering subdomains", domain))
    
    result = await discover_subdomains(domain)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🌐", "SUBDOMAINS", domain)
        formatted += f"\n<b>Found:</b> {result['count']} subdomains\n"
        formatted += Formatter.section_divider() + "\n"
        
        for subdomain in result['subdomains'][:20]:  # First 20
            formatted += f"• <code>{subdomain}</code>\n"
        
        if result['count'] > 20:
            formatted += f"\n... and {result['count'] - 20} more"
        
        formatted += f"\n\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("username"))
@require_not_banned
async def username_command(message: Message):
    """
    /username <username> - Check across 27+ platforms
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /username <username>")
        return
    
    username = args[1]
    msg = await message.answer(Formatter.loading_message("Searching username", username))
    
    result = await check_username(username)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("👤", "USERNAME SEARCH", username)
        formatted += f"\n<b>Found:</b> {result['found_count']} platforms\n"
        formatted += f"<b>Not Found:</b> {result['not_found_count']} platforms\n"
        formatted += Formatter.section_divider() + "\n"
        
        if result['results']['found']:
            formatted += "<b>✅ Found On:</b>\n"
            for item in result['results']['found']:
                formatted += f"<a href='{item['url']}'>{item['platform']}</a>\n"
        
        formatted += f"\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")


@router.message(Command("whois"))
@require_not_banned
async def whois_command(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /whois <domain|ip>")
        return
    target = args[1]
    msg = await message.answer(Formatter.loading_message("WHOIS lookup", target))
    result = await whois_lookup(target)
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔍", "WHOIS", target)
        formatted += f"\n<b>Registrar:</b> {result['registrar']}\n"
        formatted += f"<b>Created:</b> {result['creation_date']}\n"
        formatted += f"<b>Expires:</b> {result['expiration_date']}\n"
        formatted += f"<b>Country:</b> {result['country']}\n"
        if result['name_servers']:
            formatted += "\n<b>Name Servers:</b>\n"
            for ns in result['name_servers']:
                formatted += f"  • <code>{ns}</code>\n"
        formatted += f"\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    await msg.edit_text(formatted, parse_mode="HTML")
