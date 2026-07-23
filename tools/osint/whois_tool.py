import asyncio
import whois as python_whois


async def whois_lookup(target: str) -> dict | str:
    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, python_whois.whois, target)
        return {
            "domain": target,
            "registrar": str(data.registrar or "N/A"),
            "creation_date": str(data.creation_date or "N/A"),
            "expiration_date": str(data.expiration_date or "N/A"),
            "name_servers": list(data.name_servers or [])[:5],
            "status": str(data.status or "N/A")[:100],
            "country": str(data.country or "N/A"),
        }
    except Exception as e:
        return f"WHOIS lookup failed: {e}"
