export type JevGuidance = string | Record<string, unknown> | readonly unknown[];
export type JevState = string | Record<string, unknown> | readonly unknown[];

export interface NoulQuestion {
  type: "noul";
  instructions: JevGuidance;
  criteria?: {
    true: JevGuidance;
    false: JevGuidance;
  };
}

export interface ChoiceQuestion {
  type: "choice";
  instructions: JevGuidance;
  criteria: Record<string, JevGuidance | null>;
}

export interface ScoreQuestion {
  type: "score";
  instructions: JevGuidance;
  criteria: readonly JevGuidance[];
}

export type JevQuestion = NoulQuestion | ChoiceQuestion | ScoreQuestion;

export interface JevDecisionRequest {
  state: JevState;
  questions: Record<string, JevQuestion>;
  model?: string;
  session_id?: string;
  user?: string;
  provider?: Record<string, unknown>;
  trace?: Record<string, unknown>;
}

export interface NoulAnswer {
  type: "noul";
  noul: number;
}

export interface ChoiceAnswer {
  type: "choice";
  choice: string;
  confidence?: number;
  probabilities?: Record<string, number>;
}

export interface ScoreAnswer {
  type: "score";
  score: number;
  confidence?: number;
  probabilities?: Record<string, number>;
  legend?: Record<string, JevGuidance>;
}

export type JevAnswer = NoulAnswer | ChoiceAnswer | ScoreAnswer;

export interface JevUsage {
  input_tokens: number;
  output_tokens: number;
  cost: number;
}

export interface JevDecisionResponse {
  id?: string;
  model: string;
  provider?: string;
  answers: Record<string, JevAnswer>;
  usage: JevUsage;
}

export interface JevClientOptions {
  baseUrl: string;
  clientId: string;
  secret: string;
  timeoutMs?: number;
  fetch?: typeof globalThis.fetch;
}

export interface JevRequestOptions {
  signal?: AbortSignal;
}
