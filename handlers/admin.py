"""
Admin Handler - Lord Noctis + Sudo commands
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.permissions import lord_noctis_only, require_sudo, Permission, get_user_permission
from utils.formatter import Formatter
from utils.storage import (
    add_sudo_user, remove_sudo_user, get_sudo_users,
    ban_user, unban_user, is_banned, set_user_role,
    get_stats, add_group, get_groups
)
from config import SUDO_FILE, BANNED_FILE, ROLES_FILE, STATS_FILE, GROUPS_FILE, LORD_NOCTIS_ID

router = Router()

@router.message(Command("addsudo"))
@lord_noctis_only
async def addsudo_command(message: Message):
    """
    /addsudo <user_id> - Add sudo user (Lord Noctis only)
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /addsudo <user_id>")
        return
    
    try:
        user_id = int(args[1])
        
        if user_id == LORD_NOCTIS_ID:
            await message.reply("❌ Cannot add Lord Noctis as sudo (already max)")
            return
        
        success = await add_sudo_user(SUDO_FILE, user_id)
        
        if success:
            await message.answer(f"✅ User {user_id} is now SUDO")
        else:
            await message.answer(f"⚠️ User {user_id} is already SUDO")
    
    except ValueError:
        await message.reply("❌ Invalid user ID")

@router.message(Command("removesudo"))
@lord_noctis_only
async def removesudo_command(message: Message):
    """
    /removesudo <user_id> - Remove sudo user (Lord Noctis only)
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /removesudo <user_id>")
        return
    
    try:
        user_id = int(args[1])
        
        success = await remove_sudo_user(SUDO_FILE, user_id)
        
        if success:
            await message.answer(f"✅ User {user_id} removed from SUDO")
        else:
            await message.answer(f"⚠️ User {user_id} is not SUDO")
    
    except ValueError:
        await message.reply("❌ Invalid user ID")

@router.message(Command("sudolist"))
@require_sudo
async def sudolist_command(message: Message):
    """
    /sudolist - List all sudo users
    """
    sudo_users = await get_sudo_users(SUDO_FILE)
    
    formatted = "<b>👑 Sudo Users</b>\n\n"
    
    if sudo_users:
        for user_id in sudo_users:
            formatted += f"• <code>{user_id}</code>\n"
    else:
        formatted += "<i>No sudo users</i>"
    
    formatted += f"\n<b>Lord Noctis:</b> <code>{LORD_NOCTIS_ID}</code>"
    
    await message.answer(formatted, parse_mode="HTML")

@router.message(Command("ban"))
@require_sudo
async def ban_command(message: Message):
    """
    /ban <user_id> - Ban user
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(args[1])
        
        if user_id == LORD_NOCTIS_ID:
            await message.reply("❌ Cannot ban Lord Noctis")
            return
        
        success = await ban_user(BANNED_FILE, user_id)
        
        if success:
            await message.answer(f"✅ User {user_id} banned")
        else:
            await message.answer(f"⚠️ User {user_id} is already banned")
    
    except ValueError:
        await message.reply("❌ Invalid user ID")

@router.message(Command("unban"))
@require_sudo
async def unban_command(message: Message):
    """
    /unban <user_id> - Unban user
    """
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(args[1])
        
        banned = await is_banned(BANNED_FILE, user_id)
        
        if not banned:
            await message.reply(f"⚠️ User {user_id} is not banned")
            return
        
        from utils.storage import unban_user
        success = await unban_user(BANNED_FILE, user_id)
        
        if success:
            await message.answer(f"✅ User {user_id} unbanned")
    
    except ValueError:
        await message.reply("❌ Invalid user ID")

@router.message(Command("role"))
@require_sudo
async def role_command(message: Message):
    """
    /role <user_id> <role> - Assign researcher role
    """
    args = message.text.split()
    
    if len(args) < 3:
        await message.reply("Usage: /role <user_id> <public|researcher|sudo>")
        return
    
    try:
        user_id = int(args[1])
        role = args[2].lower()
        
        if role not in ["public", "researcher", "sudo"]:
            await message.reply("❌ Invalid role (public|researcher|sudo)")
            return
        
        await set_user_role(ROLES_FILE, user_id, role)
        await message.answer(f"✅ User {user_id} assigned role: <b>{role}</b>", parse_mode="HTML")
    
    except ValueError:
        await message.reply("❌ Invalid user ID")

@router.message(Command("stats"))
@require_sudo
async def stats_command(message: Message):
    """
    /stats - View bot statistics
    """
    stats = await get_stats(STATS_FILE)
    
    formatted = "<b>📊 Bot Statistics</b>\n\n"
    
    commands = stats.get("commands", {})
    users = stats.get("users", [])
    
    formatted += f"<b>Total Unique Users:</b> {len(users)}\n"
    formatted += f"<b>Total Commands:</b> {sum(commands.values())}\n\n"
    
    if commands:
        formatted += "<b>Top Commands:</b>\n"
        top_cmds = sorted(commands.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for cmd, count in top_cmds:
            formatted += f"  /{cmd}: {count}\n"
    
    await message.answer(formatted, parse_mode="HTML")

@router.message(Command("broadcast"))
@lord_noctis_only
async def broadcast_command(message: Message):
    """
    /broadcast <message> - Send message to all monitored groups
    """
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.reply("Usage: /broadcast <message>")
        return
    
    broadcast_msg = args[1]
    groups = await get_groups(GROUPS_FILE)
    
    sent = 0
    for group_id in groups.keys():
        try:
            await message.bot.send_message(
                int(group_id),
                f"📢 <b>Broadcast from Noctis</b>\n\n{broadcast_msg}",
                parse_mode="HTML"
            )
            sent += 1
        except:
            pass
    
    await message.answer(f"✅ Broadcast sent to {sent} groups", parse_mode="HTML")
