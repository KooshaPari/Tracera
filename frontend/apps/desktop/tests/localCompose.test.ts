import { describe, expect, test } from "bun:test";
import { LOCAL_URL, startBundle, type CommandRunner } from "../src/compose";
import {
  DEFAULT_TARGET_URL,
  LEGACY_BUNDLE_OVERRIDE,
  resolveTargetUrl,
} from "../src/target";

function runner(commands: string[][]): CommandRunner {
  return (command) => {
    commands.push(command);
    return { exited: Promise.resolve(0), kill: () => undefined };
  };
}

describe("desktop bundle lifecycle", () => {
  test("starts the bundled stack, waits for health, and stops with an injected runner", async () => {
    const commands: string[][] = [];
    const stop = await startBundle({
      cliPath: "/Applications/Tracera.app/Contents/Resources/tracera-bundle/bin/tracera",
      run: runner(commands),
      fetchImpl: async (input) => new Response(
        JSON.stringify(String(input).endsWith("/ready") ? { status: "ready" } : { status: "ok" }),
        { status: 200 },
      ),
      timeoutMs: 100,
    });
    await stop();
    expect(commands[0]?.[0]).toContain("tracera");
    expect(commands[0]).toContain("up");
    expect(commands[1]).toContain("down");
    expect(LOCAL_URL).toBe("http://127.0.0.1:18081");
  });

  test("exposes the local URL pointing at the bundled stack", () => {
    expect(LOCAL_URL).toBe("http://127.0.0.1:18081");
  });

  test("defaults packaged apps to the local stack, never a hosted site", () => {
    expect(DEFAULT_TARGET_URL).toBe("http://127.0.0.1:18000");
    expect(resolveTargetUrl({})).toBe("http://127.0.0.1:18000/");
    expect(resolveTargetUrl({ TRACERA_LOCAL_PORT: "19999" })).toBe("http://127.0.0.1:19999/");
    expect(resolveTargetUrl({ TRACERA_LOCAL_PORT: "18081" })).toBe("http://127.0.0.1:18000/");
  });

  test("allows an explicit hosted override without making it the default", () => {
    expect(resolveTargetUrl({ TRACERA_GATEWAY_URL: "http://127.0.0.1:18000" }))
      .toBe("http://127.0.0.1:18000");
    expect(resolveTargetUrl({ TRACERA_HOSTED_URL: "https://example.com/tracera/" }))
      .toBe("https://example.com/tracera/");
    expect(resolveTargetUrl({ TRACERA_URL: "https://staging.example.com" }))
      .toBe("https://staging.example.com");
  });

  test("permits the legacy bundle only with an explicit developer override", () => {
    expect(
      resolveTargetUrl({
        [LEGACY_BUNDLE_OVERRIDE]: "1",
        TRACERA_LOCAL_PORT: "18081",
      }),
    ).toBe("http://127.0.0.1:18081/");
  });

  test("rejects when no CLI path is provided and none can be resolved", async () => {
    await expect(
      startBundle({
        cliPath: "/nonexistent/tracera",
        run: runner([]),
        fetchImpl: async () => new Response("", { status: 503 }),
        timeoutMs: 50,
      }),
    ).rejects.toThrow();
  });
});
