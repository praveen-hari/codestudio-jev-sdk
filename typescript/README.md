# @syncfusion/codestudio-jev

Dependency-free Node.js SDK for the SyncfusionCodeStudio JEV Decisions API.

## Install

From a GitHub Release (no registry or token needed):

```bash
npm install https://github.com/praveen-hari/codestudio-jev-sdk/releases/download/v0.1.0/syncfusion-codestudio-jev-0.1.0.tgz
```

From a local checkout:

```bash
npm install /path/to/codestudio-jev-sdk/typescript
```

To release a new version, bump `version` in `package.json`, then push a tag `vX.Y.Z` with the same
version: `.github/workflows/release-typescript.yml` builds, tests and attaches the package to the
release.

## Usage

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

Environment variables:

- `CODESTUDIO_BASE_URL`
- `CODESTUDIO_API_KEY_ID`
- `CODESTUDIO_API_KEY_SECRET`

Requires Node.js 22 or newer. The client calls only `POST /v1/decisions` and performs HMAC signing automatically.
