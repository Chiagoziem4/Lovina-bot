"""
Ban Check Middleware
"""
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from utils.permissions import is_user_banned

class BanCheckMiddleware(BaseMiddleware):
    """Check if user is banned"""
    
    async def __call__(
        self,
        handler: Callable[[Message], Awaitable[Any]],
        event: Message,
        data: dict,
    ) -> Any:
        """Silently ignore banned users"""
        
        if event.from_user:
            user_id = event.from_user.id
            
            # Check if banned
            if await is_user_banned(user_id):
                return  # Silently ignore
        
        return await handler(event, data)
