import { logger } from "@/lib/logger";

import { ApiError } from "./client-errors";

const invalidResponseBody = { error: "invalid_response" } as const;

const unknownRoute = "(unknown route)";

/**
 * Route identity for failure telemetry. Only the pathname is recorded so query
 * strings (which may carry identifiers or tokens) never reach the logs.
 */
function routeOf(response: Response): string {
  if (response.url === "") {
    return unknownRoute;
  }
  try {
    return new URL(response.url).pathname;
  } catch {
    return unknownRoute;
  }
}

function logFailure(response: Response, detail: string): void {
  logger.warn(`[API] ${detail}`, { status: response.status, route: routeOf(response) });
}

/**
 * Converts a raw openapi-fetch result into data, or throws a typed ApiError that
 * preserves the HTTP status. A failed request is never reported as success and
 * never converted into an empty result.
 */
export async function requireAvailable<T>(
  request: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await request;
  if (!response.ok) {
    logFailure(response, "request failed");
    throw new ApiError(
      response.status,
      response.status === 501 ? "Not implemented yet" : "Service unavailable",
      error,
    );
  }
  if (data === undefined) {
    logFailure(response, "response carried no data");
    throw new ApiError(502, "Invalid response from service", { ...invalidResponseBody });
  }
  return data;
}

/** Throws the shared contract-mismatch error for a 2xx payload of the wrong shape. */
export function invalidResponse(): never {
  throw new ApiError(502, "Invalid response from service", { ...invalidResponseBody });
}

/**
 * True when a 2xx payload is not API content (for example a sign-in HTML page
 * served with HTTP 200 by an edge/proxy). Such a payload must never be treated
 * as data or as a downloadable artifact.
 */
export function isNonApiContent(contentType: string): boolean {
  const normalized = contentType.toLowerCase();
  return normalized.includes("text/html") || normalized.includes("text/plain");
}

export function rejectNonApiContent(contentType: string): void {
  if (isNonApiContent(contentType)) {
    logger.warn("[API] rejected non-API content", { contentType });
    invalidResponse();
  }
}

export type FailureKind =
  | "not_implemented"
  | "unauthorized"
  | "forbidden"
  | "absent_route"
  | "rate_limited"
  | "invalid_response"
  | "unavailable"
  | "failed";

export interface FailureState {
  kind: FailureKind;
  status: number | undefined;
  title: string;
  detail: string;
}

const failureStates: Record<FailureKind, { title: string; detail: string }> = {
  not_implemented: {
    title: "Not implemented yet",
    detail: "This capability is not available yet.",
  },
  unauthorized: {
    title: "Sign-in required",
    detail: "Your session is not valid. Sign in again to load this data.",
  },
  forbidden: {
    title: "Access denied",
    detail: "You do not have permission to view this data.",
  },
  absent_route: {
    title: "Route not available",
    detail: "The server has no route for this request, so no data was loaded.",
  },
  rate_limited: {
    title: "Too many requests",
    detail: "The server is rate limiting requests. Try again shortly.",
  },
  invalid_response: {
    title: "Invalid response",
    detail:
      "The server replied, but the payload did not match the expected contract. No data was loaded.",
  },
  unavailable: {
    title: "Service unavailable",
    detail: "The backend cannot be reached or is not ready. Try again later.",
  },
  failed: {
    title: "Request failed",
    detail: "The request failed before any data could be loaded. Try again.",
  },
};

function kindOfStatus(status: number, markedInvalid: boolean): FailureKind {
  if (markedInvalid) {
    return "invalid_response";
  }
  if (status === 501) {
    return "not_implemented";
  }
  if (status === 401) {
    return "unauthorized";
  }
  if (status === 403) {
    return "forbidden";
  }
  if (status === 404 || status === 405) {
    return "absent_route";
  }
  if (status === 429) {
    return "rate_limited";
  }
  if (status >= 500) {
    return "unavailable";
  }
  return "failed";
}

function isMarkedInvalid(data: unknown): boolean {
  return (
    typeof data === "object" &&
    data !== null &&
    (data as Record<string, unknown>)["error"] === invalidResponseBody.error
  );
}

/**
 * Classifies a failure into the user-facing state model: not implemented,
 * unauthorized, forbidden, absent route, rate limited, invalid response,
 * unavailable backend, or failed request. Unknown failures are never reported
 * as healthy or complete.
 */
export function describeFailure(error: unknown): FailureState {
  const isApiError = error instanceof ApiError;
  const status = isApiError ? error.status : undefined;
  const kind = isApiError ? kindOfStatus(error.status, isMarkedInvalid(error.data)) : "unavailable";
  const state = failureStates[kind];
  return { kind, status, title: state.title, detail: state.detail };
}
