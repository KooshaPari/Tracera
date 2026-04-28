import { createRequire } from 'node:module';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const configDir = dirname(fileURLToPath(import.meta.url));

function getAbsolutePath(value) {
  return dirname(require.resolve(`${value}/package.json`));
}

const config = {
  addons: [
    getAbsolutePath('@storybook/addon-docs'),
    '@storybook/addon-a11y',
    '@storybook/addon-coverage',
    '@storybook/addon-themes',
  ],

  core: {
    disableTelemetry: true,
  },

  docs: {
    autodocs: 'tag',
    defaultName: 'Documentation',
  },

  features: {
    buildStoriesJson: true,
    storyStoreV7: true,
  },

  framework: {
    name: getAbsolutePath('@storybook/react-vite'),
    options: {
      builder: {
        viteConfigPath: undefined,
      },
    },
  },

  stories: [
    '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)',
    '../../web/src/**/*.stories.@(js|jsx|mjs|ts|tsx)',
  ],

  typescript: {
    check: true,
    reactDocgen: 'react-docgen-typescript',
    reactDocgenTypescriptOptions: {
      propFilter: (prop) => {
        if (prop.parent) {
          return !prop.parent.fileName.includes('node_modules');
        }
        return true;
      },
      shouldExtractLiteralValuesFromEnum: true,
      shouldRemoveUndefinedFromOptional: true,
    },
  },
  viteFinal: async (viteConfig) => {
    const aliases = Array.isArray(viteConfig.resolve?.alias)
      ? viteConfig.resolve?.alias
      : viteConfig.resolve?.alias
        ? [viteConfig.resolve?.alias]
        : [];

    const sanitizedAliases = aliases.filter(
      (alias) => alias && typeof alias === 'object' && 'find' in alias && alias.find != null,
    );

    return {
      ...viteConfig,
      server: {
        ...(viteConfig.server || {}),
        watch: {
          ...(viteConfig.server?.watch || {}),
          usePolling: true,
          interval: 30000,
        },
      },
      resolve: {
        ...viteConfig.resolve,
        alias: [
          ...sanitizedAliases,
          {
            find: '@',
            replacement: resolve(configDir, '../../web/src'),
          },
        ],
      },
    };
  },
};

export default config;
