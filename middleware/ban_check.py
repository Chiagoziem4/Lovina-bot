"""
Ban Check Middleware
"""
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from utils.permissions import is_user_banned

class BanCheckMiddleware(BaseMiddleware):
    """Check if user is banned"""
    
    async def __call__(
        self,
        handler: Callable[[Update], Awaitable[Any]],
        event: Update,
        data: dict,
    ) -> Any:
        """Silently ignore banned users"""
        
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
            
            # Check if banned
            if await is_user_banned(user_id):
                return  # Silently ignore
        
        return await handler(event, data)
