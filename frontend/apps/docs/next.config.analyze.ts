import { NextConfig } from 'next';
import createMDX from 'fumadocs-mdx/config';
import BundleAnalyzer from '@next/bundle-analyzer';

const withMDX = createMDX();

const withBundleAnalyzer = BundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default withBundleAnalyzer(withMDX(nextConfig));
