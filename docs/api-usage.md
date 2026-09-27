# JEV Decisions API — Usage Guide

> Use TypeSafe JEV through SyncfusionCodeStudio with HMAC API-key authentication.

## Overview

The JEV Decisions API evaluates application state and returns typed answers with probabilities rather than generated text. It supports three primitives:

| Primitive | Purpose | Main result |
|---|---|---|
| `noul` | Evaluate whether a condition is true | Probability from `0` to `1` |
| `choice` | Select one option | Choice, option probabilities, and confidence |
| `score` | Place state on an ordered scale | Weighted score, probabilities, legend, and confidence |

JEV is not a chat-completion API. Send `state` and one or more typed `questions`.

## Endpoints

Use the recommended REST route:

| Method | Route | Description |
|---|---|---|
| POST | `/v1/decisions` | Evaluate state with one or more typed JEV questions |

## Create an API key

An organization administrator creates a key through `POST /v1/apikeys`:

```json
{
  "name": "JEV Automation",
  "scopes": ["jev:invoke"],
  "rateLimitPerMinute": 120,
  "expirationDays": 30
}
```

The response includes:

```json
{
  "result": {
    "clientId": "key_0123456789abcdef",
    "rawSecret": "base64url-secret-shown-once",
    "scopes": ["jev:invoke"]
  }
}
```

Store both values immediately. The raw secret is returned only when the key is created or rotated.

### Supported scopes

| Scope | JEV access | Other LLM access | Recommendation |
|---|---:|---:|---|
| `jev:invoke` | Yes | No | Preferred for JEV-only automation |
| `llm:invoke` | Yes | Yes | Backward-compatible general LLM key |
| `admin:*` | Yes | Yes | Avoid for automation |

Unrelated scopes such as `users:read` and `proxy:invoke` cannot call JEV.

## HMAC authentication

Every API-key request requires:

```text
X-Api-Key-Id: <clientId>
X-Api-Timestamp: <current ISO-8601 UTC timestamp>
X-Api-Signature: <base64url HMAC-SHA256 signature>
Content-Type: application/json
```

The timestamp must be within five minutes of server time. When Redis replay protection is enabled, a signature cannot be reused.

### Canonical message

Build the canonical message from five newline-separated values:

```text
UPPERCASE_HTTP_METHOD
lowercase_request_path
alphabetically_sorted_query_string_or_empty
timestamp
lowercase_sha256_hex_of_exact_body_bytes
```

For `POST /v1/decisions` with no query parameters:

```text
POST
/v1/decisions

2026-09-27T10:00:00.000000Z
<body-sha256-hex>
```

The blank third line is required because the query string is empty.

Compute:

$$
\text{signature} = \operatorname{Base64Url}\left(\operatorname{HMAC\text{-}SHA256}(\text{rawSecret}, \text{canonicalMessage})\right)
$$

The returned `rawSecret` is base64url-encoded. Decode it before using it as the HMAC key.

> Serialize the request exactly once. Hash and send the same bytes. Reformatting or re-serializing JSON after signing causes authentication to fail.

## Request format

Required fields:

| Field | Type | Description |
|---|---|---|
| `model` | string | A JEV model identifier |
| `state` | string, object, or array | Data to evaluate |
| `questions` | object | One or more named typed questions |

Optional fields include `session_id`, `user`, `provider`, and `trace`.

Accepted model identifiers include:

- `~typesafe/jev-latest`
- `typesafe/jev-1.13`
- `jev-latest` — normalized to `~typesafe/jev-latest`
- `jev-1.13` — normalized to `typesafe/jev-1.13`

### Noul

```json
{
  "model": "~typesafe/jev-latest",
  "state": "The checkout button does nothing when clicked.",
  "questions": {
    "is_bug": {
      "type": "noul",
      "instructions": "Is this a software defect?",
      "criteria": {
        "true": "The state describes broken software behavior.",
        "false": "The state does not describe broken software behavior."
      }
    }
  }
}
```

Example answer:

```json
{
  "type": "noul",
  "noul": 0.96
}
```

### Choice

```json
{
  "model": "~typesafe/jev-latest",
  "state": "I was charged twice for my subscription.",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this request?",
      "criteria": {
        "billing": "Charges, subscriptions, invoices, and refunds.",
        "technical": "Product bugs, outages, and integrations.",
        "account": "Login, permissions, and profile settings."
      }
    }
  }
}
```

Example answer:

```json
{
  "type": "choice",
  "choice": "billing",
  "probabilities": {
    "billing": 1,
    "technical": 0,
    "account": 0
  },
  "confidence": 1
}
```

### Score

```json
{
  "model": "~typesafe/jev-latest",
  "state": "Payment processing is down for every customer and revenue is blocked.",
  "questions": {
    "urgency": {
      "type": "score",
      "instructions": "How urgent is this incident?",
      "criteria": [
        "Can wait until the next release",
        "Should be fixed this week",
        "Production emergency blocking revenue"
      ]
    }
  }
}
```

Example answer:

```json
{
  "type": "score",
  "score": 2,
  "legend": {
    "0": "Can wait until the next release",
    "1": "Should be fixed this week",
    "2": "Production emergency blocking revenue"
  },
  "probabilities": {
    "0": 0,
    "1": 0,
    "2": 1
  },
  "confidence": 1
}
```

