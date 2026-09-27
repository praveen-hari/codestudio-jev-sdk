import { createHash, createHmac } from "node:crypto";
import { JevConfigurationError } from "./errors.js";

export interface SignedHeaders {
  "x-api-key-id": string;
  "x-api-timestamp": string;
  "x-api-signature": string;
}

export function buildCanonicalMessage(
  method: string,
  path: string,
  queryString: string,
  timestamp: string,
  body: string,
): string {
  const bodyHash = createHash("sha256").update(body, "utf8").digest("hex");
  return [method.toUpperCase(), path.toLowerCase(), sortQueryString(queryString), timestamp, bodyHash].join("\n");
}

export function signHeaders(
  clientId: string,
  encodedSecret: string,
  method: string,
  path: string,
  queryString: string,
  timestamp: string,
  body: string,
): SignedHeaders {
  if (!clientId.trim()) {
    throw new JevConfigurationError("clientId is required");
  }

  let secret: Buffer;
  try {
    secret = Buffer.from(encodedSecret, "base64url");
  } catch (error) {
    throw new JevConfigurationError(`secret must be valid base64url: ${String(error)}`);
  }
  if (secret.length !== 32) {
    throw new JevConfigurationError("secret must decode to exactly 32 bytes");
  }

  const canonicalMessage = buildCanonicalMessage(method, path, queryString, timestamp, body);
  const signature = createHmac("sha256", secret).update(canonicalMessage, "utf8").digest("base64url");

  return {
    "x-api-key-id": clientId,
    "x-api-timestamp": timestamp,
    "x-api-signature": signature,
  };
}

function sortQueryString(queryString: string): string {
  const query = queryString.startsWith("?") ? queryString.slice(1) : queryString;
  if (!query) return "";

  return query
    .split("&")
    .filter(Boolean)
    .map((part) => {
      const separator = part.indexOf("=");
      return separator >= 0 ? [part.slice(0, separator), part.slice(separator + 1)] : [part, ""];
    })
    .sort(([left], [right]) => (left ?? "").localeCompare(right ?? ""))
    .map(([key, value]) => `${key}=${value}`)
    .join("&");
}
