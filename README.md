# CodeStudio JEV SDK

TypeScript and Python clients for calling the CodeStudio JEV Decisions API with automatic HMAC authentication.

Both SDKs call the recommended endpoint:

```text
POST /v1/decisions
```

## Features

- Noul, Choice, and Score primitives
- Automatic request-body hashing and HMAC-SHA256 signing
- Typed TypeScript requests and responses
- Python response dataclass and typed request definitions
- Structured API and configuration errors
- HTTPS enforcement outside localhost
- No runtime dependencies

## Repository layout

```text
typescript/   TypeScript package: @syncfusion/codestudio-jev
python/       Python package: syncfusion-codestudio-jev
examples/     TypeScript and Python examples
docs/         Getting-started and API usage guides
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

Install the released package (see [Releases](https://github.com/praveen-hari/codestudio-jev-sdk/releases)):

```bash
npm install https://github.com/praveen-hari/codestudio-jev-sdk/releases/download/v0.1.0/syncfusion-codestudio-jev-0.1.0.tgz
```

Or the local package from another project:

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
