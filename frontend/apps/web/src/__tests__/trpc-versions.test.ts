import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import { describe, expect, it } from 'vitest';

const trpcPackages = ['@trpc/client', '@trpc/react-query', '@trpc/server'] as const;

async function readWebDependencies(): Promise<Record<(typeof trpcPackages)[number], string>> {
  const packageJsonPath = resolve(process.cwd(), 'package.json');
  const packageJson = JSON.parse(await readFile(packageJsonPath, 'utf8')) as {
    dependencies: Record<string, string>;
  };

  return Object.fromEntries(
    trpcPackages.map((packageName) => [packageName, packageJson.dependencies[packageName]]),
  ) as Record<(typeof trpcPackages)[number], string>;
}

describe('tRPC dependency versions', () => {
  it('keeps the client, React Query bridge, and server on the same release', async () => {
    const dependencies = await readWebDependencies();

    expect(new Set(Object.values(dependencies))).toEqual(new Set(['^11.18.0']));
  });
});
