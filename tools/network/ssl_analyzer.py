"""
SSL/TLS Certificate Analyzer
No API key needed
"""
import ssl
import socket
from typing import Dict
from datetime import datetime

async def analyze_ssl(domain: str, port: int = 443) -> Dict | str:
    """
    Analyze SSL/TLS certificate
    """
    try:
        if not domain:
            return "❌ Invalid domain"
        
        # Remove http/https
        domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
        
        # Create SSL context
        context = ssl.create_default_context()
        
        try:
            # Connect and get certificate
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    protocol = ssock.version()
                    
                    # Parse certificate
                    subject = dict(x[0] for x in cert.get('subject', []))
                    issued_to = subject.get('commonName', 'Unknown')
                    
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    issued_by = issuer.get('commonName', 'Unknown')
                    
                    # Dates
                    not_before = datetime.strptime(cert.get('notBefore', ''), '%b %d %H:%M:%S %Y %Z')
                    not_after = datetime.strptime(cert.get('notAfter', ''), '%b %d %H:%M:%S %Y %Z')
                    
                    days_valid = (not_after - datetime.utcnow()).days
                    
                    # SANs
                    sans = []
                    for name_type, name_value in cert.get('subjectAltName', []):
                        if name_type == 'DNS':
                            sans.append(name_value)
                    
                    return {
                        "domain": domain,
                        "issued_to": issued_to,
                        "issued_by": issued_by,
                        "valid_from": str(not_before),
                        "valid_to": str(not_after),
                        "days_until_expiry": days_valid,
                        "is_expired": days_valid < 0,
                        "is_expiring_soon": days_valid < 30,
                        "protocol": protocol,
                        "cipher": cipher[0],
                        "sans": sans
                    }
        
        except ssl.SSLError as e:
            return f"❌ SSL Error: {str(e)}"
        except socket.timeout:
            return "❌ Connection timeout"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
