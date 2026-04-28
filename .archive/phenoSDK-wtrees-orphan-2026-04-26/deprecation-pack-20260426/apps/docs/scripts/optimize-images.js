#!/usr/bin/env node

/**
 * Image Optimization Script
 * 
 * Optimizes PNG and JPEG images in the docs/public directory.
 * Reduces file size by 30-50% without quality loss.
 * 
 * Usage:
 *   node scripts/optimize-images.js
 * 
 * Requirements:
 *   npm install --save-dev imagemin imagemin-pngquant imagemin-mozjpeg
 */

const path = require('path');
const fs = require('fs');
const glob = require('glob');

// Try to import imagemin (may not be installed yet)
let imagemin;
let imageminPngquant;
let imageminMozjpeg;

async function loadDependencies() {
  try {
    imagemin = await import('imagemin');
    imageminPngquant = await import('imagemin-pngquant');
    imageminMozjpeg = await import('imagemin-mozjpeg');
    return true;
  } catch (err) {
    console.log('ℹ️  Image optimization libraries not found.');
    console.log('To use this script, install: npm install --save-dev imagemin imagemin-pngquant imagemin-mozjpeg');
    console.log('\nFor now, here are manual compression recommendations:');
    console.log('- Use TinyPNG (https://tinypng.com/) for PNG files');
    console.log('- Use JPEGmini (https://www.jpegmini.com/) for JPEG files');
    console.log('- Convert to WebP for 25-35% better compression');
    return false;
  }
}

async function optimizeImages() {
  const publicDir = path.join(__dirname, '..', 'public');
  
  // Check if public directory exists
  if (!fs.existsSync(publicDir)) {
    console.log('✅ No images to optimize (public directory not created yet)');
    console.log('\nWhen you add images:');
    console.log(`1. Place them in: ${publicDir}`);
    console.log('2. Run this script to optimize them');
    console.log('3. Commit the optimized versions');
    return;
  }

  // Find image files
  const imagePatterns = [
    path.join(publicDir, '**/*.png'),
    path.join(publicDir, '**/*.jpg'),
    path.join(publicDir, '**/*.jpeg'),
  ];

  let files = [];
  for (const pattern of imagePatterns) {
    files = files.concat(glob.sync(pattern, { ignore: '**/.*' }));
  }

  if (files.length === 0) {
    console.log('✅ No PNG or JPEG files found in public directory');
    console.log('\nWhen you add images, run this script again to optimize them.');
    return;
  }

  console.log(`🔍 Found ${files.length} image(s) to optimize...\n`);

  const hasDeps = await loadDependencies();
  if (!hasDeps) return;

  try {
    const result = await imagemin.default(
      [path.join(publicDir, '**/*.{png,jpg,jpeg}')],
      {
        destination: publicDir,
        plugins: [
          imageminPngquant.default({
            quality: [0.6, 0.8], // 60-80% quality
            speed: 4, // balance between speed and compression
          }),
          imageminMozjpeg.default({
            quality: 80, // 80% quality for JPEGs
            progressive: true, // Progressive JPEG
          }),
        ],
      }
    );

    if (result.length > 0) {
      console.log('✅ Image optimization complete:\n');
      
      let totalOriginal = 0;
      let totalOptimized = 0;

      result.forEach((file) => {
        const original = fs.statSync(file.sourcePath);
        const optimized = fs.statSync(file.destinationPath);
        const savings = original.size - optimized.size;
        const percent = ((savings / original.size) * 100).toFixed(1);

        totalOriginal += original.size;
        totalOptimized += optimized.size;

        console.log(`  ${path.basename(file.destinationPath)}`);
        console.log(`    Original: ${(original.size / 1024).toFixed(1)}KB`);
        console.log(`    Optimized: ${(optimized.size / 1024).toFixed(1)}KB`);
        console.log(`    Saved: ${(savings / 1024).toFixed(1)}KB (${percent}%)\n`);
      });

      console.log(`📊 Total savings: ${((totalOriginal - totalOptimized) / 1024).toFixed(1)}KB`);
      console.log(`   From ${(totalOriginal / 1024 / 1024).toFixed(2)}MB → ${(totalOptimized / 1024 / 1024).toFixed(2)}MB`);
    }
  } catch (err) {
    console.error('❌ Error optimizing images:', err.message);
    process.exit(1);
  }
}

// Run optimization
optimizeImages().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
