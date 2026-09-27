# CodeStudio JEV SDK

Build reliable software-development automations with typed decisions from TypeSafe JEV.

<div class="grid cards" markdown>

-   :material-language-typescript:{ .lg .middle }

    **TypeScript SDK**

    ---

    Typed requests and responses, automatic HMAC signing, cancellation, and structured errors for Node.js 22+.

    [:octicons-arrow-right-24: TypeScript reference](sdk/typescript.md)

-   :material-language-python:{ .lg .middle }

    **Python SDK**

    ---

    Standard-library runtime, typed request definitions, response dataclass, automatic signing, and structured errors.

    [:octicons-arrow-right-24: Python reference](sdk/python.md)

-   :material-api:{ .lg .middle }

    **REST API**

    ---

    Call `POST /v1/decisions` with Noul, Choice, and Score questions using HMAC API-key authentication.

    [:octicons-arrow-right-24: API reference](api/index.md)

-   :material-robot-outline:{ .lg .middle }

    **Automation harnesses**

    ---

    Classify failures, assess risk, route review, and gate predefined workflow actions.

    [:octicons-arrow-right-24: Development patterns](guides/software-development.md)

</div>

## Quick start

=== "TypeScript"

    ```bash
    npm install /path/to/codestudio-jev-sdk/typescript
    ```

    ```typescript
    import { JevClient } from "@syncfusion/codestudio-jev";

    const result = await JevClient.fromEnv().decide({
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

=== "Python"

    ```bash
    python3 -m pip install /path/to/codestudio-jev-sdk/python
    ```

    ```python
    from codestudio_jev import JevClient

    result = JevClient.from_env().decide(
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

## Configure credentials

Ask an organization administrator to create an API key in the CodeStudio Enterprise **API Keys** page with the `jev:invoke` scope. Store the one-time secret securely, then configure:

```bash
export CODESTUDIO_BASE_URL="https://api.sfcodestudio.com"
export CODESTUDIO_API_KEY_ID="key_..."
export CODESTUDIO_API_KEY_SECRET="..."
```

!!! warning "Protect API credentials"
    Never commit the client ID and secret. Use a secret manager or protected CI/CD variables. Long-lived organization keys must not be injected into untrusted sandboxes.

## Decision primitives

| Primitive | Use it for | Returns |
|---|---|---|
| **Noul** | Whether a condition holds | A probability from `0` to `1` |
| **Choice** | Selecting one predefined option | Selected option, probabilities, confidence |
| **Score** | Position on an ordered scale | Weighted score, probabilities, legend, confidence |

## What JEV should decide

Use JEV for bounded classification from structured evidence:

- Test-failure triage
- Risk and severity scoring
- Review routing
- Retry, stop, or human-review recommendations
- Deployment and destructive-action gates

Keep deterministic checks authoritative. Compilers, tests, policy engines, vulnerability scanners, and branch protection should not be replaced by JEV.
