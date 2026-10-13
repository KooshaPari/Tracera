import assert from "node:assert/strict";
import { test } from "node:test";
import { verifyDeployedApp } from "./verify-deployed-app.mjs";

const app =
  '<div id="root"></div><script type="module" crossorigin src="/assets/index-abc.js"></script>';
test("built SPA response passes", () => verifyDeployedApp(200, app));
test("login pages fail even with a root and successful HTTP status", () => {
  assert.throws(
    () =>
      verifyDeployedApp(
        200,
        `${app}<a href="https://vercel.com/login">login</a>`,
      ),
    /protection/,
  );
});
test("empty bodies and placeholder pages fail", () => {
  assert.throws(() => verifyDeployedApp(200, ""), /empty/);
  assert.throws(
    () => verifyDeployedApp(200, `${app}Frontend scaffolding coming soon.`),
    /placeholder/,
  );
});
test("non-success responses fail even when they contain SPA markup", () => {
  for (const status of [0, 302, 401, 403, 500])
    assert.throws(() => verifyDeployedApp(status, app), /HTTP/);
});
test("root-only shells and unbuilt development entrypoints fail", () => {
  assert.throws(
    () => verifyDeployedApp(200, '<div id="root"></div>'),
    /module/,
  );
  assert.throws(
    () =>
      verifyDeployedApp(
        200,
        '<div id="root"></div><script type="module" src="/src/main.tsx"></script>',
      ),
    /module/,
  );
  assert.throws(
    () =>
      verifyDeployedApp(
        200,
        '<script type="module" src="/assets/index.js"></script>',
      ),
    /root/,
  );
});
test("attribute order and single quotes are supported", () => {
  verifyDeployedApp(
    200,
    "<div id='root'></div><script src='/assets/index.js' type='module'></script>",
  );
});
