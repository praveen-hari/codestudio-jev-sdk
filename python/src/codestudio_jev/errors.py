"""SDK exceptions."""

from __future__ import annotations

from typing import Any


class JevError(Exception):
    """Base SDK error."""


class JevConfigurationError(JevError):
    """Invalid SDK configuration or request input."""


class JevApiError(JevError):
    """A non-success response from the JEV API."""

    def __init__(
        self,
        status: int,
        message: str,
        *,
        code: int | str | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.response_body = response_body
