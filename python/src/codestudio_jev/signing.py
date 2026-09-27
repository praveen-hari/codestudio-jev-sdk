"""HMAC request signing compatible with SyncfusionCodeStudio API keys."""

from __future__ import annotations

import base64
import hashlib
import hmac
from urllib.parse import parse_qsl

from .errors import JevConfigurationError


def build_canonical_message(
    method: str,
    path: str,
    query_string: str,
    timestamp: str,
    body: bytes,
) -> bytes:
    body_hash = hashlib.sha256(body).hexdigest()
    sorted_query = _sort_query_string(query_string)
    return "\n".join(
        [method.upper(), path.lower(), sorted_query, timestamp, body_hash]
    ).encode("utf-8")


def sign_headers(
    client_id: str,
    encoded_secret: str,
    method: str,
    path: str,
    query_string: str,
    timestamp: str,
    body: bytes,
) -> dict[str, str]:
    if not client_id.strip():
        raise JevConfigurationError("client_id is required")

    secret = _decode_base64url(encoded_secret)
    if len(secret) != 32:
        raise JevConfigurationError("secret must decode to exactly 32 bytes")

    canonical = build_canonical_message(
        method, path, query_string, timestamp, body
    )
    signature = base64.urlsafe_b64encode(
        hmac.new(secret, canonical, hashlib.sha256).digest()
    ).rstrip(b"=").decode("ascii")
    return {
        "X-Api-Key-Id": client_id,
        "X-Api-Timestamp": timestamp,
        "X-Api-Signature": signature,
    }


def _decode_base64url(value: str) -> bytes:
    try:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
    except (ValueError, base64.binascii.Error) as error:
        raise JevConfigurationError("secret must be valid base64url") from error


def _sort_query_string(query_string: str) -> str:
    query = query_string.removeprefix("?")
    if not query:
        return ""
    return "&".join(
        f"{key}={value}" for key, value in sorted(parse_qsl(query, keep_blank_values=True))
    )
