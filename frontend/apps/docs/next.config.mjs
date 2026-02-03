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
  aggressiveFrontEndNavCaching: true,
  cacheOnFrontEndNav: true,
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  reloadOnOnline: true,
  skipWaiting: true,
  workboxOptions: {
    disableDevLogs: true,
    runtimeCaching: [
      {
        handler: 'NetworkFirst',
        options: {
          cacheName: 'offlineCache',
          expiration: {
            maxAgeSeconds: 86_400,
            maxEntries: 200, // 1 day
          },
        },
        urlPattern: /^https?.*/,
      },
    ],
  },
});

/** @type {import('next').NextConfig} */
const nextConfig = {
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
        hostname: 'api.tracertm.com',
        protocol: 'https',
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
      '@radix-ui/react-dropdown-menu',
      'cmdk',
    ],
  },

  // Enable SWC minification (faster and smaller bundles)

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
              name: 'react',
              priority: 40,
              reuseExistingChunk: true,
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
            },
            // Fumadocs libraries
            fumadocs: {
              name: 'fumadocs',
              priority: 35,
              reuseExistingChunk: true,
              test: /[\\/]node_modules[\\/](fumadocs-ui|fumadocs-core|fumadocs-openapi|fumadocs-mdx)[\\/]/,
            },
            // Radix UI components
            radix: {
              name: 'radix-ui',
              priority: 30,
              reuseExistingChunk: true,
              test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
            },
            // Lucide icons
            lucide: {
              name: 'lucide-icons',
              priority: 25,
              reuseExistingChunk: true,
              test: /[\\/]node_modules[\\/]lucide-react[\\/]/,
            },
            // Common vendor libraries
            vendor: {
              name: 'vendor',
              priority: 20,
              reuseExistingChunk: true,
              test: /[\\/]node_modules[\\/]/,
            },
          },
          chunks: 'all',
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

export default pwaConfig(bundleAnalyzer(withMDX(nextConfig)));
