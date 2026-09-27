# Examples

Runnable examples are available in the repository:

- [`examples/jev-decisions.ts`](https://github.com/praveen-hari/codestudio-jev-sdk/blob/main/examples/jev-decisions.ts)
- [`examples/jev_decisions.py`](https://github.com/praveen-hari/codestudio-jev-sdk/blob/main/examples/jev_decisions.py)

## Configure credentials

```bash
export CODESTUDIO_BASE_URL="https://api.sfcodestudio.com"
export CODESTUDIO_API_KEY_ID="key_..."
export CODESTUDIO_API_KEY_SECRET="..."
```

## TypeScript example

Build the SDK and run the example from a consumer project:

```bash
cd typescript
npm install
npm run build
cd ..
npm install ./typescript
npx tsx examples/jev-decisions.ts
```

The example sends all three primitives in one request:

```typescript
const result = await client.decide({
  state: {
    service: "checkout",
    impact: "Payment processing is unavailable for every customer.",
  },
  questions: {
    is_incident: {
      type: "noul",
      instructions: "Does this state describe a production incident?",
    },
    owner: {
      type: "choice",
      instructions: "Which team should own the response?",
      criteria: {
        payments: "Checkout, billing, or payment processing.",
        frontend: "Rendering, layout, or browser behavior.",
      },
    },
    urgency: {
      type: "score",
      instructions: "How urgent is this incident?",
      criteria: ["Low", "Medium", "Critical"],
    },
  },
});
```

## Python example

```bash
python3 -m pip install ./python
python3 examples/jev_decisions.py
```

```python
result = client.decide(
    state={
        "service": "checkout",
        "impact": "Payment processing is unavailable for every customer.",
    },
    questions={
        "is_incident": {
            "type": "noul",
            "instructions": "Does this state describe a production incident?",
        },
        "owner": {
            "type": "choice",
            "instructions": "Which team should own the response?",
            "criteria": {
                "payments": "Checkout, billing, or payment processing.",
                "frontend": "Rendering, layout, or browser behavior.",
            },
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this incident?",
            "criteria": ["Low", "Medium", "Critical"],
        },
    },
)
```

## CI example

```yaml
name: JEV risk review

on:
  pull_request:

jobs:
  risk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm install ./typescript

      - run: node scripts/review-risk.mjs
        env:
          CODESTUDIO_BASE_URL: ${{ secrets.CODESTUDIO_BASE_URL }}
          CODESTUDIO_API_KEY_ID: ${{ secrets.CODESTUDIO_API_KEY_ID }}
          CODESTUDIO_API_KEY_SECRET: ${{ secrets.CODESTUDIO_API_KEY_SECRET }}
```

Use a dedicated `jev:invoke` key with a low rate limit and appropriate expiration.
