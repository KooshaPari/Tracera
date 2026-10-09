import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

export function verifyGatewayHealth(code, rawHeaders, body, expected = "ok", origin) {
  if (Number(code) < 200 || Number(code) >= 300) throw new Error("Gateway returned non-success HTTP status");
  const headers = new Map(rawHeaders.trim().split(/\r?\n/).flatMap(line => {
    const separator = line.indexOf(":");
    return separator < 0 ? [] : [[line.slice(0, separator).toLowerCase(), line.slice(separator + 1).trim()]];
  }));
  if (headers.get("x-tracera-gateway-mode") !== "proxy") throw new Error("Gateway did not forward a real upstream response");
  if (!headers.get("content-type")?.includes("application/json")) throw new Error("Health response is not JSON");
  const payload = JSON.parse(body);
  if (payload?.status !== expected || payload?.service !== "tracera-server") throw new Error("Tracera backend did not report the expected health status");
  if (origin && ![origin, "*"].includes(headers.get("access-control-allow-origin"))) throw new Error("CORS does not allow the deployed frontend");
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [code, headersPath, bodyPath, expected, origin] = process.argv.slice(2);
  verifyGatewayHealth(code, readFileSync(headersPath, "utf8"), readFileSync(bodyPath, "utf8"), expected, origin);
  console.log("PASS: real backend health and frontend CORS verified");
}