## Complete response

```json
{
  "model": "typesafe/jev-1.13-20260917",
  "answers": {
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
    "input_tokens": 304,
    "output_tokens": 18,
    "cost": 0.000012768
  },
  "id": "gen-dec-...",
  "provider": "TypeSafe"
}
```

The response also carries `x-request-id` and `x-model-name` headers.

## SDK quick start

The repository contains dependency-free local SDK packages that handle JSON serialization, timestamp generation, body hashing, HMAC signing, timeout handling, and structured API errors.

For installation, configuration, error handling, and complete examples, see the [SDK Getting Started guide](jev-sdk-getting-started.md).

### TypeScript SDK

Install from this repository:

```bash
npm install ./sdk/typescript
```

```typescript
import { JevClient } from "@syncfusion/codestudio-jev";

const jev = JevClient.fromEnv();
const result = await jev.decide({
  state: { incident: "Payments are unavailable" },
  questions: {
    urgency: {
      type: "score",
      instructions: "How urgent is this incident?",
      criteria: ["Low", "Medium", "Critical"],
    },
  },
});

console.log(result.answers.urgency);
```

Package documentation: [`sdk/typescript/README.md`](../sdk/typescript/README.md).

### Python SDK

Install from this repository:

```bash
python3 -m pip install ./sdk/python
```

```python
from codestudio_jev import JevClient

jev = JevClient.from_env()
result = jev.decide(
    state={"incident": "Payments are unavailable"},
    questions={
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this incident?",
            "criteria": ["Low", "Medium", "Critical"],
        }
    },
)

print(result.answers["urgency"])
```

Package documentation: [`sdk/python/README.md`](../sdk/python/README.md).

Both SDKs read:

```text
CODESTUDIO_BASE_URL
CODESTUDIO_API_KEY_ID
CODESTUDIO_API_KEY_SECRET
```

## Python script

The runnable example is available at [`examples/jev/jev_decisions.py`](../examples/jev/jev_decisions.py).

Set credentials and run:

```bash
export CODESTUDIO_BASE_URL="http://localhost:5142"
export CODESTUDIO_API_KEY_ID="key_..."
export CODESTUDIO_API_KEY_SECRET="..."
python3 -m pip install ./sdk/python
python3 examples/jev/jev_decisions.py
```

The SDK uses only the Python standard library at runtime.

## TypeScript script

The runnable example is available at [`examples/jev/jev-decisions.ts`](../examples/jev/jev-decisions.ts).

Requirements: Node.js 22+ and a TypeScript runner such as `tsx`.

```bash
export CODESTUDIO_BASE_URL="http://localhost:5142"
export CODESTUDIO_API_KEY_ID="key_..."
export CODESTUDIO_API_KEY_SECRET="..."
cd sdk/typescript && npm install && npm run build && cd ../..
npm install ./sdk/typescript
npx tsx examples/jev/jev-decisions.ts
```

The script uses Node's built-in `crypto` and `fetch` APIs.

## Error responses

Errors follow this shape:

```json
{
  "error": {
    "code": 400,
    "message": "The required 'state' field must be a string, object, or array."
  }
}
```

| Status | Meaning |
|---:|---|
| 400 | Invalid JSON or JEV request |
| 401 | Missing, invalid, expired, or replayed HMAC authentication |
| 402 | Subscription or credit restriction |
| 403 | API key lacks `jev:invoke`, `llm:invoke`, or `admin:*` |
| 413 | Request exceeds 10 MB |
| 429 | API-key, gateway, or organization rate limit reached |
| 502 | Invalid/unavailable upstream provider response |
| 503 | JEV not configured or circuit temporarily open |
| 504 | Upstream request timeout |

## Security guidance

- Never commit `clientId` and `rawSecret` to source control.
- Use CI/CD secret stores, environment injection, or a platform secret manager.
- Prefer `jev:invoke` over `llm:invoke` for least privilege.
- Set an expiration and the lowest practical rate limit.
- Rotate keys periodically and revoke unused keys.
- Never log the raw secret, canonical message, or authorization headers.
- Treat repository scripts and cloud sandboxes as untrusted. Do not inject long-lived organization keys into an untrusted sandbox; use a trusted broker or short-lived run-scoped credential.
- Ensure clients synchronize system time because timestamps outside the five-minute window are rejected.

## Troubleshooting

### HTTP 401: invalid signature

Check that:

1. The secret is base64url-decoded before HMAC computation.
2. The request path in the canonical message exactly matches the called route.
3. The query line is present even when empty.
4. The body hash uses the exact bytes sent over HTTP.
5. The signature is unpadded base64url.
6. The timestamp is current UTC ISO-8601.

### HTTP 401 on a repeated request

Generate a new timestamp and signature. Redis replay protection rejects reused signatures.

### HTTP 403

Create or rotate a key containing `jev:invoke`, `llm:invoke`, or `admin:*`. Prefer `jev:invoke`.

### HTTP 429

The effective limit can be constrained by both the API-key rate limit and gateway rate limiting. Reduce request frequency or ask an administrator to adjust the key limit.
