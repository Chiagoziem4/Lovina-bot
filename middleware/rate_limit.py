"""
Rate Limit Middleware
"""
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from utils.rate_limiter import check_rate_limit
from utils.formatter import Formatter

class RateLimitMiddleware(BaseMiddleware):
    """Rate limit enforcement middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Update], Awaitable[Any]],
        event: Update,
        data: dict,
    ) -> Any:
        """Check rate limit before processing command"""
        
        # Only check messages with commands
        if event.message and event.message.text and event.message.text.startswith('/'):
            user_id = event.message.from_user.id
            
            # Extract command name
            parts = event.message.text.split()
            command = parts[0].lstrip('/')  # Remove leading /
            
            # Check rate limit
            is_limited, wait_seconds = await check_rate_limit(user_id, command)
            
            if is_limited:
                response = (
                    "⏳ <b>Rate limit reached</b>\n\n"
                    f"Try again in <b>{wait_seconds}</b> seconds.\n"
                    "<i>Sudo users have unlimited access.</i>"
                )
                await event.message.reply(response, parse_mode="HTML")
                return
        
        return await handler(event, data)
