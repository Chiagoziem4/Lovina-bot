"""
Permission system for Lovina bot
4-tier hierarchy: LORD_NOCTIS > SUDO > RESEARCHER > PUBLIC
"""
from enum import Enum
from typing import Callable
from functools import wraps
from aiogram import types
from aiogram.types import Message
from config import LORD_NOCTIS_ID, SUDO_FILE, BANNED_FILE, ROLES_FILE
from utils.storage import get_sudo_users, is_banned, get_user_role

class Permission(Enum):
    """Permission levels"""
    PUBLIC = 0
    RESEARCHER = 1
    SUDO = 2
    LORD_NOCTIS = 3

async def get_user_permission(user_id: int) -> Permission:
    """Get user permission level"""
    
    # Check if banned
    if await is_banned(BANNED_FILE, user_id):
        return Permission.PUBLIC  # Banned users treated as public (blocked)
    
    # Check if Lord Noctis
    if user_id == LORD_NOCTIS_ID:
        return Permission.LORD_NOCTIS
    
    # Check if sudo
    sudo_users = await get_sudo_users(SUDO_FILE)
    if user_id in sudo_users:
        return Permission.SUDO
    
    # Check role
    role = await get_user_role(ROLES_FILE, user_id)
    if role == "researcher":
        return Permission.RESEARCHER
    
    return Permission.PUBLIC

async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    return await is_banned(BANNED_FILE, user_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERMISSION DECORATORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def require_permission(min_perm: Permission):
    """Decorator to require minimum permission level"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_perm = await get_user_permission(message.from_user.id)
            
            # Check if banned
            if await is_user_banned(message.from_user.id):
                return  # Silently ignore banned users
            
            if user_perm.value < min_perm.value:
                await message.reply(
                    "❌ <b>Access Denied</b>\n\n"
                    f"<i>Permission level required: {min_perm.name}</i>",
                    parse_mode="HTML"
                )
                return
            
            return await func(message, *args, **kwargs)
        
        return wrapper
    return decorator

def lord_noctis_only(func: Callable) -> Callable:
    """Only Lord Noctis can use this command"""
    return require_permission(Permission.LORD_NOCTIS)(func)

def require_sudo(func: Callable) -> Callable:
    """Sudo and Lord Noctis only"""
    return require_permission(Permission.SUDO)(func)

def require_researcher(func: Callable) -> Callable:
    """Researcher, Sudo, and Lord Noctis"""
    return require_permission(Permission.RESEARCHER)(func)

def require_not_banned(func: Callable) -> Callable:
    """Check if user is not banned"""
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if await is_user_banned(message.from_user.id):
            return  # Silently ignore
        return await func(message, *args, **kwargs)
    return wrapper

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERMISSION CHECKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def has_permission(user_id: int, required: Permission) -> bool:
    """Check if user has required permission"""
    user_perm = await get_user_permission(user_id)
    return user_perm.value >= required.value
