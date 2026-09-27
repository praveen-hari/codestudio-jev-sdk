# Responses and errors

## Success response

| Field | Type | Description |
|---|---|---|
| `id` | string | Provider generation identifier. |
| `model` | string | Resolved dated model snapshot. |
| `provider` | string | Provider name, normally `TypeSafe`. |
| `answers` | object | One typed answer for each request question. |
| `usage.input_tokens` | integer | Input tokens consumed. |
| `usage.output_tokens` | integer | Output tokens reported. |
| `usage.cost` | number | Provider-reported USD cost. |

## Noul answer

```json
{
  "type": "noul",
  "noul": 0.96
}
```

`noul` is the probability that the condition is true. Values near `0.5` indicate ambiguity.

## Choice answer

```json
{
  "type": "choice",
  "choice": "billing",
  "probabilities": {
    "billing": 0.9,
    "technical": 0.08,
    "account": 0.02
  },
  "confidence": 0.82
}
```

`choice` is the selected option. `probabilities` provides the distribution across options. `confidence` describes concentration of that distribution; it is not a guarantee that an automated action is safe.

## Score answer

```json
{
  "type": "score",
  "score": 1.8,
  "legend": {
    "0": "Low",
    "1": "Medium",
    "2": "Critical"
  },
  "probabilities": {
    "0": 0,
    "1": 0.2,
    "2": 0.8
  },
  "confidence": 0.8
}
```

`score` is the probability-weighted position on the ordered criteria. Do not assume it is always an integer.

## Error shape

```json
{
  "error": {
    "code": 400,
    "message": "The required 'state' field must be a string, object, or array."
  }
}
```

## HTTP statuses

| Status | Meaning | Typical action |
|---:|---|---|
| `400` | Invalid JSON, model, state, questions, or criteria | Correct the request; do not retry unchanged. |
| `401` | Missing/invalid signature, expired timestamp, revoked key, or replay | Verify credentials and generate a fresh signature. |
| `402` | Subscription or credit restriction | Contact the organization administrator. |
| `403` | API key lacks an allowed scope | Request `jev:invoke` or `llm:invoke`. |
| `413` | Request exceeds 10 MB | Reduce state and log excerpts. |
| `429` | API-key or gateway rate limit | Back off according to application policy. |
| `502` | Upstream unavailable or invalid response | Retry later if the operation is safe to repeat. |
| `503` | JEV is not configured or circuit is open | Check service configuration and status. |
| `504` | Upstream timeout | Treat outcome as unknown before retrying a billable request. |

!!! warning "Do not blindly retry billable requests"
    A timeout or gateway failure does not prove the provider skipped processing. The service deliberately does not automatically retry JEV requests.

## SDK exceptions

=== "TypeScript"

    ```typescript
    import { JevApiError } from "@syncfusion/codestudio-jev";

    try {
      await client.decide(request);
    } catch (error) {
      if (error instanceof JevApiError) {
        console.error(error.status, error.code, error.message);
      }
    }
    ```

=== "Python"

    ```python
    from codestudio_jev import JevApiError

    try:
        client.decide(state=state, questions=questions)
    except JevApiError as error:
        print(error.status, error.code, str(error))
    ```
