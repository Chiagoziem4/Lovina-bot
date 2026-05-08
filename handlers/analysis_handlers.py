"""
Analysis Tool Handlers
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.permissions import require_not_banned
from utils.formatter import Formatter
from tools.analysis.hash_tool import generate_hashes, hash_identify
from tools.analysis.encoder import encode, decode
from tools.analysis.jwt_analyzer import analyze_jwt

router = Router()

@router.message(Command("hash"))
@require_not_banned
async def hash_command(message: Message):
    """
    /hash <text> - Generate all hash types
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /hash <text>")
        return
    
    text = args[1]
    
    result = await generate_hashes(text)
    
    if isinstance(result, dict):
        formatted = Formatter.format_hash_result(text, result)
    else:
        formatted = Formatter.error_message(result)
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await message.answer(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("hashid"))
@require_not_banned
async def hashid_command(message: Message):
    """
    /hashid <hash> - Identify hash type
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /hashid <hash>")
        return
    
    hash_value = args[1]
    result = await hash_identify(hash_value)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔍", "HASH IDENTIFICATION")
        formatted += f"\n<b>Hash:</b> <code>{hash_value[:32]}...</code>\n"
        formatted += f"<b>Length:</b> {result['length']} characters\n"
        formatted += f"<b>Possible Types:</b>\n"
        
        for hash_type in result['possible_types']:
            formatted += f"  • {hash_type}\n"
        
        formatted += f"\n{Formatter.section_divider()}\n⚠️ For educational and authorised use only"
    else:
        formatted = Formatter.error_message(result)
    
    await message.answer(formatted, parse_mode="HTML")

@router.message(Command("encode"))
@require_not_banned
async def encode_command(message: Message):
    """
    /encode <format> <text> - Encode text
    """
    args = message.text.split(maxsplit=2)
    
    if len(args) < 2:
        await message.reply("Usage: /encode <base64|hex|url|html|rot13> <text>")
        return
    
    format_type = args[1].lower()
    text = args[2] if len(args) > 2 else ""
    
    if not text:
        await message.reply("Usage: /encode <format> <text>")
        return
    
    result = await encode(text, format_type)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔐", "ENCODING")
        formatted += f"<b>Input:</b> <code>{text[:50]}</code>\n"
        formatted += Formatter.section_divider() + "\n"
        
        for enc_type, encoded_value in result.items():
            formatted += f"\n<b>{enc_type.upper()}:</b>\n<code>{encoded_value[:100]}</code>"
            if len(encoded_value) > 100:
                formatted += "..."
    else:
        formatted = Formatter.error_message(result)
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("decode"))
@require_not_banned
async def decode_command(message: Message):
    """
    /decode <format> <text> - Decode text
    """
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        await message.reply("Usage: /decode <base64|hex|url|html|rot13> <text>")
        return
    
    format_type = args[1].lower()
    text = args[2]
    
    result = await decode(text, format_type)
    
    formatted = Formatter.section_header("🔓", "DECODING")
    formatted += f"<b>Format:</b> {format_type.upper()}\n"
    formatted += Formatter.section_divider() + "\n"
    formatted += f"<b>Result:</b>\n<code>{result}</code>"
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("jwt"))
@require_not_banned
async def jwt_command(message: Message):
    """
    /jwt <token> - Analyze JWT token
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /jwt <token>")
        return
    
    token = args[1]
    result = await analyze_jwt(token)
    
    if isinstance(result, dict):
        formatted = Formatter.section_header("🔐", "JWT ANALYSIS")
        formatted += f"\n<b>Algorithm:</b> <code>{result['algorithm']}</code>\n"
        formatted += f"<b>Type:</b> {result['token_type']}\n"
        
        if "valid_until" in result:
            formatted += f"<b>Expires:</b> {result['valid_until']}\n"
            formatted += f"<b>Seconds Left:</b> {result['seconds_until_expiry']}\n"
        
        formatted += Formatter.section_divider() + "\n"
        formatted += "<b>Claims:</b>\n"
        
        for key, value in result['claims'].items():
            formatted += f"  <b>{key}:</b> {str(value)[:50]}\n"
        
        if result['warnings']:
            formatted += f"\n{Formatter.section_divider()}\n<b>⚠️ Warnings:</b>\n"
            for warning in result['warnings']:
                formatted += f"  {warning}\n"
    else:
        formatted = Formatter.error_message(result)
    
    messages = Formatter.truncate(formatted)
    for idx, msg_text in enumerate(messages):
        await message.answer(msg_text, parse_mode="HTML")
