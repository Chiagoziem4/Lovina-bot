"""
Encoding/Decoding Tool
Supports: base64, hex, binary, URL, HTML, ROT13, Morse
No API key needed
"""
import base64
import urllib.parse
import html
from typing import Dict

MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.'
}

REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}

async def encode(text: str, format: str = "all") -> Dict | str:
    """
    Encode text to various formats
    """
    try:
        if not text:
            return "❌ No text provided"
        
        results = {}
        text_bytes = text.encode() if isinstance(text, str) else text
        
        # Base64
        if format in ["base64", "all"]:
            results["base64"] = base64.b64encode(text_bytes).decode()
        
        # Hex
        if format in ["hex", "all"]:
            results["hex"] = text_bytes.hex()
        
        # Binary
        if format in ["binary", "all"]:
            results["binary"] = ''.join(format(ord(c), '08b') for c in text)
        
        # URL
        if format in ["url", "all"]:
            results["url"] = urllib.parse.quote(text)
        
        # HTML
        if format in ["html", "all"]:
            results["html"] = html.escape(text)
        
        # ROT13
        if format in ["rot13", "all"]:
            results["rot13"] = ''.join(
                chr((ord(c) - ord('a') + 13) % 26 + ord('a')) if c.isalpha() else c
                for c in text.lower()
            )
        
        # ASCII
        if format in ["ascii", "all"]:
            results["ascii"] = ' '.join(str(ord(c)) for c in text)
        
        return results if results else "❌ Invalid format"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

async def decode(text: str, format: str = "base64") -> str:
    """
    Decode text from various formats
    """
    try:
        if not text:
            return "❌ No text provided"
        
        text = text.strip()
        
        if format == "base64":
            try:
                decoded = base64.b64decode(text).decode()
                return decoded
            except:
                return "❌ Invalid base64"
        
        elif format == "hex":
            try:
                decoded = bytes.fromhex(text).decode()
                return decoded
            except:
                return "❌ Invalid hex"
        
        elif format == "url":
            return urllib.parse.unquote(text)
        
        elif format == "html":
            return html.unescape(text)
        
        elif format == "rot13":
            return ''.join(
                chr((ord(c) - ord('a') + 13) % 26 + ord('a')) if c.isalpha() else c
                for c in text.lower()
            )
        
        else:
            return "❌ Unsupported format"
    
    except Exception as e:
        return f"❌ Error: {str(e)}"
