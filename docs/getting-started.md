# CodeStudio JEV SDK — Getting Started

Use the TypeScript or Python SDK to call the CodeStudio JEV Decisions API without implementing HMAC signing manually.

Both SDKs call only the recommended endpoint:

```text
POST /v1/decisions
```

## Prerequisites

You need:

- A running CodeStudio Enterprise API
- An API key ID and secret
- One of these API-key scopes:
  - `jev:invoke` — recommended for JEV-only access
  - `llm:invoke` — general LLM access, including JEV
  - `admin:*` — supported but not recommended for automation
- Node.js 22+ for TypeScript, or Python 3.11+ for Python

## 1. Create an API key

An organization administrator creates the key through:

```text
POST /v1/apikeys
```

Request:

```json
{
  "name": "JEV SDK",
  "scopes": ["jev:invoke"],
  "rateLimitPerMinute": 120,
  "expirationDays": 30
}
```

Save the returned values immediately:

```json
{
  "result": {
    "clientId": "key_0123456789abcdef",
    "rawSecret": "base64url-secret-shown-once"
  }
}
```

The raw secret is displayed only when the key is created or rotated.

## 2. Configure credentials

Both SDKs use the same environment variables:

```bash
export CODESTUDIO_BASE_URL="http://localhost:5142"
export CODESTUDIO_API_KEY_ID="key_0123456789abcdef"
export CODESTUDIO_API_KEY_SECRET="base64url-secret-shown-once"
```

Use an HTTPS URL outside local development:

```bash
export CODESTUDIO_BASE_URL="https://enterprise.example.com"
```

Do not commit these values to source control.

---

# TypeScript SDK

## Install

From this repository:

```bash
cd sdk/typescript
npm install
npm run build
cd ../..
npm install ./sdk/typescript
```

The package name is:

```text
@syncfusion/codestudio-jev
```

## First decision

```typescript
import { JevClient } from "@syncfusion/codestudio-jev";

const jev = JevClient.fromEnv();

const result = await jev.decide({
  state: {
    service: "checkout",
    impact: "Payment processing is unavailable for every customer.",
  },
  questions: {
    urgency: {
      type: "score",
      instructions: "How urgent is this incident?",
      criteria: ["Low", "Medium", "Critical"],
    },
  },
});

console.log(result.answers.urgency);
console.log(result.usage);
```

## Explicit configuration

Use explicit configuration instead of environment variables when credentials come from a secret manager:

```typescript
import { JevClient } from "@syncfusion/codestudio-jev";

const jev = new JevClient({
  baseUrl: "https://enterprise.example.com",
  clientId: process.env.MY_JEV_KEY_ID!,
  secret: process.env.MY_JEV_KEY_SECRET!,
  timeoutMs: 30_000,
});
```

## Cancellation

```typescript
const controller = new AbortController();

const result = await jev.decide(
  {
    state: "Payment processing is unavailable.",
    questions: {
      incident: {
        type: "noul",
        instructions: "Is this a production incident?",
      },
    },
  },
  { signal: controller.signal },
);
```

## Error handling

```typescript
import {
  JevApiError,
  JevClient,
  JevConfigurationError,
} from "@syncfusion/codestudio-jev";

try {
  const result = await JevClient.fromEnv().decide({
    state: "Payment processing is unavailable.",
    questions: {
      incident: {
        type: "noul",
        instructions: "Is this a production incident?",
      },
    },
  });

  console.log(result.answers);
} catch (error) {
  if (error instanceof JevApiError) {
    console.error(`JEV API failed: HTTP ${error.status}`, error.message);
  } else if (error instanceof JevConfigurationError) {
    console.error("Invalid JEV SDK configuration:", error.message);
  } else {
    throw error;
  }
}
```

## Run the repository example

```bash
npx tsx examples/jev/jev-decisions.ts
```

---

# Python SDK

## Install

From this repository:

```bash
python3 -m pip install ./sdk/python
```

The distribution name is:

```text
syncfusion-codestudio-jev
```

The import package is:

```text
codestudio_jev
```

## First decision

```python
from codestudio_jev import JevClient

jev = JevClient.from_env()

result = jev.decide(
    state={
        "service": "checkout",
        "impact": "Payment processing is unavailable for every customer.",
    },
    questions={
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this incident?",
            "criteria": ["Low", "Medium", "Critical"],
        }
    },
)

print(result.answers["urgency"])
print(result.usage)
```

## Explicit configuration

