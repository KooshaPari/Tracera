import type { NextConfig } from 'next';

import { createMDX } from 'fumadocs-mdx/next';

const withMDXConfig = createMDX({
  configPath: './source.config.ts',
});

const nextConfig: NextConfig = {
  pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
};

export default withMDXConfig(nextConfig);
