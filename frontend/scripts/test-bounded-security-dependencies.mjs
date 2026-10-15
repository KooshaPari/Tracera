import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const require = createRequire(
  new URL("../apps/web/package.json", import.meta.url),
);
// Resolve Bun's isolated packages without requiring new direct dependencies.
const versions = {
  "brace-expansion": "5.0.12",
  dompurify: "3.4.16",
  "fast-uri": "3.1.8",
  "ip-address": "10.7.1",
  "postcss-selector-parser": "7.1.6",
  "smol-toml": "1.9.0",
  "source-map-js": "1.2.2",
  undici: "7.29.1",
};
const modules = {};
for (const [name, version] of Object.entries(versions)) {
  const directory = resolve(
    root,
    "node_modules/.bun",
    `${name}@${version}`,
    "node_modules",
    name,
  );
  assert.equal(
    JSON.parse(readFileSync(resolve(directory, "package.json"), "utf8"))
      .version,
    version,
  );
  modules[name] = require(directory);
}
const expand = modules["brace-expansion"].expand;
assert.deepEqual(expand("file-{a,b}.ts"), ["file-a.ts", "file-b.ts"]);
const { JSDOM } = require("jsdom");
const window = new JSDOM("").window;
try {
  const sanitize = modules.dompurify(window);
  assert.equal(
    sanitize.sanitize(
      '<img src=x onerror="alert(1)"><script>alert(1)</script>',
    ),
    '<img src="x">',
  );
} finally {
  window.close();
}
assert.equal(
  modules["fast-uri"].parse("https://example.com/a").host,
  "example.com",
);
assert.equal(
  new modules["ip-address"].Address6("2001:db8::1").correctForm(),
  "2001:db8::1",
);
assert.equal(
  modules["postcss-selector-parser"]().processSync(".item:hover"),
  ".item:hover",
);
assert.equal(modules["smol-toml"].parse("count = 3").count, 3);
const map = new modules["source-map-js"].SourceMapGenerator({ file: "out.js" });
map.addMapping({
  generated: { line: 1, column: 0 },
  original: { line: 1, column: 0 },
  source: "in.js",
});
assert.equal(JSON.parse(map.toString()).sources[0], "in.js");
const headers = new modules.undici.Headers({ "x-contract": "passed" });
assert.equal(headers.get("x-contract"), "passed");
console.log(
  JSON.stringify({
    packages: versions,
    versionChecks: 8,
    consumerSmokeChecks: 8,
    result: "pass",
  }),
);
