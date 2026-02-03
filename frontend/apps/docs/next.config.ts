import type { NextConfig } from 'next';
import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

// Bundle analyzer setup (enable with ANALYZE=true)
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

const nextConfig: NextConfig = {
  // Disable Turbopack to avoid Next.js 16 + fumadocs-mdx compatibility issues
  // See: https://github.com/vercel/next.js/issues/84748
  turbo: false,

  reactStrictMode: true,
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],

  images: {
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
    dangerouslyAllowSVG: true,
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    formats: ['image/avif', 'image/webp'],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.tracertm.com',
      },
    ],
    unoptimized: process.env.NODE_ENV === 'development',
  },

  trailingSlash: false,

  // PHASE 1: Aggressive Bundle Optimization
  experimental: {
    // Optimize package imports to reduce bundle size
    optimizePackageImports: [
      'fumadocs-ui',
      'fumadocs-core',
      'fumadocs-openapi',
      'lucide-react',
    ],
  },

  // Enable SWC minification (faster and smaller bundles)
  swcMinify: true,

  // Production source maps (disabled for smaller bundles)
  productionBrowserSourceMaps: false,

  // Aggressive code splitting and tree shaking
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      // Enable tree shaking
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: true,

        // Manual chunk splitting for better caching
        splitChunks: {
          cacheGroups: {
            // Separate React into its own chunk
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              name: 'react',
              priority: 40,
              reuseExistingChunk: true,
            },
            // Fumadocs libraries
            fumadocs: {
              test: /[\\/]node_modules[\\/](fumadocs-ui|fumadocs-core|fumadocs-openapi|fumadocs-mdx)[\\/]/,
              name: 'fumadocs',
              priority: 35,
              reuseExistingChunk: true,
            },
            // Lucide icons
            lucide: {
              test: /[\\/]node_modules[\\/]lucide-react[\\/]/,
              name: 'lucide-icons',
              priority: 25,
              reuseExistingChunk: true,
            },
            // Common vendor libraries
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendor',
              priority: 20,
              reuseExistingChunk: true,
            },
          },
          chunks: 'all',
        },
      };
    }

    return config;
  },

  // Aggressive caching headers for static assets
  async headers() {
    return [
      {
        // Cache static assets immutably
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
        source: '/_next/static/:path*',
      },
      {
        // Cache images for 1 year
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
        source: '/images/:path*',
      },
      {
        // Cache HTML pages with revalidation
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=3600, stale-while-revalidate=86400',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
        source: '/:path*',
      },
    ];
  },

  // Generate ETag for cache validation
  generateEtags: true,

  // Compress responses
  compress: true,

  // PoweredBy header removal for security
  poweredByHeader: false,
};

export default withBundleAnalyzer(withMDX(nextConfig));
