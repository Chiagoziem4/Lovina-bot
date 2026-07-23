import hashlib

HASH_LENGTH_MAP = {
    32: ["MD5"],
    40: ["SHA-1"],
    56: ["SHA-224"],
    64: ["SHA-256", "Blake2s", "SHA3-256"],
    96: ["SHA-384"],
    128: ["SHA-512", "SHA3-512", "BLAKE2b-512"],
}


async def generate_hashes(text: str) -> dict | str:
    try:
        encoded = text.encode()
        return {
            "MD5": hashlib.md5(encoded).hexdigest(),
            "SHA-1": hashlib.sha1(encoded).hexdigest(),
            "SHA-256": hashlib.sha256(encoded).hexdigest(),
            "SHA-512": hashlib.sha512(encoded).hexdigest(),
            "SHA3-256": hashlib.sha3_256(encoded).hexdigest(),
            "BLAKE2b": hashlib.blake2b(encoded).hexdigest(),
        }
    except Exception as e:
        return f"Hash generation failed: {e}"


async def hash_identify(hash_value: str) -> dict | str:
    length = len(hash_value)
    possible = HASH_LENGTH_MAP.get(length, ["Unknown — no match for this length"])
    return {"hash": hash_value, "length": length, "possible_types": possible}
