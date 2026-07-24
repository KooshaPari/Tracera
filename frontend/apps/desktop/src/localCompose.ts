/** Opt-in lifecycle for the desktop-hosted Tracera Compose stack. */
export const LOCAL_PORT = 18081;
export const LOCAL_URL = `http://127.0.0.1:${LOCAL_PORT}`;
export type CommandRunner = (command: string[], options: { cwd: string; env: Record<string, string> }) => { exited: Promise<number>; kill: () => void };
export type LocalComposeOptions = { repoRoot: string; envFile?: string; composeFile?: string; env?: Record<string, string | undefined>; run?: CommandRunner; fetchImpl?: typeof fetch; sleep?: (milliseconds: number) => Promise<void>; timeoutMs?: number };
const defaultSleep = (milliseconds: number) => new Promise((resolve) => setTimeout(resolve, milliseconds));
function commandRunner(command: string[], options: { cwd: string; env: Record<string, string> }) { return Bun.spawn(command, { cwd: options.cwd, env: options.env, stdout: "ignore", stderr: "pipe" }); }
function composeCommand(options: LocalComposeOptions): { command: string[]; env: Record<string, string> } {
  const env = Object.fromEntries(Object.entries({ ...process.env, ...options.env }).filter((entry): entry is [string, string] => entry[1] !== undefined));
  const envFile = options.envFile ?? `${options.repoRoot}/.env.local`;
  const composeFile = options.composeFile ?? `${options.repoRoot}/docker-compose.local.yml`;
  const port = env.TRACERA_LOCAL_PORT ?? String(LOCAL_PORT);
  if (port === "8080") throw new Error("refusing port 8080; it is reserved for Grapheon");
  return { command: ["docker", "compose", "--env-file", envFile, "-f", composeFile, "up", "-d"], env };
}
export async function startLocalCompose(options: LocalComposeOptions): Promise<() => Promise<void>> {
  const { command, env } = composeCommand(options);
  const run = options.run ?? commandRunner;
  const process = run(command, { cwd: options.repoRoot, env });
  const exitCode = await process.exited;
  if (exitCode !== 0) throw new Error(`docker compose up failed with exit code ${exitCode}`);
  const fetchImpl = options.fetchImpl ?? fetch;
  const sleep = options.sleep ?? defaultSleep;
  const deadline = Date.now() + (options.timeoutMs ?? 180_000);
  while (Date.now() < deadline) {
    try {
      const [health, ready] = await Promise.all([fetchImpl(`${LOCAL_URL}/health`), fetchImpl(`${LOCAL_URL}/ready`)]);
      if (health.ok && ready.ok && (await health.json() as { status?: string }).status === "ok" && (await ready.json() as { status?: string }).status === "ready") break;
    } catch { /* service is still starting */ }
    await sleep(2_000);
  }
  if (Date.now() >= deadline) throw new Error(`Tracera backend did not become ready at ${LOCAL_URL}`);
  return async () => {
    const down = run(["docker", "compose", "--env-file", options.envFile ?? `${options.repoRoot}/.env.local`, "-f", options.composeFile ?? `${options.repoRoot}/docker-compose.local.yml`, "down"], { cwd: options.repoRoot, env });
    const code = await down.exited;
    if (code !== 0) throw new Error(`docker compose down failed with exit code ${code}`);
  };
}
