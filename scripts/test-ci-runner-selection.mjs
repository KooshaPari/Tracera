import { readFile } from 'node:fs/promises';

const files = ['.github/workflows/ci.yml', '.github/workflows/infisical.yml'];
const workflows = Object.fromEntries(
  await Promise.all(files.map(async (file) => [file, await readFile(file, 'utf8')])),
);

const failures = [];
for (const file of files) {
  const source = workflows[file];
  if (!source.includes('workflow_dispatch:')) failures.push(`${file}: missing workflow_dispatch`);
  if (!source.includes('runner:')) failures.push(`${file}: missing runner input`);
  if (!source.includes("default: desk")) failures.push(`${file}: manual dispatch must default to desk`);
  if (/runs-on:\\s*(ubuntu-|windows-|macos-|\\$\\{\\{\\s*inputs\\.runner)/.test(source)) failures.push(`${file}: hosted fallback forbidden`);
  if (!source.includes("runs-on: [self-hosted, podman, wsl2, fedora44]")) failures.push(`${file}: missing desk labels`);
  if (/runs-on:\s*blacksmith-/.test(source)) {
    failures.push(`${file}: hard-coded Blacksmith runner remains`);
  }
}

const ci = workflows['.github/workflows/ci.yml'];
for (const job of [
  'rust-lint',
  'rust-test',
  'rust-build',
  'python-lint',
  'python-test',
  'go-lint',
  'go-test',
  'typescript-lint',
  'typescript-test',
]) {
  const block = ci.match(new RegExp(`\\n  ${job}:\\n([\\s\\S]*?)(?=\\n  [a-z0-9-]+:|$)`))?.[1] ?? '';
  if (!block.includes("runs-on: [self-hosted, podman, wsl2, fedora44]")) {
    failures.push(`ci.yml: ${job} is not bound to the desk runner`);
  }
}

if (!workflows['.github/workflows/infisical.yml'].includes("if: github.event_name != 'pull_request'")) {
  failures.push('infisical.yml: pull requests must not require unavailable secret credentials');
}

if (failures.length) {
  console.error(failures.map((failure) => `FAIL: ${failure}`).join('\n'));
  process.exit(1);
}

console.log('CI runner selection contracts validated.');
