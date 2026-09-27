# SDK overview

The repository provides two dependency-free runtime clients with the same behavior:

<div class="grid cards" markdown>

-   **TypeScript**

    Package: `@syncfusion/codestudio-jev`

    Node.js 22+, typed discriminated unions, built-in `fetch` and `crypto`, cancellation via `AbortSignal`.

    [:octicons-arrow-right-24: TypeScript API](typescript.md)

-   **Python**

    Distribution: `syncfusion-codestudio-jev`

    Python 3.11+, standard-library HTTP and crypto, typed request definitions, immutable response dataclass.

    [:octicons-arrow-right-24: Python API](python.md)

</div>

## Shared behavior

Both SDKs:

- Call only `POST /v1/decisions`
- Default to `~typesafe/jev-latest`
- Serialize the request exactly once
- Hash and sign the exact transmitted bytes
- Generate a UTC timestamp for each request
- Decode the base64url API secret automatically
- Add all HMAC authentication headers
- Use a 45-second default timeout
- Reject non-HTTPS remote base URLs
- Permit HTTP only for `localhost` and `127.0.0.1`
- Validate the top-level response and usage fields
- Never log credentials or signatures

## Environment configuration

```text
CODESTUDIO_BASE_URL=https://api.sfcodestudio.com
CODESTUDIO_API_KEY_ID=key_...
CODESTUDIO_API_KEY_SECRET=...
```

`CODESTUDIO_BASE_URL` defaults to `http://localhost:5142` for local development. The key ID and secret are required.

## Choosing an SDK

| Requirement | TypeScript | Python |
|---|---:|---:|
| Node.js automation | Best fit | — |
| Python automation | — | Best fit |
| Compile-time answer discrimination | Yes | TypedDict request definitions |
| Cancellation signal | Yes | Not currently exposed |
| Custom HTTP implementation | Custom `fetch` | Not currently exposed |
| Runtime dependencies | None | None |
