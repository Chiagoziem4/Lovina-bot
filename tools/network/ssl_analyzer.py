import ssl
import socket
import asyncio
from datetime import datetime, timezone


async def analyze_ssl(domain: str, port: int = 443) -> dict | str:
    try:
        loop = asyncio.get_event_loop()
        def _get_cert():
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    return ssock.getpeercert(), ssock.cipher(), ssock.version()
        cert, cipher_info, protocol = await loop.run_in_executor(None, _get_cert)
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_left = (not_after - now).days
        subject = dict(x[0] for x in cert["subject"])
        issuer = dict(x[0] for x in cert["issuer"])
        sans = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]
        return {
            "issued_to": subject.get("commonName", domain),
            "issued_by": issuer.get("organizationName", "Unknown"),
            "valid_from": not_before.strftime("%Y-%m-%d"),
            "valid_to": not_after.strftime("%Y-%m-%d"),
            "days_until_expiry": days_left,
            "is_expired": days_left < 0,
            "is_expiring_soon": 0 <= days_left <= 30,
            "protocol": protocol,
            "cipher": cipher_info[0] if cipher_info else "Unknown",
            "sans": sans,
        }
    except Exception as e:
        return f"SSL analysis failed: {e}"
