import type { NextConfig } from 'next';
import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

const nextConfig: NextConfig = {
  reactStrictMode: true,
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],

  // Note: Static export disabled to enable full Fumadocs features
  // For static export, remove the following comment and rebuild
  // output: 'export',

  images: {
    // Enable image optimization for production
    unoptimized: process.env.NODE_ENV === 'development',
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.tracertm.com',
      },
    ],
  },

  // Trailing slashes for better static file structure
  trailingSlash: true,
};

export default withMDX(nextConfig);
