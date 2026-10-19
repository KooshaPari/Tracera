import { ApiError } from "./client-errors";

export async function requireAvailable<T>(
  request: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await request;
  if (!response.ok)
    throw new ApiError(
      response.status,
      response.status === 501 ? "Not implemented yet" : "Service unavailable",
      error,
    );
  if (data === undefined) throw new ApiError(502, "Invalid response from service");
  return data;
}

export function invalidResponse(): never {
  throw new ApiError(502, "Invalid response from service");
}
