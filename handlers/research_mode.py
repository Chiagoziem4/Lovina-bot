"""
Research Mode Handler — uses aiogram FSM for state management
"""
import hashlib
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import RESEARCH_STATES_FILE
from utils.formatter import Formatter
from utils.storage import Storage
from utils.permissions import require_sudo
import datetime

router = Router()


class ResearchFlow(StatesGroup):
    awaiting_passphrase = State()


def verify_passphrase(answer: str) -> bool:
    from config import RESEARCH_PASSPHRASE
    if not RESEARCH_PASSPHRASE:
        return False
    expected = hashlib.sha256(RESEARCH_PASSPHRASE.encode()).hexdigest()
    given = hashlib.sha256(answer.strip().lower().encode()).hexdigest()
    return expected == given


@router.message(Command("research"))
@require_sudo
async def research_command(message: Message, state: FSMContext):
    await state.set_state(ResearchFlow.awaiting_passphrase)
    await message.answer(
        "⚠️ <b>RESTRICTED ZONE</b>\n\n"
        "🔐 Attempting to activate Research Mode.\n\n"
        "<b>To proceed, answer:</b>\n"
        "<i>What do you stand for?</i>",
        parse_mode="HTML"
    )


@router.message(ResearchFlow.awaiting_passphrase)
async def research_passphrase_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if verify_passphrase(message.text):
        data = await Storage.load(RESEARCH_STATES_FILE)
        if not isinstance(data, dict):
            data = {}
        if "states" not in data:
            data["states"] = {}
        data["states"][str(user_id)] = {
            "active": True,
            "activated_at": datetime.datetime.utcnow().isoformat()
        }
        await Storage.save(RESEARCH_STATES_FILE, data)
        await message.answer(
            "✅ <b>Research Mode ACTIVATED</b>\n\n"
            "🔓 Full access granted\n"
            "📊 Advanced analysis enabled\n"
            "🚀 No rate limits\n\n"
            "Use /endresearch to deactivate",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ <b>Access Denied</b>\n\n"
            "Incorrect answer. Research mode not activated.\n"
            "Use /research to try again.",
            parse_mode="HTML"
        )


@router.message(Command("endresearch"))
async def endresearch_command(message: Message):
    user_id = message.from_user.id
    data = await Storage.load(RESEARCH_STATES_FILE)
    if isinstance(data, dict) and str(user_id) in data.get("states", {}):
        data["states"][str(user_id)]["active"] = False
        await Storage.save(RESEARCH_STATES_FILE, data)
        response = "✅ Research Mode DEACTIVATED"
    else:
        response = "⚠️ Research mode was not active"
    await message.answer(response, parse_mode="HTML")


@router.message(Command("research_status"))
async def research_status_command(message: Message):
    user_id = message.from_user.id
    data = await Storage.load(RESEARCH_STATES_FILE)
    is_active = False
    if isinstance(data, dict):
        is_active = data.get("states", {}).get(str(user_id), {}).get("active", False)
    status = "🟢 ACTIVE" if is_active else "🔴 INACTIVE"
    await message.answer(f"<b>Research Mode Status:</b> {status}", parse_mode="HTML")
