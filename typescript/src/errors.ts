export interface JevErrorBody {
  error?: {
    code?: number | string;
    message?: string;
  };
}

export class JevApiError extends Error {
  readonly status: number;
  readonly code: number | string | undefined;
  readonly responseBody: unknown;

  constructor(status: number, message: string, code?: number | string, responseBody?: unknown) {
    super(message);
    this.name = "JevApiError";
    this.status = status;
    this.code = code;
    this.responseBody = responseBody;
  }
}

export class JevConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "JevConfigurationError";
  }
}
