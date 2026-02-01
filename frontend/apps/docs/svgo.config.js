/**
 * SVGO Configuration
 *
 * Optimizes SVG files by removing unnecessary metadata and reducing file size.
 * Used for optimizing static SVG assets and icons.
 */

module.exports = {
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          // Disable removing viewBox as it's needed for responsive SVGs
          removeViewBox: false,
          // Keep important attributes for accessibility
          removeUnknownsAndDefaults: {
            keepAriaAttrs: true,
            keepRoleAttr: true,
          },
        },
      },
    },
    // Remove comments
    'removeComments',
    // Remove metadata
    'removeMetadata',
    // Remove editor data
    'removeEditorsNSData',
    // Remove unnecessary whitespace
    'cleanupListOfValues',
    // Minify colors
    'minifyStyles',
    // Remove empty attributes
    'removeEmptyAttrs',
    // Remove empty containers
    'removeEmptyContainers',
    // Clean up IDs
    'cleanupIds',
    // Merge paths
    'mergePaths',
    // Convert colors
    'convertColors',
    // Convert path data
    'convertPathData',
    // Sort attributes
    'sortAttrs',
    // Remove script elements for security
    'removeScriptElement',
    // Optimize transformations
    'convertTransform',
  ],
};
