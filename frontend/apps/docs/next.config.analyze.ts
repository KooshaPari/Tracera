import type { NextConfig } from 'next';
import createMDX from 'fumadocs-mdx/config';
import BundleAnalyzer from '@next/bundle-analyzer';

const withMDX = createMDX();

const withBundleAnalyzer = BundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  reactStrictMode: true,
};

export default withBundleAnalyzer(withMDX(nextConfig));
