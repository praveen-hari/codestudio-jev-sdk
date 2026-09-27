# Authentication and security

The SDKs authenticate with HMAC-SHA256 signed API keys. The raw secret is never sent over the network.

## Obtain credentials

SDK users and automation scripts cannot create API keys directly. Ask an organization administrator to:

1. Sign in to the CodeStudio Enterprise web UI.
2. Open the **API Keys** page.
3. Create a key with the `jev:invoke` scope.
4. Configure an appropriate rate limit and expiration.
5. Transfer the client ID and one-time secret through an approved secure channel.

If the secret is lost, ask the administrator to rotate the key. The existing secret cannot be retrieved.

## Required headers

```text
X-Api-Key-Id: <client ID>
X-Api-Timestamp: <current ISO-8601 UTC timestamp>
X-Api-Signature: <base64url HMAC-SHA256 signature>
Content-Type: application/json
```

## Canonical message

The signature covers five newline-separated values:

```text
UPPERCASE_HTTP_METHOD
lowercase_request_path
alphabetically_sorted_query_string_or_empty
timestamp
lowercase_sha256_hex_of_exact_body_bytes
```

For the Decisions endpoint with no query string:

```text
POST
/v1/decisions

2026-09-27T10:00:00.000000Z
<body-sha256-hex>
```

The blank third line is required.

$$
\text{signature} = \operatorname{Base64Url}\left(
  \operatorname{HMAC\text{-}SHA256}(\text{decodedSecret}, \text{canonicalMessage})
\right)
$$

The administrator-provided secret is base64url encoded. The SDK decodes it before HMAC calculation.

## Security properties

The signature binds authentication to:

- HTTP method
- Request path
- Sorted query string
- Timestamp
- Exact request body

The server additionally enforces:

- Five-minute timestamp window
- Constant-time signature verification
- Key activation and expiry
- Scope authorization
- Per-key rate limiting
- Replay protection when Redis is available
- Secret rotation with a grace period

## Exact-body requirement

These JSON documents contain the same data but produce different hashes:

```json
{"state":"hello"}
```

```json
{ "state": "hello" }
```

The SDK serializes once, then hashes and transmits that exact representation. If implementing signing manually, never re-serialize or format the body after signing.

## Scope selection

| Scope | Use |
|---|---|
| `jev:invoke` | Recommended for JEV-only scripts and automation |
| `llm:invoke` | General LLM access, including JEV |
| `admin:*` | Administrative access; do not use for normal automation |

Follow least privilege. An SDK integration normally needs only `jev:invoke`.

## Credential storage

Recommended:

- Cloud secret manager
- GitHub Actions or CI protected secrets
- Kubernetes Secrets
- Operating-system credential store
- Protected environment injection

Do not store credentials in:

- Source files
- Committed `.env` files
- Harness configuration
- Command-line arguments
- JEV state or questions
- Logs, traces, or exception messages

## Untrusted sandboxes

Do not inject a long-lived organization key into an untrusted sandbox. Repository scripts can inspect environment variables and exfiltrate secrets.

Use one of these patterns instead:

1. Run the SDK call in the trusted harness host.
2. Expose JEV as a trusted agent tool.
3. Use a broker with a short-lived, run-scoped capability.

## Secret exposure response

If a secret appears in chat, logs, shell history, or a repository:

1. Rotate the API key immediately in the Enterprise UI.
2. Update the secret manager.
3. Invalidate or remove exposed history where possible.
4. Review API-key usage and request logs.
