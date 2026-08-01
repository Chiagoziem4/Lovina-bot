"""
Network Tool Handlers
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.permissions import require_not_banned
from utils.formatter import Formatter
from tools.network.port_scanner import port_scan
from tools.network.ssl_analyzer import analyze_ssl

router = Router()

@router.message(Command("portscan"))
@require_not_banned
async def scan_command(message: Message):
    """
    /scan <host> [ports] - TCP port scanner
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /portscan <host> [ports]\nExample: /portscan example.com 80,443,8080")
        return
    
    host = args[1]
    
    # Parse ports
    ports = None
    if len(args) > 2:
        try:
            ports = [int(p) for p in args[2].split(",")]
        except:
            ports = None
    
    msg = await message.answer(Formatter.loading_message("Scanning ports", host))
    
    result = await port_scan(host, ports)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔍", "PORT SCAN", f"{result['host']} ({result['ip']})")
        formatted += f"\n<b>Open Ports:</b> {result['open_ports']}\n"
        formatted += f"<b>Closed Ports:</b> {result['closed_ports']}\n"
        formatted += f"<b>Scan Time:</b> {result['scan_time']}s\n"
        formatted += Formatter.section_divider() + "\n"
        
        if result['ports']['open']:
            formatted += "<b>🟢 Open Ports:</b>\n"
            for port_info in result['ports']['open']:
                formatted += f"  {port_info['port']:5d} - {port_info['service']}\n"
        
        formatted += f"\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    
    await msg.edit_text(formatted, parse_mode="HTML")

@router.message(Command("ssl"))
@require_not_banned
async def ssl_command(message: Message):
    """
    /ssl <domain> - SSL/TLS certificate analysis
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /ssl <domain>")
        return
    
    domain = args[1]
    msg = await message.answer(Formatter.loading_message("Analyzing SSL certificate", domain))
    
    result = await analyze_ssl(domain)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔐", "SSL/TLS CERTIFICATE", domain)
        formatted += f"\n<b>Issued To:</b> {result['issued_to']}\n"
        formatted += f"<b>Issued By:</b> {result['issued_by']}\n"
        formatted += f"<b>Valid From:</b> {result['valid_from']}\n"
        formatted += f"<b>Valid To:</b> {result['valid_to']}\n"
        
        if result['is_expired']:
            formatted += f"\n🔴 <b>EXPIRED - {result['days_until_expiry']} days ago</b>"
        elif result['is_expiring_soon']:
            formatted += f"\n🟡 <b>EXPIRING SOON - {result['days_until_expiry']} days left</b>"
        else:
            formatted += f"\n🟢 <b>VALID - {result['days_until_expiry']} days until expiry</b>"
        
        formatted += f"\n\n<b>Protocol:</b> {result['protocol']}\n"
        formatted += f"<b>Cipher:</b> {result['cipher']}\n"
        
        if result['sans']:
            formatted += f"\n<b>Subject Alternative Names:</b>\n"
            for san in result['sans'][:10]:
                formatted += f"  • {san}\n"
        
        formatted += f"\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")
