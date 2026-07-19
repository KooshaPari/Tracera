#!/usr/bin/env node

import fs from 'node:fs';

const appPath = new URL('../apps/web/src/App.jsx', import.meta.url);
const topNavPath = new URL('../apps/web/src/components/TopNav.jsx', import.meta.url);

const appSource = fs.readFileSync(appPath, 'utf8');
const topNavSource = fs.readFileSync(topNavPath, 'utf8');

const checks = [
  {
    name: 'TopNav includes trace entry',
    ok: /{ id:\s*['\"]trace['\"],\s*label:\s*['\"]Evidence['\"]\s*}/.test(topNavSource),
  },
  {
    name: 'TopNav onNavigate callback wired',
    ok: /onClick=\{\(\) => onNavigate\(page\.id\)\}/.test(topNavSource),
  },
  {
    name: 'App maps trace id to TraceViewer',
    ok: /page\s*===\s*['\"]trace['\"]/.test(appSource),
  },
  {
    name: 'App uses fallback dashboard route',
    ok: /:\s*<Dashboard\s*\/>/.test(appSource),
  },
];

const failures = checks.filter((check) => !check.ok);

for (const check of checks) {
  if (check.ok) {
    console.log(`PASS ${check.name}`);
  } else {
    console.error(`FAIL ${check.name}`);
  }
}

if (failures.length > 0) {
  console.error(`\nUI route mapping check failed (${failures.length} issue(s)).`);
  process.exitCode = 1;
}

console.log('\nUI route mapping check: PASS');
