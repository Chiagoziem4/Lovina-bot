import base64
import urllib.parse
import html
import codecs


async def encode(text: str, format_type: str) -> dict | str:
    try:
        match format_type:
            case "base64":
                return {"base64": base64.b64encode(text.encode()).decode()}
            case "hex":
                return {"hex": text.encode().hex()}
            case "url":
                return {"url": urllib.parse.quote(text)}
            case "html":
                return {"html": html.escape(text)}
            case "rot13":
                return {"rot13": codecs.encode(text, "rot_13")}
            case _:
                return f"Unknown format: {format_type}. Use: base64, hex, url, html, rot13"
    except Exception as e:
        return f"Encoding failed: {e}"


async def decode(text: str, format_type: str) -> str:
    try:
        match format_type:
            case "base64":
                return base64.b64decode(text.encode()).decode(errors="replace")
            case "hex":
                return bytes.fromhex(text).decode(errors="replace")
            case "url":
                return urllib.parse.unquote(text)
            case "html":
                return html.unescape(text)
            case "rot13":
                return codecs.decode(text, "rot_13")
            case _:
                return f"Unknown format: {format_type}"
    except Exception as e:
        return f"Decoding failed: {e}"
