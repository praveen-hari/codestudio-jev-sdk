from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from codestudio_jev import (
    JevApiError,
    JevClient,
    JevConfigurationError,
    build_canonical_message,
)


class FakeResponse:
    def __init__(self, body: dict[str, object]) -> None:
        self._body = json.dumps(body).encode()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class JevClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.secret_bytes = bytes(range(32))
        self.secret = base64.urlsafe_b64encode(self.secret_bytes).rstrip(b"=").decode()

    @patch("codestudio_jev.client.urlopen")
    def test_decide_signs_exact_body(self, urlopen_mock: object) -> None:
        captured_request = None

        def respond(request: object, **_: object) -> FakeResponse:
            nonlocal captured_request
            captured_request = request
            return FakeResponse({
                "model": "typesafe/jev-1.13",
                "answers": {"safe": {"type": "noul", "noul": 0.9}},
                "usage": {"input_tokens": 10, "output_tokens": 1, "cost": 0.000001},
            })

        urlopen_mock.side_effect = respond
        client = JevClient(
            base_url="http://localhost:5142",
            client_id="key_test",
            secret=self.secret,
        )
        result = client.decide(
            state="hello",
            questions={"safe": {"type": "noul", "instructions": "Safe?"}},
        )

        self.assertEqual(result.model, "typesafe/jev-1.13")
        self.assertIsNotNone(captured_request)
        request = captured_request
        body = request.data
        timestamp = request.headers["X-api-timestamp"]
        canonical = build_canonical_message("POST", "/v1/decisions", "", timestamp, body)
        expected = base64.urlsafe_b64encode(
            hmac.new(self.secret_bytes, canonical, hashlib.sha256).digest()
        ).rstrip(b"=").decode()
        self.assertEqual(request.headers["X-api-signature"], expected)
        self.assertIn(b'"model":"~typesafe/jev-latest"', body)

    def test_rejects_insecure_remote_base_url(self) -> None:
        with self.assertRaisesRegex(JevConfigurationError, "must use HTTPS"):
            JevClient(
                base_url="http://enterprise.example.com",
                client_id="key_test",
                secret=self.secret,
            )

    @patch("codestudio_jev.client.urlopen")
    def test_invalid_success_response_raises_api_error(self, urlopen_mock: object) -> None:
        urlopen_mock.return_value = FakeResponse({"model": "typesafe/jev-1.13"})
        client = JevClient(
            base_url="https://enterprise.example.com",
            client_id="key_test",
            secret=self.secret,
        )
        with self.assertRaises(JevApiError) as raised:
            client.decide(
                state="hello",
                questions={"safe": {"type": "noul", "instructions": "Safe?"}},
            )
        self.assertEqual(raised.exception.status, 502)


if __name__ == "__main__":
    unittest.main()
