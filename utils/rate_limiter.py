"""
Rate limiter for user actions
"""
import time
from typing import Dict, List, Tuple
from config import RATE_LIMITS, LORD_NOCTIS_ID, SUDO_FILE
from utils.storage import get_sudo_users

class RateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self):
        self.user_actions: Dict[int, Dict[str, List[float]]] = {}
    
    async def is_limited(self, user_id: int, action: str = "default") -> Tuple[bool, int]:
        """
        Check if user is rate limited
        Returns: (is_limited, seconds_until_available)
        """
        
        # Lord Noctis and sudo users are never limited
        if user_id == LORD_NOCTIS_ID:
            return False, 0
        
        sudo_users = await get_sudo_users(SUDO_FILE)
        if user_id in sudo_users:
            return False, 0
        
        # Get rate limit for action
        if action not in RATE_LIMITS:
            action = "default"
        
        limit, window = RATE_LIMITS[action]
        current_time = time.time()
        
        # Initialize user tracking
        if user_id not in self.user_actions:
            self.user_actions[user_id] = {}
        
        if action not in self.user_actions[user_id]:
            self.user_actions[user_id][action] = []
        
        # Remove old timestamps outside window
        self.user_actions[user_id][action] = [
            ts for ts in self.user_actions[user_id][action]
            if current_time - ts < window
        ]
        
        # Check if limited
        if len(self.user_actions[user_id][action]) >= limit:
            # Calculate when next request is allowed
            oldest_timestamp = self.user_actions[user_id][action][0]
            time_until_available = int(window - (current_time - oldest_timestamp)) + 1
            return True, time_until_available
        
        # Record this action
        self.user_actions[user_id][action].append(current_time)
        return False, 0
    
    def cleanup_old_users(self, max_age: int = 3600):
        """Remove old user tracking data (older than max_age seconds)"""
        current_time = time.time()
        users_to_remove = []
        
        for user_id, actions in self.user_actions.items():
            # Check if any action has been recorded recently
            has_recent = False
            
            for action_list in actions.values():
                if action_list and current_time - action_list[-1] < max_age:
                    has_recent = True
                    break
            
            if not has_recent:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.user_actions[user_id]

# Global rate limiter instance
rate_limiter = RateLimiter()

async def check_rate_limit(user_id: int, action: str = "default") -> Tuple[bool, int]:
    """Check if user is rate limited"""
    return await rate_limiter.is_limited(user_id, action)
