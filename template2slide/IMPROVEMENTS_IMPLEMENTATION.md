# Implementation Guide: Improvements for Stable Slide Generation

## Overview

This document provides step-by-step instructions to improve template2slide for:
1. ✅ Consistent background handling (absolute `file://` URLs)
2. ✅ Proper format in each slide (shared constants)
3. ✅ Support for many different templates (robust parsing)

## Status

### ✅ Completed
- [x] Created `SLIDE_FORMAT` constants in `shared.js`
- [x] Added `getBackgroundUrl()` function for absolute `file://` URLs
- [x] Created comparison and recommendation document

### ⚠️ In Progress
- [ ] Update all renderers to use `getBackgroundUrl()` instead of `getBackgroundRelPath()`
- [ ] Update `generate_from_json.js` to pass background URL to renderers
- [ ] Add format validation to Subagent 2

### 📋 TODO
- [ ] Test with multiple templates
- [ ] Update documentation

---

## Step 1: Update Renderers to Use Absolute Background URLs

### Current Issue
All renderers use `getBackgroundRelPath()` which creates relative paths. This doesn't work reliably with html2pptx.

### Solution
Update all renderers to use `getBackgroundUrl()` which creates absolute `file://` URLs.

### Files to Update
1. `renderers/title.js`
2. `renderers/content_bullets.js`
3. `renderers/two_column.js`
4. `renderers/diagram.js`
5. `renderers/timeline.js`
6. `renderers/module_description.js`
7. `renderers/content_table.js`

### Example Change

**Before:**
```javascript
const { escapeHtml, getBackgroundRelPath } = require('./shared');

function generateTitleSlideHTML(slide, htmlDir, assetsDir, constants) {
  const bgPath = getBackgroundRelPath(htmlDir, assetsDir);
  // ...
  background-image: url('${bgPath}');
}
```

**After:**
```javascript
const { escapeHtml, getBackgroundUrl, SLIDE_FORMAT } = require('./shared');

function generateTitleSlideHTML(slide, htmlDir, assetsDir, constants) {
  const bgUrl = getBackgroundUrl(assetsDir);
  // ...
  background-image: url('${bgUrl}');
}
```

---

## Step 2: Update generate_from_json.js

### Changes Needed

1. **Update RENDER_CONSTANTS** to include background URL:
```javascript
const { getBackgroundUrl } = require('./renderers/shared');

// After assetsDir is created:
const BACKGROUND_URL = getBackgroundUrl(assetsDir);
const RENDER_CONSTANTS = { 
  SLIDE_WIDTH, 
  SLIDE_HEIGHT, 
  ACCENT_COLOR, 
  TEXT_COLOR,
  BACKGROUND_URL  // Add this
};
```

2. **Verify background exists** before generation:
```javascript
const BACKGROUND_IMAGE = path.resolve(__dirname, 'background.png');
if (!fs.existsSync(BACKGROUND_IMAGE)) {
  throw new Error(`Background image not found: ${BACKGROUND_IMAGE}`);
}
```

---

## Step 3: Use SLIDE_FORMAT Constants in Renderers

### Example: Update title.js

**Before:**
```javascript
const { SLIDE_WIDTH, SLIDE_HEIGHT, ACCENT_COLOR, TEXT_COLOR } = constants;

h1 {
  color: ${ACCENT_COLOR};
  font-size: 28pt;
  // ...
}
```

**After:**
```javascript
const { SLIDE_FORMAT, getBackgroundUrl } = require('./shared');

const bgUrl = getBackgroundUrl(assetsDir);
const { width, height, accentColor, textColor, fonts } = SLIDE_FORMAT;

h1 {
  color: ${accentColor};
  font-size: ${fonts.title};
  // ...
}
```

---

## Step 4: Add Format Validation to Subagent 2

### Add to `subagent2_validate.py`:

```python
def _validate_format_consistency(self, result: ValidationResult):
    """Validate format consistency across slides"""
    slides = self.slide_structure.get('slides', [])
    
    # Check if background is used consistently
    # (This would require parsing HTML or checking JSON structure)
    
    # Check font sizes are consistent
    # Check colors are consistent
    # Check spacing is consistent
```

---

## Testing Checklist

After implementing changes, test with:

1. ✅ **Leda_Inio_template.md** (already tested)
2. ⚠️ **Bromma_Malaysia_template.md**
3. ⚠️ **Other templates with different formats**

### What to Check:
- [ ] Background shows correctly in all slides
- [ ] Font sizes are consistent
- [ ] Colors are consistent (viAct Blue #00AEEF)
- [ ] Spacing is consistent
- [ ] No overflow issues
- [ ] Professional appearance

---

## Migration Notes

### For Existing Templates
- No changes needed to templates
- Background will automatically use absolute URLs
- Format will be more consistent

### For New Templates
- Use standard template format
- Background will be applied automatically
- Format will be consistent

---

## Quick Reference

### Background URL Format
```javascript
// ✅ CORRECT (absolute file:// URL)
const bgUrl = `file:///absolute/path/to/background.png`;

// ❌ WRONG (relative path)
const bgUrl = `../assets/background.png`;

// ❌ WRONG (base64)
const bgUrl = `data:image/png;base64,...`;
```

### Format Constants
```javascript
const SLIDE_FORMAT = {
  width: 720,
  height: 405,
  accentColor: '#00AEEF',
  textColor: '#FFFFFF',
  fonts: {
    title: '28pt Arial, Helvetica, sans-serif',
    body: '16pt Arial, Helvetica, sans-serif'
  }
};
```

---

## Next Steps

1. **Update all renderers** (Priority 1)
2. **Update generate_from_json.js** (Priority 1)
3. **Add format validation** (Priority 2)
4. **Test with multiple templates** (Priority 2)
5. **Update documentation** (Priority 3)



