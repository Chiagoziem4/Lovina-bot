import httpx
from config import HTTP_TIMEOUT


async def ip_lookup(ip_address: str) -> dict | str:
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            r = await client.get(
                f"http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,lat,lon,timezone,isp,org,as,query,reverse"
            )
            data = r.json()
        if data.get("status") != "success":
            return data.get("message", "Lookup failed")
        return {
            "ip": data["query"],
            "location": f"{data['city']}, {data['regionName']}, {data['country']}",
            "asn": data.get("as", "N/A"),
            "isp": data.get("isp", "N/A"),
            "timezone": data.get("timezone", "N/A"),
            "latitude": data.get("lat", 0),
            "longitude": data.get("lon", 0),
            "hostname": data.get("reverse", ""),
        }
    except Exception as e:
        return f"IP lookup failed: {e}"
