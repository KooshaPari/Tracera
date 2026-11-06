import { describeFailure } from "@/api/availability";

export function NotImplemented() {
  return (
    <div role="status">
      <h2>Not implemented yet</h2>
      <p>This capability is not available yet.</p>
    </div>
  );
}

export function Unavailable({ error }: { error?: unknown }) {
  const state = describeFailure(error);
  if (state.kind === "not_implemented") return <NotImplemented />;
  return (
    <div role="alert" data-availability={state.kind}>
      <h2>{state.title}</h2>
      <p>{state.detail}</p>
    </div>
  );
}
