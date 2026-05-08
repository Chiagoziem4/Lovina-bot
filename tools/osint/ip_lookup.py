"""
IP Lookup - Geolocation, ASN, ISP data
No API key needed (ipapi.co free)
"""
import httpx
import json
from typing import Dict, Optional
from config import HTTP_TIMEOUT, USER_AGENTS
import random

async def ip_lookup(ip: str) -> Dict | str:
    """
    Lookup IP geolocation, ASN, ISP
    """
    try:
        # Validate IP
        if not ip or len(ip) > 39:
            return "❌ Invalid IP address"
        
        # Use ipapi.co (no key required)
        url = f"https://ipapi.co/{ip}/json/"
        
        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "curl/7.68.0"
            ])
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "ip": data.get("ip", ip),
                    "location": f"{data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country_name', 'Unknown')}",
                    "asn": data.get("asn", "Unknown"),
                    "isp": data.get("org", "Unknown"),
                    "timezone": data.get("timezone", "Unknown"),
                    "latitude": data.get("latitude", "Unknown"),
                    "longitude": data.get("longitude", "Unknown"),
                    "hostname": data.get("hostname", "N/A")
                }
            else:
                return "❌ IP lookup failed"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
