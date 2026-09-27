# Software development automation

JEV is useful where a development harness must make a small typed decision from bounded evidence.

## Recommended pattern

```text
Collect deterministic evidence
        ↓
Ask one or more typed JEV questions
        ↓
Validate answer types and allowed values
        ↓
Apply confidence thresholds
        ↓
Apply deterministic safety overrides
        ↓
Execute one predefined harness action
```

JEV should classify evidence. It should not generate arbitrary shell commands or override deterministic safety checks.

## Good use cases

| Workflow | Primitive | Outcomes |
|---|---|---|
| Test-failure triage | Choice | `code_defect`, `transient`, `environment`, `unknown` |
| Retry recommendation | Noul | Probability that a retry is appropriate |
| Change risk | Score | `low`, `medium`, `high`, `critical` |
| Review routing | Choice | `frontend`, `backend`, `security`, `database` |
| Destructive action gate | Choice | `allow`, `human_review`, `deny` |
| Test-scope selection | Choice | `targeted`, `integration`, `full_regression` |
| Defect severity | Score | Ordered severity |
| Agent completion review | Noul + Choice | Criteria satisfaction and next action |

## Test failure triage

=== "TypeScript"

    ```typescript
    import { JevClient } from "@syncfusion/codestudio-jev";

    const result = await JevClient.fromEnv().decide({
      state: {
        command: "npm test",
        exitCode: 1,
        attempt: 1,
        changedFiles: ["src/auth.ts", "test/auth.test.ts"],
        stderr: testOutput.slice(-15_000),
      },
      questions: {
        failure_type: {
          type: "choice",
          instructions: "Classify the primary cause using only supplied evidence.",
          criteria: {
            code_defect: "The implementation or test is incorrect.",
            transient: "Retrying without changes is likely to succeed.",
            environment: "Infrastructure, credentials, or setup failed.",
            unknown: "Evidence is insufficient.",
          },
        },
      },
    });

    const answer = result.answers.failure_type;
    const action = answer?.type === "choice" && (answer.confidence ?? 0) >= 0.75
      ? answer.choice
      : "human_review";
    ```

=== "Python"

    ```python
    from codestudio_jev import JevClient

    result = JevClient.from_env().decide(
        state={
            "command": "pytest",
            "exit_code": 1,
            "attempt": 1,
            "changed_files": ["src/auth.py", "tests/test_auth.py"],
            "stderr": test_output[-15_000:],
        },
        questions={
            "failure_type": {
                "type": "choice",
                "instructions": "Classify the primary cause using only supplied evidence.",
                "criteria": {
                    "code_defect": "Implementation or test is incorrect.",
                    "transient": "Retrying without changes is likely to succeed.",
                    "environment": "Infrastructure, credentials, or setup failed.",
                    "unknown": "Evidence is insufficient.",
                },
            }
        },
    )

    answer = result.answers["failure_type"]
    action = answer["choice"] if answer.get("confidence", 0) >= 0.75 else "human_review"
    ```

Always cap retries independently of the JEV answer.

## Deployment gate

Ask multiple independent questions, then apply deterministic policy:

```typescript
const result = await client.decide({
  state: {
    branch,
    environment,
    testStatus,
    securityFindings,
    migrations,
    changedFiles,
  },
  questions: {
    blocking_risk: {
      type: "noul",
      instructions: "Is there evidence of a blocking deployment risk?",
      criteria: {
        true: "Evidence indicates data loss, security, or rollback risk.",
        false: "No blocking risk is present in supplied evidence.",
      },
    },
    risk_level: {
      type: "score",
      instructions: "Rate deployment risk.",
      criteria: ["Low", "Medium", "High", "Critical"],
    },
    next_action: {
      type: "choice",
      instructions: "Choose the required deployment action.",
      criteria: {
        approve: "Evidence supports automated deployment.",
        human_review: "A person must review before deployment.",
        deny: "Deployment must not proceed.",
      },
    },
  },
});
```

```typescript
const blocking = result.answers.blocking_risk;
const risk = result.answers.risk_level;
const next = result.answers.next_action;

const action =
  blocking?.type !== "noul" ||
  risk?.type !== "score" ||
  next?.type !== "choice" ||
  blocking.noul >= 0.5 ||
  risk.score >= 2 ||
  (next.confidence ?? 0) < 0.8
    ? "human_review"
    : next.choice;
```

## Harness output contract

Decision scripts should print one machine-readable object:

```json
{
  "action": "human_review",
  "confidence": 0.72,
  "probabilities": {
    "continue": 0.2,
    "retry": 0.08,
    "human_review": 0.72
  },
  "request_id": "gen-dec-..."
}
```

The trusted runner should:

1. Capture bounded command evidence.
2. Execute the decision script with a timeout.
3. Parse exactly one JSON object from standard output.
4. Reject unknown actions.
5. Enforce retry limits.
6. Default to `human_review` or `stop` on any failure.
7. Audit the evidence reference, JEV request ID, decision, and final action.

## What not to delegate

Keep these deterministic:

- Compilation success
- Test pass/fail
- Numeric coverage thresholds
- Critical vulnerability findings
- Migration existence
- Credential validity
- Command allowlists
- Protected-branch enforcement

Use JEV for: **“Given bounded evidence, which predefined category or action best fits?”**
