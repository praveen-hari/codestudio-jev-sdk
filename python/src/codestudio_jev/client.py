"""Synchronous JEV Decisions API client."""

from __future__ import annotations

import json
import os
import ssl
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .errors import JevApiError, JevConfigurationError
from .models import DecisionResponse, Question, State
from .signing import sign_headers

_DECISIONS_PATH = "/v1/decisions"
_DEFAULT_MODEL = "~typesafe/jev-latest"


class JevClient:
    """Dependency-free synchronous client with automatic HMAC signing."""

    def __init__(
        self,
        *,
        base_url: str,
        client_id: str,
        secret: str,
        timeout: float = 45.0,
    ) -> None:
        parsed_url = urlparse(base_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise JevConfigurationError("base_url must be an absolute URL")
        if parsed_url.scheme != "https" and parsed_url.hostname not in {"localhost", "127.0.0.1"}:
            raise JevConfigurationError("base_url must use HTTPS except for localhost development")
        if not client_id.strip():
            raise JevConfigurationError("client_id is required")
        if not secret.strip():
            raise JevConfigurationError("secret is required")
        if timeout <= 0:
            raise JevConfigurationError("timeout must be positive")

        self._base_url = base_url.rstrip("/")
        self._client_id = client_id
        self._secret = secret
        self._timeout = timeout

    @classmethod
    def from_env(cls) -> "JevClient":
        client_id = os.environ.get("CODESTUDIO_API_KEY_ID")
        secret = os.environ.get("CODESTUDIO_API_KEY_SECRET")
        if not client_id:
            raise JevConfigurationError("CODESTUDIO_API_KEY_ID is required")
        if not secret:
            raise JevConfigurationError("CODESTUDIO_API_KEY_SECRET is required")
        return cls(
            base_url=os.environ.get("CODESTUDIO_BASE_URL", "http://localhost:5142"),
            client_id=client_id,
            secret=secret,
        )

    def decide(
        self,
        *,
        state: State,
        questions: Mapping[str, Question],
        model: str = _DEFAULT_MODEL,
        session_id: str | None = None,
        user: str | None = None,
        provider: Mapping[str, Any] | None = None,
        trace: Mapping[str, Any] | None = None,
    ) -> DecisionResponse:
        self._validate_request(state, questions)
        payload: dict[str, Any] = {
            "model": model,
            "state": state,
            "questions": questions,
        }
        for key, value in {
            "session_id": session_id,
            "user": user,
            "provider": provider,
            "trace": trace,
        }.items():
            if value is not None:
                payload[key] = value

        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        authentication = sign_headers(
            self._client_id,
            self._secret,
            "POST",
            _DECISIONS_PATH,
            "",
            timestamp,
            body,
        )
        request = Request(
            f"{self._base_url}{_DECISIONS_PATH}",
            data=body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "codestudio-jev-python/0.1.0",
                **authentication,
            },
        )

        try:
            with urlopen(request, timeout=self._timeout, context=ssl.create_default_context()) as response:
                return self._parse_success(response.read())
        except HTTPError as error:
            response_body = error.read()
            parsed = self._parse_json(response_body)
            error_data = parsed.get("error", {}) if isinstance(parsed, dict) else {}
            message = error_data.get("message") if isinstance(error_data, dict) else None
            code = error_data.get("code") if isinstance(error_data, dict) else None
            raise JevApiError(
                error.code,
                message if isinstance(message, str) else f"JEV request failed with HTTP {error.code}",
                code=code if isinstance(code, (int, str)) else None,
                response_body=parsed if parsed is not None else response_body.decode("utf-8", errors="replace"),
            ) from error
        except URLError as error:
            raise JevApiError(0, f"JEV request failed: {error.reason}") from error

    @staticmethod
    def _validate_request(state: State, questions: Mapping[str, Question]) -> None:
        if state is None:
            raise JevConfigurationError("state is required")
        if not questions:
            raise JevConfigurationError("at least one question is required")
        for name, question in questions.items():
            if not name.strip():
                raise JevConfigurationError("question names cannot be empty")
            if not question.get("instructions"):
                raise JevConfigurationError(f"question '{name}' requires instructions")
            if question.get("type") in {"choice", "score"} and not question.get("criteria"):
                raise JevConfigurationError(f"question '{name}' requires criteria")

    @classmethod
    def _parse_success(cls, body: bytes) -> DecisionResponse:
        parsed = cls._parse_json(body)
        if not isinstance(parsed, Mapping):
            raise JevApiError(502, "JEV returned an invalid response", response_body=parsed)
        try:
            return DecisionResponse.from_dict(parsed)
        except ValueError as error:
            raise JevApiError(502, str(error), response_body=parsed) from error

    @staticmethod
    def _parse_json(body: bytes) -> Any:
        try:
            return json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
