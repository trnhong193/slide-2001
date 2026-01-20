const path = require('path');
const fs = require('fs');

// ============================================================================
// SLIDE FORMAT CONSTANTS - Use these for consistent formatting across all slides
// ============================================================================

const SLIDE_FORMAT = {
  // Dimensions
  width: 720,  // pt (16:9 aspect ratio)
  height: 405, // pt
  
  // Colors
  accentColor: '#00AEEF',  // viAct Blue
  textColor: '#FFFFFF',    // White
  backgroundColor: '#000000', // Black (for html background)
  
  // Typography
  fonts: {
    title: '28pt Arial, Helvetica, sans-serif',
    subtitle: '24pt Arial, Helvetica, sans-serif',
    body: '16pt Arial, Helvetica, sans-serif',
    small: '14pt Arial, Helvetica, sans-serif',
    tiny: '12pt Arial, Helvetica, sans-serif'
  },
  
  // Spacing
  spacing: {
    margin: '40pt',
    padding: '20pt',
    lineHeight: '1.4',
    bulletSpacing: '8pt'
  },
  
  // Border
  borderColor: '#00AEEF',
  borderWidth: '2pt'
};

// ============================================================================
// BACKGROUND HANDLING - Use absolute file:// URLs for html2pptx compatibility
// ============================================================================

/**
 * Get absolute file:// URL for background image
 * This is required for html2pptx to work correctly
 */
function getBackgroundUrl(assetsDir) {
  const backgroundPath = path.join(assetsDir, 'background.png');
  
  // Check if background exists
  if (!fs.existsSync(backgroundPath)) {
    console.warn(`Warning: Background image not found at ${backgroundPath}`);
    return '';
  }
  
  // Convert to absolute path and use file:// URL
  const absPath = path.resolve(backgroundPath);
  return `file://${absPath}`;
}

/**
 * Get relative path for background (fallback, not recommended)
 * @deprecated Use getBackgroundUrl() instead for html2pptx compatibility
 */
function getBackgroundRelPath(htmlDir, assetsDir) {
  return path.relative(htmlDir, path.join(assetsDir, 'background.png'));
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// repo structure:
// template2slide/scripts/renderers/*  -> __dirname = .../template2slide/scripts/renderers
// template2slide/ref                 -> .../template2slide/ref
function getRefDir() {
  return path.join(path.dirname(__dirname), '..', 'ref');
}

function cleanTimelineEvent(event) {
  if (!event) return '';
  return String(event).replace(/^\s*\|+\s*/, '').replace(/\s*\|+\s*$/, '').trim();
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = {
  // Format constants
  SLIDE_FORMAT,
  
  // Background handling
  getBackgroundUrl,        // NEW: Use this for absolute file:// URLs
  getBackgroundRelPath,    // DEPRECATED: Use getBackgroundUrl instead
  
  // Utilities
  cleanTimelineEvent,
  escapeHtml,
  getRefDir,
};



