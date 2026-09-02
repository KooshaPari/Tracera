#!/usr/bin/env node

import { spawn } from "node:child_process";
import { constants as osConstants } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_DEADLINE_MS = 14 * 60 * 1000;
const DEFAULT_GRACE_MS = 10 * 1000;
const SPAWN_ERROR_EXIT_CODE = 127;
const DEADLINE_EXIT_CODE = 124;

function usage() {
  return `Usage: node scripts/verify-vitest-termination.mjs [options] [-- command arg ...]

Runs \`npm run test:unit\` from the frontend directory by default.

Options:
  --deadline-ms N  Send SIGTERM after N milliseconds (default: ${DEFAULT_DEADLINE_MS})
  --grace-ms N     Send SIGKILL N milliseconds after SIGTERM (default: ${DEFAULT_GRACE_MS})
  --help           Show this help

Arguments after -- are passed directly to the child without a shell.`;
}

function parseMilliseconds(value, option) {
  const milliseconds = Number(value);
  if (!Number.isSafeInteger(milliseconds) || milliseconds <= 0) {
    throw new Error(`${option} must be a positive integer`);
  }
  return milliseconds;
}

function parseArguments(arguments_) {
  let deadlineMs = DEFAULT_DEADLINE_MS;
  let graceMs = DEFAULT_GRACE_MS;
  let command = "npm";
  let commandArguments = ["run", "test:unit"];

  for (let index = 0; index < arguments_.length; index += 1) {
    const argument = arguments_[index];
    if (argument === "--help") return { help: true };
    if (argument === "--") {
      const override = arguments_.slice(index + 1);
      if (override.length === 0) throw new Error("-- requires a command");
      [command, ...commandArguments] = override;
      break;
    }
    if (argument.startsWith("--")) {
      const { deadline, grace } = parseDeadlineGraceOption(argument, arguments_, index);
      if (deadline !== undefined) { deadlineMs = deadline; index += 1; continue; }
      if (grace !== undefined) { graceMs = grace; index += 1; continue; }
    }
    throw new Error(`Unknown option: ${argument}`);
  }

  return { command, commandArguments, deadlineMs, graceMs, help: false };
}

function parseDeadlineGraceOption(argument, arguments_, index) {
  if (argument !== "--deadline-ms" && argument !== "--grace-ms") return {};
  const value = arguments_[index + 1];
  if (value === undefined) throw new Error(`${argument} requires a value`);
  const milliseconds = parseMilliseconds(value, argument);
  return argument === "--deadline-ms"
    ? { deadline: milliseconds }
    : { grace: milliseconds };
}

function signalExitCode(signal) {
  const signalNumber = osConstants.signals[signal];
  return typeof signalNumber === "number" ? 128 + signalNumber : 1;
}

async function supervise(options) {
  const frontendDirectory = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const useProcessGroup = process.platform !== "win32";
  const child = spawn(options.command, options.commandArguments, {
    cwd: frontendDirectory,
    detached: useProcessGroup,
    shell: false,
    stdio: "inherit",
  });

  let deadlineReached = false;
  let deadlineTimer;
  let graceTimer;

  const signalChild = (signal) => {
    if (!child.pid || child.exitCode !== null || child.signalCode !== null) return;
    try {
      if (useProcessGroup) process.kill(-child.pid, signal);
      else child.kill(signal);
    } catch (error) {
      if (error?.code !== "ESRCH") throw error;
    }
  };

  return new Promise((resolve) => {
    let settled = false;
    const forwardedSignals = ["SIGINT", "SIGTERM"];
    const signalHandlers = new Map(
      forwardedSignals.map((signal) => [signal, () => signalChild(signal)]),
    );

    const finish = (exitCode) => {
      if (settled) return;
      settled = true;
      clearTimeout(deadlineTimer);
      clearTimeout(graceTimer);
      for (const [signal, handler] of signalHandlers) process.off(signal, handler);
      resolve(exitCode);
    };

    for (const [signal, handler] of signalHandlers) process.once(signal, handler);

    child.once("error", (error) => {
      console.error(`[vitest-supervisor] failed to spawn ${options.command}: ${error.message}`);
      finish(SPAWN_ERROR_EXIT_CODE);
    });

    child.once("exit", (code, signal) => {
      if (deadlineReached) finish(DEADLINE_EXIT_CODE);
      else if (code !== null) finish(code);
      else finish(signalExitCode(signal));
    });

    deadlineTimer = setTimeout(() => {
      deadlineReached = true;
      console.error(
        `[vitest-supervisor] deadline reached after ${options.deadlineMs}ms; sending SIGTERM`,
      );
      signalChild("SIGTERM");
      graceTimer = setTimeout(() => {
        console.error(
          `[vitest-supervisor] child still running after ${options.graceMs}ms; sending SIGKILL`,
        );
        signalChild("SIGKILL");
      }, options.graceMs);
    }, options.deadlineMs);
  });
}

let options;
try {
  options = parseArguments(process.argv.slice(2));
} catch (error) {
  console.error(`[vitest-supervisor] ${error.message}`);
  console.error(usage());
  process.exitCode = 2;
}

if (options?.help) {
  console.log(usage());
} else if (options) {
  process.exitCode = await supervise(options);
}
