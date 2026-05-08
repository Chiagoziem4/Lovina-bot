"""
Hash Generation Tool
Generate multiple hash types simultaneously
No API key needed
"""
import hashlib
from typing import Dict

async def generate_hashes(text: str) -> Dict | str:
    """
    Generate all common hash types
    MD5, SHA1, SHA224, SHA256, SHA384, SHA512, SHA3-256, BLAKE2b
    """
    try:
        if not text:
            return "❌ No text provided"
        
        if isinstance(text, str):
            text_bytes = text.encode()
        else:
            text_bytes = text
        
        hashes = {
            "MD5": hashlib.md5(text_bytes).hexdigest(),
            "SHA1": hashlib.sha1(text_bytes).hexdigest(),
            "SHA224": hashlib.sha224(text_bytes).hexdigest(),
            "SHA256": hashlib.sha256(text_bytes).hexdigest(),
            "SHA384": hashlib.sha384(text_bytes).hexdigest(),
            "SHA512": hashlib.sha512(text_bytes).hexdigest(),
            "SHA3-256": hashlib.sha3_256(text_bytes).hexdigest(),
            "BLAKE2b": hashlib.blake2b(text_bytes).hexdigest(),
        }
        
        return hashes
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def hash_identify(hash_value: str) -> Dict | str:
    """
    Identify hash type by length and pattern
    """
    try:
        hash_value = hash_value.strip().lower()
        hash_length = len(hash_value)
        
        # Identify by length
        hash_types = {
            32: ["MD5", "MD4", "MD2", "NTLM"],
            40: ["SHA1", "SHA160"],
            56: ["SHA224"],
            64: ["SHA256", "BLAKE2b-256"],
            96: ["SHA384"],
            128: ["SHA512", "BLAKE2b-512"],
            131: ["MD5(WordPress)"],
        }
        
        # Check bcrypt/special formats
        if hash_value.startswith("$2a$") or hash_value.startswith("$2b$"):
            return {"type": "bcrypt", "length": len(hash_value)}
        
        if hash_value.startswith("$argon2"):
            return {"type": "argon2", "length": len(hash_value)}
        
        # Check by length
        possible_types = hash_types.get(hash_length, ["Unknown"])
        
        return {
            "hash_type": possible_types,
            "length": hash_length,
            "possible_types": possible_types
        }
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
