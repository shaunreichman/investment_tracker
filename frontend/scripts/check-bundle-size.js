#!/usr/bin/env node

/**
 * Bundle Size Monitoring Script
 * 
 * This script provides a simple way to check bundle sizes during development
 * and can be integrated into CI/CD pipelines for performance tracking.
 * 
 * Usage:
 *   node scripts/check-bundle-size.js
 *   npm run check-bundle-size
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BUILD_DIR = path.join(__dirname, '../build');
const STATIC_DIR = path.join(BUILD_DIR, 'static');
const MAX_BUNDLE_SIZE = 500 * 1024; // 500KB warning threshold
const MAX_CHUNK_SIZE = 200 * 1024;  // 200KB warning threshold

/**
 * Format bytes to human readable format
 */
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Check if a file is a JavaScript bundle
 */
function isJavaScriptBundle(filename) {
  return filename.endsWith('.js') && !filename.includes('.map');
}

/**
 * Analyze bundle sizes
 */
function analyzeBundleSizes() {
  console.log('📦 Bundle Size Analysis');
  console.log('========================\n');
  
  if (!fs.existsSync(BUILD_DIR)) {
    console.log('❌ Build directory not found. Run "npm run build" first.');
    return;
  }
  
  if (!fs.existsSync(STATIC_DIR)) {
    console.log('❌ Static directory not found in build.');
    return;
  }
  
  const jsFiles = fs.readdirSync(STATIC_DIR)
    .filter(file => isJavaScriptBundle(file))
    .map(file => ({
      name: file,
      path: path.join(STATIC_DIR, file),
      size: fs.statSync(path.join(STATIC_DIR, file)).size
    }))
    .sort((a, b) => b.size - a.size);
  
  if (jsFiles.length === 0) {
    console.log('❌ No JavaScript bundles found.');
    return;
  }
  
  let totalSize = 0;
  let warnings = 0;
  
  console.log('📊 Bundle Analysis Results:\n');
  
  jsFiles.forEach(file => {
    const sizeFormatted = formatBytes(file.size);
    const isLarge = file.size > MAX_BUNDLE_SIZE;
    const isChunkLarge = file.size > MAX_CHUNK_SIZE;
    
    if (isLarge) {
      console.log(`⚠️  ${file.name}: ${sizeFormatted} (LARGE BUNDLE)`);
      warnings++;
    } else if (isChunkLarge) {
      console.log(`⚠️  ${file.name}: ${sizeFormatted} (LARGE CHUNK)`);
      warnings++;
    } else {
      console.log(`✅ ${file.name}: ${sizeFormatted}`);
    }
    
    totalSize += file.size;
  });
  
  console.log('\n📈 Summary:');
  console.log(`   Total JavaScript: ${formatBytes(totalSize)}`);
  console.log(`   Bundle count: ${jsFiles.length}`);
  console.log(`   Warnings: ${warnings}`);
  
  if (warnings > 0) {
    console.log('\n💡 Recommendations:');
    console.log('   - Consider code splitting for large bundles');
    console.log('   - Review lazy loading implementation');
    console.log('   - Check for unused dependencies');
    console.log('   - Consider tree shaking optimization');
  }
  
  // Check for CSS files too
  const cssFiles = fs.readdirSync(STATIC_DIR)
    .filter(file => file.endsWith('.css'))
    .map(file => ({
      name: file,
      size: fs.statSync(path.join(STATIC_DIR, file)).size
    }));
  
  if (cssFiles.length > 0) {
    const totalCSS = cssFiles.reduce((sum, file) => sum + file.size, 0);
    console.log(`\n🎨 CSS Total: ${formatBytes(totalCSS)}`);
  }
  
  console.log('\n✅ Bundle size check completed.');
}

// Run the analysis
if (require.main === module) {
  analyzeBundleSizes();
}

module.exports = { analyzeBundleSizes };
