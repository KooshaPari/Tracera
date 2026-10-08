import assert from "node:assert/strict";
import { test } from "node:test";
import { verifyGatewayHealth } from "./verify-gateway-health.mjs";

const headers = "HTTP/2 200\r\nContent-Type: application/json\r\nX-Tracera-Gateway-Mode: proxy\r\nAccess-Control-Allow-Origin: https://app.invalid\r\n";
test("real backend JSON health and readiness pass", () => {
  verifyGatewayHealth(200, headers, '{"status":"ok","service":"tracera-server"}', "ok", "https://app.invalid");
  verifyGatewayHealth(200, headers, '{"status":"ready","service":"tracera-server"}', "ready", "https://app.invalid");
});
test("legacy synthetic health with no gateway provenance fails", () => {
  assert.throws(() => verifyGatewayHealth(200, headers.replace("X-Tracera-Gateway-Mode: proxy\r\n", ""), '{"status":"ok","service":"tracera-server"}'));
});
test("Cloudflare login HTML cannot count as success", () => {
  assert.throws(() => verifyGatewayHealth(200, headers.replace("application/json", "text/html"), "<html>cloudflareaccess</html>"));
  assert.throws(() => verifyGatewayHealth(302, headers, '{"status":"ok","service":"tracera-server"}'));
});
test("CORS headers on an unavailable service cannot count as success", () => {
  assert.throws(() => verifyGatewayHealth(503, headers, '{"status":"ok","service":"tracera-server"}', "ok", "https://app.invalid"));
});
test("wrong origin or malformed/wrong JSON fail", () => {
  assert.throws(() => verifyGatewayHealth(200, headers, '{"status":"ok","service":"tracera-server"}', "ok", "https://different.invalid"));
  assert.throws(() => verifyGatewayHealth(200, headers, "broken"));
  assert.throws(() => verifyGatewayHealth(200, headers, '{"status":"ready","service":"tracera-server"}'));
});
