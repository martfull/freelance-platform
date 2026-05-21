import hashlib
import json
from pathlib import Path
from typing import Any


HASH_CHUNK_SIZE_BYTES = 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = HASH_CHUNK_SIZE_BYTES) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return canonical.encode("utf-8")


def sha256_payload(payload: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(payload))
