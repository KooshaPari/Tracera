"use strict";
/* global Bun, Deno -- detection */
var globalThis = require("../internals/global-this");
var userAgent = require("../internals/environment-user-agent");
var classof = require("../internals/classof-raw");

var userAgentStartsWith = (string) =>
	userAgent.slice(0, string.length) === string;

module.exports = (() => {
	if (userAgentStartsWith("Bun/")) return "BUN";
	if (userAgentStartsWith("Cloudflare-Workers")) return "CLOUDFLARE";
	if (userAgentStartsWith("Deno/")) return "DENO";
	if (userAgentStartsWith("Node.js/")) return "NODE";
	if (globalThis.Bun && typeof Bun.version == "string") return "BUN";
	if (globalThis.Deno && typeof Deno.version == "object") return "DENO";
	if (classof(globalThis.process) === "process") return "NODE";
	if (globalThis.window && globalThis.document) return "BROWSER";
	return "REST";
})();
