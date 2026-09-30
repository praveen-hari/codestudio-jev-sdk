# CodeStudio JEV SDK

TypeScript and Python clients for calling the CodeStudio JEV Decisions API with automatic HMAC authentication.

Both SDKs call the recommended endpoint:

```text
POST /v1/decisions
```

## Contents

- [Features](#features) · [Primitives](#primitives) · [Repository layout](#repository-layout) · [Credentials](#credentials)
- [TypeScript](#typescript) · [Python](#python) · [Error handling](#error-handling) · [Examples](#examples)
- [Documentation](#documentation) · [Security](#security) · [License](#license)

## Features

- Noul, Choice, and Score primitives
- Automatic request-body hashing and HMAC-SHA256 signing
- Typed TypeScript requests and responses
- Python response dataclass and typed request definitions
- Structured API and configuration errors
- HTTPS enforcement outside localhost
- No runtime dependencies

## Primitives

| Type | Purpose | `criteria` |
| --- | --- | --- |
| `noul` | Yes/no style question about the state | not used |
| `choice` | Pick one option | map of option name to description |
| `score` | Rate on a scale | list of scale labels, e.g. `["Low", "Medium", "Critical"]` |

## Repository layout

```text
typescript/   TypeScript package: @syncfusion/codestudio-jev
python/       Python package: syncfusion-codestudio-jev
examples/     TypeScript and Python examples
docs/         MkDocs site sources (guides, API reference, troubleshooting)
```

## Credentials

Ask an organization administrator to create an API key from the CodeStudio Enterprise **API Keys** page with the least-privilege `jev:invoke` scope. After the administrator securely provides the client ID and one-time secret, set:

```bash
export CODESTUDIO_BASE_URL="https://enterprise.example.com"
export CODESTUDIO_API_KEY_ID="key_..."
export CODESTUDIO_API_KEY_SECRET="..."
```

Never commit credentials to source control.

## TypeScript

```bash
cd typescript
npm install
npm test
npm run build
```

Install the local package from another project:

```bash
npm install /path/to/codestudio-jev-sdk/typescript
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
```

## Python

```bash
python3 -m pip install ./python
python3 -m unittest discover -s python/tests -v
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
```

## Error handling

Both clients raise structured errors for configuration problems (missing credentials, non-HTTPS base URL) and for API error responses. See the [troubleshooting guide](docs/troubleshooting.md) for details.

## Examples

Runnable examples covering all three primitives:

- [`examples/jev-decisions.ts`](examples/jev-decisions.ts)
- [`examples/jev_decisions.py`](examples/jev_decisions.py)

## Documentation

- [Documentation site](https://praveen-hari.github.io/codestudio-jev-sdk/)
- [Getting started](docs/getting-started.md)
- [JEV Decisions API usage](docs/api-usage.md)

Build the MkDocs site locally:

```bash
python3 -m pip install -r requirements-docs.txt
mkdocs serve
```

## Security

Use `jev:invoke` for least privilege. Store API credentials in a secret manager or protected environment variables. Do not inject long-lived organization keys into untrusted sandboxes.

## License

MIT