```python
import os

from codestudio_jev import JevClient

jev = JevClient(
    base_url="https://enterprise.example.com",
    client_id=os.environ["MY_JEV_KEY_ID"],
    secret=os.environ["MY_JEV_KEY_SECRET"],
    timeout=30.0,
)
```

## Error handling

```python
from codestudio_jev import JevApiError, JevClient, JevConfigurationError

try:
    result = JevClient.from_env().decide(
        state="Payment processing is unavailable.",
        questions={
            "incident": {
                "type": "noul",
                "instructions": "Is this a production incident?",
            }
        },
    )
    print(result.answers)
except JevApiError as error:
    print(f"JEV API failed: HTTP {error.status}: {error}")
except JevConfigurationError as error:
    print(f"Invalid JEV SDK configuration: {error}")
```

## Run the repository example

```bash
python3 examples/jev/jev_decisions.py
```

---

# Decision primitives

## Noul

Use Noul for a yes/no condition. The result is a probability from `0` to `1`.

```typescript
const result = await jev.decide({
  state: "The checkout button does nothing.",
  questions: {
    is_bug: {
      type: "noul",
      instructions: "Is this a software defect?",
      criteria: {
        true: "The state describes broken software behavior.",
        false: "The state does not describe broken software behavior.",
      },
    },
  },
});
```

Typical answer:

```json
{
  "type": "noul",
  "noul": 0.96
}
```

## Choice

Use Choice to select one option.

```python
result = jev.decide(
    state="I was charged twice for my subscription.",
    questions={
        "department": {
            "type": "choice",
            "instructions": "Which team should handle this request?",
            "criteria": {
                "billing": "Charges, subscriptions, invoices, and refunds.",
                "technical": "Product bugs, outages, and integrations.",
                "account": "Login, permissions, and profile settings.",
            },
        }
    },
)
```

Typical answer:

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

## Score

Use Score to place state on an ordered scale.

```typescript
const result = await jev.decide({
  state: "Payment processing is unavailable for every customer.",
  questions: {
    urgency: {
      type: "score",
      instructions: "How urgent is this incident?",
      criteria: ["Low", "Medium", "Critical"],
    },
  },
});
```

Typical answer:

```json
{
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
```

# Multiple questions

JEV can answer independent questions about the same state in one request:

```typescript
const result = await jev.decide({
  state: {
    service: "checkout",
    impact: "Payments are unavailable for all customers.",
  },
  questions: {
    is_incident: {
      type: "noul",
      instructions: "Is this a production incident?",
    },
    owner: {
      type: "choice",
      instructions: "Which team should respond?",
      criteria: {
        payments: "Payment or checkout failure.",
        frontend: "Rendering or browser failure.",
      },
    },
    urgency: {
      type: "score",
      instructions: "How urgent is this?",
      criteria: ["Low", "Medium", "Critical"],
    },
  },
});
```

# Default behavior

The SDKs:

- Call only `POST /v1/decisions`
- Default to `~typesafe/jev-latest`
- Serialize the payload once
- Hash and sign the exact transmitted body
- Generate the current UTC timestamp
- Add all required HMAC headers
- Use a 45-second default timeout
- Reject non-HTTPS remote base URLs
- Allow HTTP only for `localhost` and `127.0.0.1`
- Never log credentials or signatures

# Common errors

| Error | Likely cause | Resolution |
|---|---|---|
| HTTP 401 | Invalid signature, expired timestamp, revoked key, or replay | Verify key values and generate a fresh request |
| HTTP 403 | Key lacks JEV permission | Add `jev:invoke` or `llm:invoke` |
| HTTP 429 | API-key or gateway limit reached | Reduce request rate or adjust the key limit |
| HTTP 502 | Invalid/unavailable upstream response | Retry later after checking provider status |
| HTTP 503 | JEV configuration missing or circuit open | Verify server configuration |
| HTTP 504 | Provider timeout | Retry according to application policy |

# Security recommendations

- Use `jev:invoke` for least privilege.
- Store credentials in a secret manager or protected environment variables.
- Never commit credentials to a repository.
- Use HTTPS outside localhost.
- Set short expiration periods for automation keys.
- Rotate and revoke unused keys.
- Do not inject long-lived organization keys into untrusted sandboxes.
- For untrusted execution, use a trusted broker or short-lived run-scoped credential.

# Further reading

- [JEV Decisions API usage guide](jev-decisions-api-usage.md)
- [TypeScript SDK README](../sdk/typescript/README.md)
- [Python SDK README](../sdk/python/README.md)
