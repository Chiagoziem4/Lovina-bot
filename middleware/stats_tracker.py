"""
Stats Tracker Middleware
"""
from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from config import STATS_FILE
from utils.storage import log_command

class StatsTrackerMiddleware(BaseMiddleware):
    """Track command usage statistics"""
    
    async def __call__(
        self,
        handler: Callable[[Update], Awaitable[Any]],
        event: Update,
        data: dict,
    ) -> Any:
        """Log command usage"""
        
        if event.message and event.message.text and event.message.text.startswith('/'):
            user_id = event.message.from_user.id
            
            # Extract command name
            parts = event.message.text.split()
            command = parts[0].lstrip('/')
            
            # Log to stats
            await log_command(STATS_FILE, user_id, command)
        
        return await handler(event, data)
