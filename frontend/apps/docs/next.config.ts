import type { NextConfig } from 'next';

import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ['fumadocs-core', 'fumadocs-openapi', 'fumadocs-ui', 'lucide-react'],
  },
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
};

export default withMDX(nextConfig);
