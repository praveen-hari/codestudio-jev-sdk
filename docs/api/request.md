# Request schema

## Top-level object

| Field | Type | Required | Description |
|---|---|---:|---|
| `model` | string | Yes at REST level | JEV model identifier. SDKs default to `~typesafe/jev-latest`. |
| `state` | string, object, or array | Yes | Evidence or application state to evaluate. |
| `questions` | object | Yes | One or more named Noul, Choice, or Score questions. |
| `session_id` | string | No | Correlates related requests; maximum 256 characters. |
| `user` | string | No | Caller-defined user identifier; maximum 256 characters. |
| `provider` | object | No | OpenRouter provider-routing preferences. |
| `trace` | object | No | Trace and observability metadata. |

## Model identifiers

Accepted forms include:

- `~typesafe/jev-latest`
- `typesafe/jev-1.13`
- `jev-latest`, normalized to `~typesafe/jev-latest`
- `jev-1.13`, normalized to `typesafe/jev-1.13`

Pin a specific model version when calibrated thresholds must remain stable. Use the latest alias when automatic model upgrades are acceptable.

## State

`state` can be a string:

```json
{
  "state": "The checkout button does nothing when clicked."
}
```

Or structured JSON:

```json
{
  "state": {
    "command": "npm test",
    "exit_code": 1,
    "attempt": 1,
    "changed_files": ["src/auth.ts", "test/auth.test.ts"],
    "stderr": "AssertionError: expected 200, received 401"
  }
}
```

!!! tip "Send bounded evidence"
    Prefer concise structured evidence and bounded log excerpts. Do not send secrets, full environment dumps, customer PII, or entire repositories.

## Noul question

Noul evaluates whether a condition holds.

```json
{
  "type": "noul",
  "instructions": "Is this a production incident?",
  "criteria": {
    "true": "Production behavior is unavailable or broken.",
    "false": "Production behavior is operating normally."
  }
}
```

| Field | Required | Description |
|---|---:|---|
| `type` | Yes | Must be `noul`. |
| `instructions` | Yes | String, object, or array guidance. |
| `criteria` | No | If supplied, must define both `true` and `false`. |

## Choice question

Choice selects one named option.

```json
{
  "type": "choice",
  "instructions": "Classify the primary cause of this failure.",
  "criteria": {
    "code_defect": "The implementation or test is incorrect.",
    "environment": "Infrastructure, credentials, or setup failed.",
    "transient": "Retrying without a code change is likely to succeed.",
    "unknown": "There is insufficient evidence."
  }
}
```

| Field | Required | Description |
|---|---:|---|
| `type` | Yes | Must be `choice`. |
| `instructions` | Yes | String, object, or array guidance. |
| `criteria` | Yes | Non-empty object mapping option names to guidance. |

## Score question

Score positions state on an ordered scale.

```json
{
  "type": "score",
  "instructions": "Rate deployment risk.",
  "criteria": ["Low", "Medium", "High", "Critical"]
}
```

| Field | Required | Description |
|---|---:|---|
| `type` | Yes | Must be `score`. |
| `instructions` | Yes | String, object, or array guidance. |
| `criteria` | Yes | Non-empty ordered array. |

The returned score is a probability-weighted position. It can be fractional.

## Multiple questions

Questions in one request share the same state and are evaluated independently:

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
        "payments": "Payment failure.",
        "frontend": "Rendering failure."
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
