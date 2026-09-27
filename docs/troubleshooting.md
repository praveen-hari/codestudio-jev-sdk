# Troubleshooting

## HTTP 401

Possible causes:

- Incorrect client ID or secret
- Secret not base64url decoded before manual signing
- Body changed after signature generation
- Incorrect request path in canonical message
- Timestamp older or newer than the five-minute window
- Reused signature rejected by replay protection
- Revoked or expired API key

SDK calls always generate a fresh timestamp and sign the exact serialized body. If SDK authentication fails, verify the provided credentials and system clock.

## HTTP 403

The API key lacks an allowed scope. Ask an administrator to create or rotate a key with:

- `jev:invoke`, recommended
- `llm:invoke`, broader access

Do not use `admin:*` for ordinary automation.

## HTTP 404

The endpoint is not deployed or exposed at the configured base URL.

The SDK appends `/v1/decisions`, so configure only the API origin:

```text
Correct:   https://api.sfcodestudio.com
Incorrect: https://api.sfcodestudio.com/v1/decisions
```

A deployed route returns `405 Method Not Allowed` for an unauthenticated `GET /v1/decisions`, with `Allow: POST`. A missing route returns `404`.

## HTTP 429

The effective limit may be constrained by:

- API-key request limit
- Gateway per-user limit
- Organization-level policy

Reduce frequency or ask an administrator to adjust the key limit.

## HTTP 502, 503, or 504

| Status | Meaning |
|---:|---|
| `502` | Upstream unavailable or returned an invalid response |
| `503` | JEV is not configured or the circuit breaker is open |
| `504` | Upstream timeout |

Treat timeouts as unknown outcomes. Do not blindly retry billable requests.

## TypeScript configuration errors

```text
baseUrl must use HTTPS except for localhost development
```

Use HTTPS for remote APIs. HTTP is accepted only for `localhost` and `127.0.0.1`.

```text
secret must decode to exactly 32 bytes
```

Use the one-time base64url secret displayed by the Enterprise API Keys UI, without quotes or surrounding whitespace.

## Python receives 403 while TypeScript works

Use the latest Python SDK. It supplies an explicit SDK user agent and JSON accept header required by some edge-security configurations.

## Invalid success response

Both SDKs verify that successful responses contain:

- `model`
- `answers`
- `usage.input_tokens`
- `usage.output_tokens`
- `usage.cost`

An invalid shape raises `JevApiError` with status `502`.

## Clock synchronization

HMAC timestamps are accepted only within five minutes of server time. Enable NTP or platform time synchronization on CI runners and automation hosts.

## Secret exposed in logs or chat

Rotate it immediately through the Enterprise API Keys UI. Updating documentation or deleting a local shell command does not invalidate an exposed credential.
