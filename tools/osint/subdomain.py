"""
Subdomain Discovery
No API key needed (crt.sh + HackerTarget)
"""
import httpx
import json
from typing import List, Dict
from config import HTTP_TIMEOUT, USER_AGENTS
import random
import asyncio

async def discover_subdomains(domain: str) -> Dict | str:
    """
    Discover subdomains using:
    - crt.sh (certificate transparency)
    - HackerTarget free API
    """
    try:
        if not domain or len(domain) > 253:
            return "❌ Invalid domain"
        
        subdomains = set()
        
        # Use crt.sh
        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=HTTP_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    for entry in data:
                        names = entry.get("name_value", "").split("\n")
                        for name in names:
                            name = name.strip().lower()
                            if name and not name.startswith("*."):
                                subdomains.add(name)
        except Exception as e:
            pass
        
        # Use HackerTarget API
        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=HTTP_TIMEOUT)
                
                if response.status_code == 200:
                    lines = response.text.split("\n")
                    for line in lines:
                        if "," in line:
                            subdomain = line.split(",")[0].strip()
                            if subdomain:
                                subdomains.add(subdomain)
        except Exception as e:
            pass
        
        # Limit results
        subdomains = list(subdomains)[:50]
        
        if not subdomains:
            return f"❌ No subdomains found for {domain}"
        
        return {
            "domain": domain,
            "count": len(subdomains),
            "subdomains": sorted(subdomains)
        }
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
