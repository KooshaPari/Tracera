import { describe, expect, test } from "bun:test";
import { LOCAL_URL, startLocalCompose, type CommandRunner } from "../src/compose";

function runner(commands: string[][]): CommandRunner {
  return (command) => {
    commands.push(command);
    return { exited: Promise.resolve(0), kill: () => undefined };
  };
}

describe("desktop local Compose lifecycle", () => {
  test("starts, waits for health, and stops with an injected runner", async () => {
    const commands: string[][] = [];
    const stop = await startLocalCompose({
      repoRoot: "/tmp/tracera",
      run: runner(commands),
      fetchImpl: async (input) => new Response(JSON.stringify({ status: String(input).endsWith("/ready") ? "ready" : "ok" }), { status: 200 }),
      timeoutMs: 100,
    });
    await stop();
    expect(commands[0]).toEqual(["docker", "compose", "--env-file", "/tmp/tracera/.env.local", "-f", "/tmp/tracera/docker-compose.local.yml", "up", "-d"]);
    expect(commands[1]?.at(-1)).toBe("down");
    expect(LOCAL_URL).toBe("http://127.0.0.1:18081");
  });

  test("rejects Grapheon port 8080 before spawning", async () => {
    await expect(startLocalCompose({ repoRoot: "/tmp/tracera", env: { TRACERA_LOCAL_PORT: "8080" }, run: runner([]) })).rejects.toThrow("reserved for Grapheon");
  });
});
