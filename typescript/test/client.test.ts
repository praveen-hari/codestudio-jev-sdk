import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import test from "node:test";
import { JevApiError, JevClient, buildCanonicalMessage } from "../src/index.js";

const secretBytes = Buffer.from(Array.from({ length: 32 }, (_, index) => index));
const secret = secretBytes.toString("base64url");

function successfulResponse(): Response {
  return new Response(JSON.stringify({
    id: "gen-dec-test",
    model: "typesafe/jev-1.13",
    provider: "TypeSafe",
    answers: { safe: { type: "noul", noul: 0.9 } },
    usage: { input_tokens: 10, output_tokens: 1, cost: 0.000001 },
  }), { status: 200, headers: { "content-type": "application/json" } });
}

test("decide signs and sends the exact serialized request", async () => {
  let capturedUrl = "";
  let capturedInit: RequestInit | undefined;
  const client = new JevClient({
    baseUrl: "http://localhost:5142/",
    clientId: "key_test",
    secret,
    fetch: async (input, init) => {
      capturedUrl = String(input);
      capturedInit = init;
      return successfulResponse();
    },
  });

  const result = await client.decide({
    state: "hello",
    questions: { safe: { type: "noul", instructions: "Is it safe?" } },
  });

  assert.equal(result.answers.safe?.type, "noul");
  assert.equal(capturedUrl, "http://localhost:5142/v1/decisions");
  assert.equal(capturedInit?.method, "POST");
  const body = String(capturedInit?.body);
  const headers = capturedInit?.headers as Record<string, string>;
  assert.match(body, /"model":"~typesafe\/jev-latest"/);
  assert.equal(headers["x-api-key-id"], "key_test");
  const canonical = buildCanonicalMessage(
    "POST",
    "/v1/decisions",
    "",
    headers["x-api-timestamp"] ?? "",
    body,
  );
  const expected = createHmac("sha256", secretBytes).update(canonical).digest("base64url");
  assert.equal(headers["x-api-signature"], expected);
});

test("decide surfaces structured API errors", async () => {
  const client = new JevClient({
    baseUrl: "https://enterprise.example.com",
    clientId: "key_test",
    secret,
    fetch: async () => new Response(
      JSON.stringify({ error: { code: 403, message: "Missing jev:invoke scope" } }),
      { status: 403 },
    ),
  });

  await assert.rejects(
    client.decide({ state: "hello", questions: { safe: { type: "noul", instructions: "Safe?" } } }),
    (error: unknown) => error instanceof JevApiError
      && error.status === 403
      && error.message === "Missing jev:invoke scope",
  );
});

test("client rejects insecure non-local base URLs", () => {
  assert.throws(
    () => new JevClient({ baseUrl: "http://enterprise.example.com", clientId: "key_test", secret }),
    /must use HTTPS/,
  );
});
