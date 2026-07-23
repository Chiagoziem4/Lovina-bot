import httpx


async def discover_subdomains(domain: str) -> dict | str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(
                f"https://crt.sh/?q=%.{domain}&output=json",
                headers={"Accept": "application/json"}
            )
            data = r.json()
        seen = set()
        subs = []
        for entry in data:
            for name in entry.get("name_value", "").split("\n"):
                sub = name.strip().lower().lstrip("*.")
                if sub and sub.endswith(domain) and sub not in seen:
                    seen.add(sub)
                    subs.append(sub)
        subs.sort()
        return {"domain": domain, "count": len(subs), "subdomains": subs}
    except Exception as e:
        return f"Subdomain discovery failed: {e}"
