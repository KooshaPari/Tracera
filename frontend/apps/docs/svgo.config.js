/**
 * SVGO Configuration
 *
 * Optimizes SVG files by removing unnecessary metadata and reducing file size.
 * Used for optimizing static SVG assets and icons.
 */

export default {
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          removeUnknownsAndDefaults: {
            keepAriaAttrs: true,
            keepRoleAttr: true,
          },
          // Disable removing viewBox as it's needed for responsive SVGs
          removeViewBox: false,
        },
      },
    },
    'removeComments',
    'removeMetadata',
    'removeEditorsNSData',
    'cleanupListOfValues',
    'minifyStyles',
    'removeEmptyAttrs',
    'removeEmptyContainers',
    'cleanupIds',
    'mergePaths',
    'convertColors',
    'convertPathData',
    'sortAttrs',
    'removeScriptElement',
    'convertTransform',
  ],
};
