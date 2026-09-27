# @syncfusion/codestudio-jev

Dependency-free Node.js SDK for the SyncfusionCodeStudio JEV Decisions API.

## Install locally

```bash
npm install ./sdk/typescript
```

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
