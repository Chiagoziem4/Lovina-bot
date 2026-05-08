"""
JWT Token Analyzer
Decode and analyze JWT tokens
No API key needed
"""
import base64
import json
from typing import Dict
from datetime import datetime

async def analyze_jwt(token: str) -> Dict | str:
    """
    Decode and analyze JWT token without verifying signature
    """
    try:
        if not token or '.' not in token:
            return "❌ Invalid JWT token format"
        
        parts = token.split('.')
        
        if len(parts) != 3:
            return "❌ Invalid JWT format (must have 3 parts)"
        
        header_part, payload_part, signature_part = parts
        
        # Decode header
        try:
            header_data = base64.urlsafe_b64decode(header_part + '==')
            header = json.loads(header_data)
        except:
            return "❌ Failed to decode header"
        
        # Decode payload
        try:
            payload_data = base64.urlsafe_b64decode(payload_part + '==')
            payload = json.loads(payload_data)
        except:
            return "❌ Failed to decode payload"
        
        # Analyze
        result = {
            "algorithm": header.get("alg", "Unknown"),
            "token_type": header.get("typ", "JWT"),
            "claims": payload,
            "signature": signature_part[:20] + "...",
            "warnings": []
        }
        
        # Check for issues
        if header.get("alg") == "none":
            result["warnings"].append("⚠️ Using 'none' algorithm - INSECURE")
        
        # Check expiration
        if "exp" in payload:
            exp_time = datetime.utcfromtimestamp(payload["exp"])
            now = datetime.utcnow()
            
            if now > exp_time:
                result["warnings"].append(f"⚠️ Token EXPIRED at {exp_time}")
            else:
                time_left = (exp_time - now).total_seconds()
                result["valid_until"] = exp_time.isoformat()
                result["seconds_until_expiry"] = int(time_left)
        
        # Check for common claims
        if not any(k in payload for k in ["sub", "iss", "aud"]):
            result["warnings"].append("⚠️ Missing standard security claims")
        
        return result
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
