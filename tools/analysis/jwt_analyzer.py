import base64
import json
from datetime import datetime, timezone


async def analyze_jwt(token: str) -> dict | str:
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            return "Invalid JWT format (expected header.payload.signature)"

        def decode_part(p):
            p += "=" * (4 - len(p) % 4)
            return json.loads(base64.urlsafe_b64decode(p))

        header = decode_part(parts[0])
        payload = decode_part(parts[1])
        warnings = []

        algorithm = header.get("alg", "Unknown")
        if algorithm == "none":
            warnings.append("⚠️ Algorithm is 'none' — signature bypass possible")
        if algorithm.startswith("HS"):
            warnings.append("⚠️ Symmetric algorithm — vulnerable to brute force if weak secret")

        result = {
            "algorithm": algorithm,
            "token_type": header.get("typ", "JWT"),
            "claims": payload,
            "warnings": warnings,
        }

        if "exp" in payload:
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = (exp - now).total_seconds()
            result["valid_until"] = exp.strftime("%Y-%m-%d %H:%M:%S UTC")
            result["seconds_until_expiry"] = int(delta)
            if delta < 0:
                warnings.append("⚠️ Token is EXPIRED")

        return result
    except Exception as e:
        return f"JWT analysis failed: {e}"
