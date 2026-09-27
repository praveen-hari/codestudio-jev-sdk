# Python SDK reference

Distribution: `syncfusion-codestudio-jev`

Import package: `codestudio_jev`

Requires Python 3.11 or newer.

## Install

```bash
python3 -m pip install ./python
```

## `JevClient`

### Constructor

```python
JevClient(
    *,
    base_url: str,
    client_id: str,
    secret: str,
    timeout: float = 45.0,
)
```

| Argument | Required | Default | Description |
|---|---:|---|---|
| `base_url` | Yes | — | Enterprise API origin without `/v1/decisions`. HTTPS required outside localhost. |
| `client_id` | Yes | — | HMAC API key client ID. |
| `secret` | Yes | — | Base64url-encoded 32-byte API secret. |
| `timeout` | No | `45.0` | Request timeout in seconds. |

```python
import os
from codestudio_jev import JevClient

client = JevClient(
    base_url="https://api.sfcodestudio.com",
    client_id=os.environ["CODESTUDIO_API_KEY_ID"],
    secret=os.environ["CODESTUDIO_API_KEY_SECRET"],
    timeout=30.0,
)
```

### `JevClient.from_env()`

```python
JevClient.from_env() -> JevClient
```

Reads:

- `CODESTUDIO_BASE_URL`, default `http://localhost:5142`
- `CODESTUDIO_API_KEY_ID`, required
- `CODESTUDIO_API_KEY_SECRET`, required

```python
client = JevClient.from_env()
```

### `client.decide()`

```python
client.decide(
    *,
    state: State,
    questions: Mapping[str, Question],
    model: str = "~typesafe/jev-latest",
    session_id: str | None = None,
    user: str | None = None,
    provider: Mapping[str, Any] | None = None,
    trace: Mapping[str, Any] | None = None,
) -> DecisionResponse
```

```python
result = client.decide(
    state={"command": "pytest", "exit_code": 1},
    questions={
        "failure_type": {
            "type": "choice",
            "instructions": "Classify the primary failure cause.",
            "criteria": {
                "code_defect": "Implementation or test is incorrect.",
                "environment": "Infrastructure or setup failed.",
                "transient": "Retrying unchanged is likely to succeed.",
                "unknown": "Evidence is insufficient.",
            },
        }
    },
)
```

## Request types

The SDK exports `NoulQuestion`, `ChoiceQuestion`, `ScoreQuestion`, and `Question` TypedDict definitions.

```python
questions = {
    "is_incident": {
        "type": "noul",
        "instructions": "Is this a production incident?",
    },
    "owner": {
        "type": "choice",
        "instructions": "Which team should respond?",
        "criteria": {
            "payments": "Payment failure.",
            "frontend": "Rendering failure.",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is this?",
        "criteria": ["Low", "Medium", "Critical"],
    },
}
```

## `DecisionResponse`

```python
@dataclass(frozen=True, slots=True)
class DecisionResponse:
    model: str
    answers: Mapping[str, Mapping[str, Any]]
    usage: Mapping[str, int | float]
    id: str | None = None
    provider: str | None = None
```

```python
answer = result.answers["failure_type"]
if answer["type"] == "choice":
    print(answer["choice"])
```

## Errors

### `JevConfigurationError`

Raised before an HTTP call for invalid client configuration or request input.

Examples:

- Missing base URL, client ID, or secret
- Non-positive timeout
- HTTP remote URL
- Empty questions
- Missing instructions or criteria

### `JevApiError`

Attributes:

| Attribute | Type | Description |
|---|---|---|
| `status` | integer | HTTP status; `0` for a network error |
| `code` | integer, string, or `None` | Structured API error code when available |
| `response_body` | any | Parsed error body or raw fallback content |

```python
from codestudio_jev import JevApiError

try:
    client.decide(state=state, questions=questions)
except JevApiError as error:
    print(error.status, error.code, str(error))
```

## Signing helpers

Advanced callers can import:

```python
from codestudio_jev import build_canonical_message, sign_headers
```

Most applications should use `JevClient`, which guarantees that the signed bytes are the bytes sent over HTTP.
