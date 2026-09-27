# REST API overview

The JEV Decisions API evaluates structured state against one or more typed questions.

## Endpoint

```http
POST /v1/decisions
Content-Type: application/json
```

Production base URL:

```text
https://api.sfcodestudio.com
```

Complete production URL:

```text
https://api.sfcodestudio.com/v1/decisions
```

## Authentication

API-key calls use HMAC-SHA256 request signing:

```text
X-Api-Key-Id: <client ID>
X-Api-Timestamp: <current ISO-8601 UTC timestamp>
X-Api-Signature: <base64url signature>
```

Use an API key with one of these scopes:

| Scope | Access |
|---|---|
| `jev:invoke` | JEV-only access; recommended |
| `llm:invoke` | General LLM access, including JEV |
| `admin:*` | Administrative access; avoid for automation |

See [Authentication and security](../guides/authentication.md) for the signing contract.

## Request

```json
{
  "model": "~typesafe/jev-latest",
  "state": {
    "service": "checkout",
    "impact": "Payments are unavailable for all customers."
  },
  "questions": {
    "is_incident": {
      "type": "noul",
      "instructions": "Is this a production incident?"
    },
    "owner": {
      "type": "choice",
      "instructions": "Which team should respond?",
      "criteria": {
        "payments": "Payment or checkout failure.",
        "frontend": "Rendering or browser failure."
      }
    },
    "urgency": {
      "type": "score",
      "instructions": "How urgent is this?",
      "criteria": ["Low", "Medium", "Critical"]
    }
  }
}
```

See [Request schema](request.md) for complete field definitions.

## Response

```json
{
  "id": "gen-dec-...",
  "model": "typesafe/jev-1.13-20260917",
  "provider": "TypeSafe",
  "answers": {
    "is_incident": {
      "type": "noul",
      "noul": 0.98
    },
    "owner": {
      "type": "choice",
      "choice": "payments",
      "probabilities": {
        "payments": 1,
        "frontend": 0
      },
      "confidence": 1
    },
    "urgency": {
      "type": "score",
      "score": 2,
      "legend": {
        "0": "Low",
        "1": "Medium",
        "2": "Critical"
      },
      "probabilities": {
        "0": 0,
        "1": 0,
        "2": 1
      },
      "confidence": 1
    }
  },
  "usage": {
    "input_tokens": 315,
    "output_tokens": 63,
    "cost": 0.00001323
  }
}
```

## Response headers

| Header | Description |
|---|---|
| `x-request-id` | CodeStudio request identifier for support and tracing |
| `x-model-name` | Resolved JEV model snapshot |

## Limits

- Request body: maximum 10 MB
- Questions: server-configured maximum, currently 100 by default
- `session_id`: maximum 256 characters
- `user`: maximum 256 characters
- Streaming: not supported
- Automatic retries: not performed by the service because requests are billable
