import { createMDX } from 'fumadocs-mdx/next';
import withPWA from '@ducanh2912/next-pwa';
import withBundleAnalyzer from '@next/bundle-analyzer';

const withMDX = createMDX();

// Bundle analyzer setup (enable with ANALYZE=true)
const bundleAnalyzer = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

// PWA configuration for offline support and caching
const pwaConfig = withPWA({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
  cacheOnFrontEndNav: true,
  aggressiveFrontEndNavCaching: true,
  reloadOnOnline: true,
  swcMinify: true,
  workboxOptions: {
    disableDevLogs: true,
    runtimeCaching: [
      {
        urlPattern: /^https?.*/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'offlineCache',
          expiration: {
            maxEntries: 200,
            maxAgeSeconds: 86400, // 1 day
          },
        },
      },
    ],
  },
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],

  images: {
    unoptimized: process.env.NODE_ENV === 'development',
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'api.tracertm.com',
      },
    ],
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
      '@radix-ui/react-dropdown-menu',
      'cmdk',
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
          chunks: 'all',
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
            // Radix UI components
            radix: {
              test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
              name: 'radix-ui',
              priority: 30,
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
        },
      };
    }

    return config;
  },

  // PHASE 2: Static Generation Configuration
  // Uncomment for full static export:
  // output: 'export',

  // Aggressive caching headers for static assets
  async headers() {
    return [
      {
        // Cache static assets immutably
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Cache images for 1 year
        source: '/images/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        // Cache HTML pages with revalidation
        source: '/:path*',
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

export default pwaConfig(bundleAnalyzer(withMDX(nextConfig)));
