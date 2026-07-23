import asyncio
import socket
import time

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443, 27017]

SERVICE_MAP = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
}


async def _check_port(host: str, port: int, timeout: float = 2.0):
    try:
        conn = asyncio.open_connection(host, port)
        _, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return {"port": port, "state": "open", "service": SERVICE_MAP.get(port, "unknown")}
    except Exception:
        return None


async def port_scan(host: str, ports: list | None = None) -> dict | str:
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        return f"Cannot resolve hostname: {host}"
    scan_ports = ports or COMMON_PORTS
    start = time.time()
    results = await asyncio.gather(*[_check_port(ip, p) for p in scan_ports])
    elapsed = round(time.time() - start, 2)
    open_ports = [r for r in results if r]
    return {
        "host": host, "ip": ip,
        "open_ports": len(open_ports),
        "closed_ports": len(scan_ports) - len(open_ports),
        "scan_time": elapsed,
        "ports": {"open": open_ports}
    }
