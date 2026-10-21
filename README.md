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

## Documentation

- [Documentation site](https://praveen-hari.github.io/codestudio-jev-sdk/)
- [Getting started](docs/getting-started.md)
- [JEV Decisions API usage](docs/api-usage.md)
- [SDK Reference](docs/sdk/index.md)
- [Guides and automation patterns](docs/guides/software-development.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Examples](examples/)

Build the MkDocs site locally:

```bash
python3 -m pip install -r requirements-docs.txt
mkdocs serve
```

## Security

Use `jev:invoke` for least privilege. Store API credentials in a secret manager or protected environment variables. Do not inject long-lived organization keys into untrusted sandboxes.

## License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2026 Praveen Hari

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
