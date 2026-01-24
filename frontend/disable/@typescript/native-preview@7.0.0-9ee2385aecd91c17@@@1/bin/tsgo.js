#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import getExePath from "#getExePath";

const exe = getExePath();

try {
	execFileSync(exe, process.argv.slice(2), { stdio: "inherit" });
} catch (e) {
	if (e.status) {
		process.exitCode = e.status;
	} else {
		throw e;
	}
}
