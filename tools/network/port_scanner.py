"""
Port Scanner - Pure Python async TCP scanner
No external dependencies
"""
import asyncio
import socket
from typing import Dict, List
import time

# Common port mappings
PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 3306: "MySQL", 3389: "RDP", 
    5900: "VNC", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
}

DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5900, 8080, 8443]

async def scan_port(host: str, port: int, timeout: float = 3.0) -> tuple:
    """
    Scan single port
    Returns: (port, is_open)
    """
    try:
        # Resolve hostname
        ip = socket.gethostbyname(host)
        
        # Try to connect
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout
        )
        
        writer.close()
        await writer.wait_closed()
        
        return port, True
    
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return port, False

async def port_scan(host: str, ports: List[int] = None, timeout: float = 3.0) -> Dict | str:
    """
    Scan ports on host
    """
    try:
        if not host:
            return "❌ Invalid host"
        
        # Clean host
        host = host.replace("http://", "").replace("https://", "").split("/")[0]
        
        # Get ports to scan
        if ports is None:
            ports_to_scan = DEFAULT_PORTS
        else:
            ports_to_scan = ports
        
        # Get IP
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            return f"❌ Could not resolve {host}"
        
        start_time = time.time()
        
        # Scan concurrently (batch of 20)
        results = {"open": [], "closed": []}
        
        for i in range(0, len(ports_to_scan), 20):
            batch = ports_to_scan[i:i+20]
            tasks = [scan_port(host, port, timeout) for port in batch]
            
            batch_results = await asyncio.gather(*tasks)
            
            for port, is_open in batch_results:
                if is_open:
                    service = PORT_SERVICES.get(port, "Unknown")
                    results["open"].append({"port": port, "service": service})
                else:
                    results["closed"].append(port)
        
        scan_time = time.time() - start_time
        
        return {
            "host": host,
            "ip": ip,
            "open_ports": len(results["open"]),
            "closed_ports": len(results["closed"]),
            "ports": results,
            "scan_time": round(scan_time, 2)
        }
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def quick_scan(host: str) -> Dict | str:
    """Quick scan of common ports"""
    return await port_scan(host, DEFAULT_PORTS)
