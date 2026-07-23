import asyncio
import dns.resolver
from config import HTTP_TIMEOUT


async def dns_lookup(domain: str, record_type: str = "A") -> dict | str:
    try:
        loop = asyncio.get_event_loop()
        def _resolve():
            resolver = dns.resolver.Resolver()
            resolver.lifetime = HTTP_TIMEOUT
            answers = resolver.resolve(domain, record_type)
            return [str(r) for r in answers]
        records = await loop.run_in_executor(None, _resolve)
        return {"domain": domain, "type": record_type, "records": records}
    except dns.resolver.NXDOMAIN:
        return f"Domain {domain} does not exist"
    except dns.resolver.NoAnswer:
        return f"No {record_type} records found for {domain}"
    except Exception as e:
        return f"DNS lookup failed: {e}"
