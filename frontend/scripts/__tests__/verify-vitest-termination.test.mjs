import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const testDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(testDirectory, "../..");
const supervisorPath = path.resolve(frontendDirectory, "scripts/verify-vitest-termination.mjs");
const packageJson = JSON.parse(
  readFileSync(path.resolve(frontendDirectory, "package.json"), "utf8"),
);

function runSupervisor(arguments_, timeout = 5000) {
  return spawnSync(process.execPath, [supervisorPath, ...arguments_], {
    cwd: frontendDirectory,
    encoding: "utf8",
    timeout,
  });
}

test("preserves a successful child exit code", () => {
  const result = runSupervisor(["--", process.execPath, "-e", "process.exit(0)"]);
  assert.equal(result.status, 0, result.stderr);
});

test("preserves a failing child exit code", () => {
  const result = runSupervisor(["--", process.execPath, "-e", "process.exit(7)"]);
  assert.equal(result.status, 7, result.stderr);
});

test("uses a non-deadline code for spawn failures", () => {
  const result = runSupervisor(["--", "/definitely/missing/tracera-command"]);
  assert.equal(result.status, 127, result.stderr);
});

test("returns 124, escalates, and removes a child process group after the deadline", () => {
  const temporaryDirectory = mkdtempSync(path.join(tmpdir(), "tracera-vitest-supervisor-"));
  const pidPath = path.join(temporaryDirectory, "child.pid");

  try {
    const childProgram = [
      "require('node:fs').writeFileSync(process.argv[1], String(process.pid));",
      "process.on('SIGTERM', () => {});",
      "setInterval(() => {}, 1000);",
    ].join("");
    const result = runSupervisor([
      "--deadline-ms",
      "150",
      "--grace-ms",
      "100",
      "--",
      process.execPath,
      "-e",
      childProgram,
      pidPath,
    ]);

    assert.equal(result.status, 124, result.stderr);
    assert.match(result.stderr, /sending SIGKILL/);
    const childPid = Number(readFileSync(pidPath, "utf8"));
    assert.throws(() => process.kill(childPid, 0), { code: "ESRCH" });
  } finally {
    rmSync(temporaryDirectory, { force: true, recursive: true });
  }
});

test("registers the bounded unit-test package command", () => {
  assert.equal(
    packageJson.scripts["test:unit:bounded"],
    "node scripts/verify-vitest-termination.mjs",
  );
});
