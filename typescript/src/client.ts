import { JevApiError, JevConfigurationError, type JevErrorBody } from "./errors.js";
import { signHeaders } from "./signing.js";
import type {
  JevClientOptions,
  JevDecisionRequest,
  JevDecisionResponse,
  JevRequestOptions,
} from "./types.js";

const DECISIONS_PATH = "/v1/decisions";
const DEFAULT_MODEL = "~typesafe/jev-latest";
const DEFAULT_TIMEOUT_MS = 45_000;

export class JevClient {
  readonly #baseUrl: string;
  readonly #clientId: string;
  readonly #secret: string;
  readonly #timeoutMs: number;
  readonly #fetch: typeof globalThis.fetch;

  constructor(options: JevClientOptions) {
    if (!options.baseUrl.trim()) throw new JevConfigurationError("baseUrl is required");
    if (!options.clientId.trim()) throw new JevConfigurationError("clientId is required");
    if (!options.secret.trim()) throw new JevConfigurationError("secret is required");
    if (options.timeoutMs !== undefined && (!Number.isFinite(options.timeoutMs) || options.timeoutMs <= 0)) {
      throw new JevConfigurationError("timeoutMs must be a positive number");
    }

    const url = new URL(options.baseUrl);
    if (url.protocol !== "https:" && url.hostname !== "localhost" && url.hostname !== "127.0.0.1") {
      throw new JevConfigurationError("baseUrl must use HTTPS except for localhost development");
    }

    this.#baseUrl = options.baseUrl.replace(/\/$/, "");
    this.#clientId = options.clientId;
    this.#secret = options.secret;
    this.#timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
    this.#fetch = options.fetch ?? globalThis.fetch;
    if (!this.#fetch) throw new JevConfigurationError("fetch is not available");
  }

  static fromEnv(environment: NodeJS.ProcessEnv = process.env): JevClient {
    const baseUrl = environment.CODESTUDIO_BASE_URL ?? "http://localhost:5142";
    const clientId = environment.CODESTUDIO_API_KEY_ID;
    const secret = environment.CODESTUDIO_API_KEY_SECRET;
    if (!clientId) throw new JevConfigurationError("CODESTUDIO_API_KEY_ID is required");
    if (!secret) throw new JevConfigurationError("CODESTUDIO_API_KEY_SECRET is required");
    return new JevClient({ baseUrl, clientId, secret });
  }

  async decide(request: JevDecisionRequest, options: JevRequestOptions = {}): Promise<JevDecisionResponse> {
    validateRequest(request);
    const payload = { ...request, model: request.model ?? DEFAULT_MODEL };
    const body = JSON.stringify(payload);
    const timestamp = new Date().toISOString();
    const authentication = signHeaders(
      this.#clientId,
      this.#secret,
      "POST",
      DECISIONS_PATH,
      "",
      timestamp,
      body,
    );

    const timeoutSignal = AbortSignal.timeout(this.#timeoutMs);
    const signal = options.signal ? AbortSignal.any([options.signal, timeoutSignal]) : timeoutSignal;
    const response = await this.#fetch(`${this.#baseUrl}${DECISIONS_PATH}`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        ...authentication,
      },
      body,
      signal,
    });

    const responseText = await response.text();
    const responseBody = parseJson(responseText);
    if (!response.ok) {
      const errorBody = responseBody as JevErrorBody | undefined;
      throw new JevApiError(
        response.status,
        errorBody?.error?.message ?? `JEV request failed with HTTP ${response.status}`,
        errorBody?.error?.code,
        responseBody ?? responseText,
      );
    }

    if (!isDecisionResponse(responseBody)) {
      throw new JevApiError(502, "JEV returned an invalid response", undefined, responseBody ?? responseText);
    }
    return responseBody;
  }
}

function validateRequest(request: JevDecisionRequest): void {
  if (request.state === null || request.state === undefined) {
    throw new JevConfigurationError("state is required");
  }
  const questions = Object.entries(request.questions ?? {});
  if (questions.length === 0) throw new JevConfigurationError("at least one question is required");

  for (const [name, question] of questions) {
    if (!name.trim()) throw new JevConfigurationError("question names cannot be empty");
    if (!question.instructions) throw new JevConfigurationError(`question '${name}' requires instructions`);
    if (question.type === "choice" && Object.keys(question.criteria).length === 0) {
      throw new JevConfigurationError(`choice question '${name}' requires criteria`);
    }
    if (question.type === "score" && question.criteria.length === 0) {
      throw new JevConfigurationError(`score question '${name}' requires criteria`);
    }
  }
}

function parseJson(value: string): unknown {
  try {
    return JSON.parse(value) as unknown;
  } catch {
    return undefined;
  }
}

function isDecisionResponse(value: unknown): value is JevDecisionResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<JevDecisionResponse>;
  return typeof candidate.model === "string"
    && !!candidate.answers && typeof candidate.answers === "object"
    && !!candidate.usage && typeof candidate.usage === "object"
    && typeof candidate.usage.input_tokens === "number"
    && typeof candidate.usage.output_tokens === "number"
    && typeof candidate.usage.cost === "number";
}
