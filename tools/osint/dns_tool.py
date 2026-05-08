"""
DNS Lookup Tool
No API key needed (dnspython direct queries)
"""
import dns.resolver
import dns.exception
from typing import Dict, List, Optional

async def dns_lookup(domain: str, record_type: str = "A") -> Dict | str:
    """
    Lookup DNS records for domain
    Supports: A, AAAA, MX, NS, TXT, CNAME, SOA
    """
    try:
        # Validate domain
        if not domain or len(domain) > 253:
            return "❌ Invalid domain"
        
        # Remove http/https if present
        domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
        
        record_type = record_type.upper()
        
        # Supported types
        if record_type not in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
            record_type = "A"
        
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, record_type)
            
            records = []
            for rdata in answers:
                if record_type == "MX":
                    records.append(f"{rdata.exchange} (priority: {rdata.preference})")
                elif record_type in ["NS", "CNAME"]:
                    records.append(str(rdata.target).rstrip('.'))
                elif record_type == "SOA":
                    records.append(f"NS: {rdata.mname}, Email: {rdata.rname}, Serial: {rdata.serial}")
                else:
                    records.append(str(rdata))
            
            return {
                "domain": domain,
                "type": record_type,
                "records": records
            }
        
        except dns.exception.NXDOMAIN:
            return f"❌ Domain not found: {domain}"
        except dns.exception.Timeout:
            return "❌ DNS query timeout"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def dns_lookup_all(domain: str) -> Dict | str:
    """Lookup all common DNS record types"""
    try:
        results = {}
        
        for record_type in ["A", "AAAA", "MX", "NS", "TXT"]:
            result = await dns_lookup(domain, record_type)
            
            if isinstance(result, dict):
                results[record_type] = result.get("records", [])
        
        return {
            "domain": domain,
            "records": results
        }
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
