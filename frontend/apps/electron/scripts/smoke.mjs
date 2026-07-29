import { readFile } from "node:fs/promises";
const packageJson = JSON.parse(await readFile(new URL("../package.json", import.meta.url)));
if (packageJson.build?.appId !== "com.phenotype.tracera") throw new Error("invalid app id");
if (packageJson.main !== "dist/main.js") throw new Error(`invalid main entry: ${packageJson.main}`);
if (!packageJson.scripts["package:web"].includes("package-web.mjs")) throw new Error("missing SPA packaging step");
const source = await readFile(new URL("../src/main.ts", import.meta.url), "utf8");
if (!source.includes('join(__dirname, "web", "index.html")')) throw new Error("embedded SPA loader missing");
if (!source.includes("127.0.0.1:18000")) throw new Error("canonical gateway default missing");
console.log("OK: Electron metadata, canonical SPA packaging, and gateway shell contract");
