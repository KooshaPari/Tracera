#!/usr/bin/env node

const isDocker = require(".");

process.exitCode = isDocker() ? 0 : 2;
