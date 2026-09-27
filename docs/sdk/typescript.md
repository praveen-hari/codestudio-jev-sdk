# TypeScript SDK reference

Package: `@syncfusion/codestudio-jev`

Requires Node.js 22 or newer.

## Install

```bash
cd typescript
npm install
npm run build
```

From another local project:

```bash
npm install /path/to/codestudio-jev-sdk/typescript
```

## `JevClient`

### Constructor

```typescript
new JevClient(options: JevClientOptions)
```

```typescript
interface JevClientOptions {
  baseUrl: string;
  clientId: string;
  secret: string;
  timeoutMs?: number;
  fetch?: typeof globalThis.fetch;
}
```

| Option | Required | Default | Description |
|---|---:|---|---|
| `baseUrl` | Yes | — | Enterprise API origin without `/v1/decisions`. HTTPS required outside localhost. |
| `clientId` | Yes | — | HMAC API key client ID. |
| `secret` | Yes | — | Base64url-encoded 32-byte API secret. |
| `timeoutMs` | No | `45000` | Request timeout in milliseconds. |
| `fetch` | No | `globalThis.fetch` | Custom fetch implementation, useful for tests or instrumentation. |

```typescript
const client = new JevClient({
  baseUrl: "https://api.sfcodestudio.com",
  clientId: process.env.CODESTUDIO_API_KEY_ID!,
  secret: process.env.CODESTUDIO_API_KEY_SECRET!,
  timeoutMs: 30_000,
});
```

### `JevClient.fromEnv()`

```typescript
JevClient.fromEnv(environment?: NodeJS.ProcessEnv): JevClient
```

Reads:

- `CODESTUDIO_BASE_URL`, default `http://localhost:5142`
- `CODESTUDIO_API_KEY_ID`, required
- `CODESTUDIO_API_KEY_SECRET`, required

```typescript
const client = JevClient.fromEnv();
```

### `client.decide()`

```typescript
client.decide(
  request: JevDecisionRequest,
  options?: JevRequestOptions,
): Promise<JevDecisionResponse>
```

```typescript
interface JevDecisionRequest {
  state: JevState;
  questions: Record<string, JevQuestion>;
  model?: string;
  session_id?: string;
  user?: string;
  provider?: Record<string, unknown>;
  trace?: Record<string, unknown>;
}

interface JevRequestOptions {
  signal?: AbortSignal;
}
```

```typescript
const result = await client.decide(
  {
    state: { command: "npm test", exitCode: 1 },
    questions: {
      failure_type: {
        type: "choice",
        instructions: "Classify the primary failure cause.",
        criteria: {
          code_defect: "Implementation or test is incorrect.",
          environment: "Infrastructure or setup failed.",
          transient: "Retrying unchanged is likely to succeed.",
          unknown: "Evidence is insufficient.",
        },
      },
    },
  },
  { signal: AbortSignal.timeout(20_000) },
);
```

## Question types

```typescript
interface NoulQuestion {
  type: "noul";
  instructions: JevGuidance;
  criteria?: { true: JevGuidance; false: JevGuidance };
}

interface ChoiceQuestion {
  type: "choice";
  instructions: JevGuidance;
  criteria: Record<string, JevGuidance | null>;
}

interface ScoreQuestion {
  type: "score";
  instructions: JevGuidance;
  criteria: readonly JevGuidance[];
}
```

`JevGuidance` is a string, JSON object, or JSON array.

## Response types

```typescript
interface JevDecisionResponse {
  id?: string;
  model: string;
  provider?: string;
  answers: Record<string, JevAnswer>;
  usage: {
    input_tokens: number;
    output_tokens: number;
    cost: number;
  };
}
```

Use the `type` discriminator:

```typescript
const answer = result.answers.failure_type;

if (answer?.type === "choice") {
  console.log(answer.choice, answer.confidence, answer.probabilities);
}
```

## Errors

### `JevConfigurationError`

Thrown before an HTTP call for invalid client configuration or request input.

Examples:

- Missing base URL, client ID, or secret
- Non-positive timeout
- HTTP remote URL
- Empty questions
- Missing instructions or criteria

### `JevApiError`

```typescript
class JevApiError extends Error {
  readonly status: number;
  readonly code: number | string | undefined;
  readonly responseBody: unknown;
}
```

Thrown for non-success HTTP responses and invalid success responses.

```typescript
try {
  await client.decide(request);
} catch (error) {
  if (error instanceof JevApiError) {
    console.error(error.status, error.code, error.message);
  }
}
```

## Signing helpers

Advanced callers can import:

```typescript
import {
  buildCanonicalMessage,
  signHeaders,
} from "@syncfusion/codestudio-jev";
```

Most applications should use `JevClient`, which ensures the signed body and transmitted body remain identical.
