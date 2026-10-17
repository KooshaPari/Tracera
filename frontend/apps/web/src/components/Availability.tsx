import { ApiError } from "@/api/client-errors";

export function NotImplemented() {
  return (
    <div role="status">
      <h2>Not implemented yet</h2>
      <p>This capability is not available yet.</p>
    </div>
  );
}

export function Unavailable({ error }: { error?: unknown }) {
  if (error instanceof ApiError && error.status === 501) return <NotImplemented />;
  return (
    <div role="alert">
      <h2>Service unavailable</h2>
      <p>Please try again later.</p>
    </div>
  );
}
