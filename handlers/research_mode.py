"""
Research Mode Handler
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config import RESEARCH_STATES_FILE, RESEARCH_PASSPHRASE
from utils.formatter import Formatter
from utils.storage import Storage
from utils.permissions import require_sudo

router = Router()

# Track research mode states
research_states: dict = {}

@router.message(Command("research"))
@require_sudo
async def research_command(message: Message):
    """
    /research - Activate research mode (passphrase required)
    """
    user_id = message.from_user.id
    
    # Set state to awaiting passphrase
    research_states[user_id] = "awaiting_passphrase"
    
    prompt = (
        "⚠️ <b>RESTRICTED ZONE</b>\n\n"
        "🔐 Attempting to activate Research Mode.\n\n"
        "<b>To proceed, answer:</b>\n"
        "<i>What do you stand for?</i>"
    )
    
    await message.answer(prompt, parse_mode="HTML")

@router.message(F.text, lambda msg: research_states.get(msg.from_user.id) == "awaiting_passphrase")
async def research_passphrase(message: Message):
    """
    Handle research mode passphrase
    """
    user_id = message.from_user.id
    answer = message.text.lower().strip()
    
    # Check passphrase
    if answer == RESEARCH_PASSPHRASE:
        # Activate research mode
        research_states[user_id] = None
        
        # Save to storage
        data = await Storage.load(RESEARCH_STATES_FILE)
        if "states" not in data:
            data["states"] = {}
        
        data["states"][str(user_id)] = {
            "active": True,
            "activated_at": str(__import__("datetime").datetime.utcnow())
        }
        
        await Storage.save(RESEARCH_STATES_FILE, data)
        
        response = (
            "✅ <b>Research Mode ACTIVATED</b>\n\n"
            "🔓 Full access granted\n"
            "📊 Advanced analysis enabled\n"
            "🚀 No rate limits\n\n"
            "Use /endresearch to deactivate"
        )
    else:
        # Wrong answer
        research_states[user_id] = None
        response = (
            "❌ <b>Access Denied</b>\n\n"
            "Incorrect answer. Research mode not activated.\n"
            "Use /research to try again."
        )
    
    await message.answer(response, parse_mode="HTML")

@router.message(Command("endresearch"))
async def endresearch_command(message: Message):
    """
    /endresearch - Deactivate research mode
    """
    user_id = message.from_user.id
    
    data = await Storage.load(RESEARCH_STATES_FILE)
    
    if str(user_id) in data.get("states", {}):
        data["states"][str(user_id)]["active"] = False
        await Storage.save(RESEARCH_STATES_FILE, data)
        
        response = "✅ Research Mode DEACTIVATED"
    else:
        response = "⚠️ Research mode not active"
    
    await message.answer(response, parse_mode="HTML")

@router.message(Command("research_status"))
async def research_status_command(message: Message):
    """
    /research_status - Check research mode status
    """
    user_id = message.from_user.id
    
    data = await Storage.load(RESEARCH_STATES_FILE)
    
    if str(user_id) in data.get("states", {}):
        is_active = data["states"][str(user_id)].get("active", False)
        status = "🟢 ACTIVE" if is_active else "🔴 INACTIVE"
    else:
        status = "🔴 INACTIVE"
    
    response = f"<b>Research Mode Status:</b> {status}"
    
    await message.answer(response, parse_mode="HTML")
