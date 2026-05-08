"""
Storage utilities for JSON file handling
"""
import json
import os
from typing import Dict, List, Any
import asyncio

class Storage:
    """JSON file-based storage"""
    
    @staticmethod
    async def load(filepath: str) -> Dict | List:
        """Load JSON file asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, Storage._load_sync, filepath)
    
    @staticmethod
    def _load_sync(filepath: str) -> Dict | List:
        """Synchronous load"""
        if not os.path.exists(filepath):
          return {} if filepath.endswith(("sudo.json", "banned.json", "roles.json", "stats.json", "groups.json")) else []
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    async def save(filepath: str, data: Dict | List) -> None:
        """Save JSON file asynchronously"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, Storage._save_sync, filepath, data)
    
    @staticmethod
    def _save_sync(filepath: str, data: Dict | List) -> None:
        """Synchronous save"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUDO USER MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_sudo_users(sudo_file: str) -> List[int]:
    """Get list of sudo user IDs"""
    data = await Storage.load(sudo_file)
    return data.get("users", [])

async def add_sudo_user(sudo_file: str, user_id: int) -> bool:
    """Add sudo user"""
    data = await Storage.load(sudo_file)
    if "users" not in data:
        data["users"] = []
    if user_id not in data["users"]:
        data["users"].append(user_id)
        await Storage.save(sudo_file, data)
        return True
    return False

async def remove_sudo_user(sudo_file: str, user_id: int) -> bool:
    """Remove sudo user"""
    data = await Storage.load(sudo_file)
    if "users" in data and user_id in data["users"]:
        data["users"].remove(user_id)
        await Storage.save(sudo_file, data)
        return True
    return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BAN MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def is_banned(banned_file: str, user_id: int) -> bool:
    """Check if user is banned"""
    data = await Storage.load(banned_file)
    return user_id in data.get("users", [])

async def ban_user(banned_file: str, user_id: int) -> bool:
    """Ban a user"""
    data = await Storage.load(banned_file)
    if "users" not in data:
        data["users"] = []
    if user_id not in data["users"]:
        data["users"].append(user_id)
        await Storage.save(banned_file, data)
        return True
    return False

async def unban_user(banned_file: str, user_id: int) -> bool:
    """Unban a user"""
    data = await Storage.load(banned_file)
    if "users" in data and user_id in data["users"]:
        data["users"].remove(user_id)
        await Storage.save(banned_file, data)
        return True
    return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROLE MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_user_role(roles_file: str, user_id: int) -> str:
    """Get user role (public, researcher, sudo)"""
    data = await Storage.load(roles_file)
    return data.get(str(user_id), "public")

async def set_user_role(roles_file: str, user_id: int, role: str) -> None:
    """Set user role"""
    data = await Storage.load(roles_file)
    data[str(user_id)] = role
    await Storage.save(roles_file, data)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATS MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def log_command(stats_file: str, user_id: int, command: str) -> None:
    """Log command usage"""
    data = await Storage.load(stats_file)
    
    if "commands" not in data:
        data["commands"] = {}
    if "users" not in data:
        data["users"] = set()
    
    data["commands"][command] = data["commands"].get(command, 0) + 1
    data["users"] = list(set(data.get("users", []) + [user_id]))
    
    await Storage.save(stats_file, data)

async def get_stats(stats_file: str) -> Dict:
    """Get bot statistics"""
    return await Storage.load(stats_file)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GROUP MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_group(groups_file: str, group_id: int, group_name: str) -> None:
    """Add group to monitoring list"""
    data = await Storage.load(groups_file)
    
    if "groups" not in data:
        data["groups"] = {}
    
    data["groups"][str(group_id)] = {
        "name": group_name,
        "enabled": True,
        "schedule": "daily"
    }
    
    await Storage.save(groups_file, data)

async def get_groups(groups_file: str) -> Dict:
    """Get all monitored groups"""
    data = await Storage.load(groups_file)
    return data.get("groups", {})

async def update_group_schedule(groups_file: str, group_id: int, schedule: str) -> None:
    """Update group update schedule"""
    data = await Storage.load(groups_file)
    
    if "groups" not in data:
        data["groups"] = {}
    
    if str(group_id) in data["groups"]:
        data["groups"][str(group_id)]["schedule"] = schedule
        await Storage.save(groups_file, data)
