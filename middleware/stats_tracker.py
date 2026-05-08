"""
Stats Tracker Middleware
"""
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from config import STATS_FILE
from utils.storage import log_command

class StatsTrackerMiddleware(BaseMiddleware):
    """Track command usage statistics"""
    
    async def __call__(
        self,
        handler: Callable[[Message], Awaitable[Any]],
        event: Message,
        data: dict,
    ) -> Any:
        """Log command usage"""
        
        if event.text and event.text.startswith('/'):
            user_id = event.from_user.id
            
            # Extract command name
            parts = event.text.split()
            command = parts[0].lstrip('/')
            
            # Log to stats
            await log_command(STATS_FILE, user_id, command)
        
        return await handler(event, data)
