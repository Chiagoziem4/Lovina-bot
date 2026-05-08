"""
AI Handler - Lovina AI integration
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.permissions import require_not_banned
from utils.formatter import Formatter
from utils.lovina_ai import ai_chat, ai_explain, ai_threat_model, ai_pentest_report, ai_google_dork
from utils.storage import Storage
from config import RESEARCH_STATES_FILE

router = Router()

@router.message(Command("ai"))
@require_not_banned
async def ai_command(message: Message):
    """
    /ai <question> - Chat with Lovina AI
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /ai <question>")
        return
    
    question = args[1]
    user_id = message.from_user.id
    
    # Check if in research mode
    research_data = await Storage.load(RESEARCH_STATES_FILE)
    is_research = research_data.get(str(user_id), {}).get("active", False)
    
    msg = await message.answer(Formatter.loading_message("Consulting Lovina"))
    
    response = await ai_chat(user_id, question, research_mode=is_research)
    
    messages = Formatter.truncate(response)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("explain"))
@require_not_banned
async def explain_command(message: Message):
    """
    /explain <text> - Have Lovina explain security output
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /explain <security_output>")
        return
    
    text = args[1]
    user_id = message.from_user.id
    
    msg = await message.answer(Formatter.loading_message("Analyzing output"))
    
    response = await ai_explain(user_id, text)
    
    messages = Formatter.truncate(response)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("threat"))
@require_not_banned
async def threat_command(message: Message):
    """
    /threat <description> - Generate threat model
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /threat <target_description>")
        return
    
    description = args[1]
    user_id = message.from_user.id
    
    msg = await message.answer(Formatter.loading_message("Building threat model"))
    
    response = await ai_threat_model(user_id, description)
    
    messages = Formatter.truncate(response)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("dork"))
@require_not_banned
async def dork_command(message: Message):
    """
    /dork <topic> - Generate Google dork queries
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /dork <topic>")
        return
    
    topic = args[1]
    user_id = message.from_user.id
    
    msg = await message.answer(Formatter.loading_message("Generating Google dorks"))
    
    response = await ai_google_dork(user_id, topic)
    
    messages = Formatter.truncate(response)
    for idx, msg_text in enumerate(messages):
        if idx == 0:
            await msg.edit_text(msg_text, parse_mode="HTML")
        else:
            await message.answer(msg_text, parse_mode="HTML")

@router.message(Command("report"))
@require_not_banned
async def report_command(message: Message):
    """
    /report - Synthesize findings into pentest report
    """
    # In real implementation, would fetch latest findings from session
    await message.reply(
        "📋 <b>Generate Pentest Report</b>\n\n"
        "Provide findings to synthesize:\n"
        "<code>/ai here's a summary of vulnerabilities found...</code>\n\n"
        "Then use: <code>/report</code>",
        parse_mode="HTML"
    )

@router.message(Command("clear"))
@require_not_banned
async def clear_command(message: Message):
    """
    /clear - Clear conversation memory
    """
    user_id = message.from_user.id
    
    response = await ai_chat(user_id, "", clear_history=True)
    
    await message.answer(response, parse_mode="HTML")
