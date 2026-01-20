const { escapeHtml, getBackgroundUrl, SLIDE_FORMAT } = require('./shared');

function generateTitleSlideHTML(slide, htmlDir, assetsDir, constants) {
  // Use absolute file:// URL for background (required for html2pptx)
  const bgUrl = getBackgroundUrl(assetsDir);
  const date = slide.date || '';

  // Use format constants for consistency
  const { SLIDE_WIDTH, SLIDE_HEIGHT, ACCENT_COLOR, TEXT_COLOR } = constants;
  const { width, height, accentColor, textColor, fonts } = SLIDE_FORMAT;

  return `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #000000; }
body {
  width: ${SLIDE_WIDTH}pt;
  height: ${SLIDE_HEIGHT}pt;
  margin: 0;
  padding: 0;
  background-image: url('${bgUrl}');
  background-size: cover;
  background-position: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: Arial, Helvetica, sans-serif;
}
.title-container {
  text-align: center;
}
h1 {
  color: ${ACCENT_COLOR};
  font-size: 28pt;
  font-weight: bold;
  text-transform: uppercase;
  margin: 0 40pt 20pt 40pt;
  padding: 0;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: ${SLIDE_WIDTH - 80}pt;
  text-align: center;
}
.date {
  color: ${TEXT_COLOR};
  font-size: 18pt;
  margin: 0;
  padding: 0;
}
</style>
</head>
<body>
<div class="title-container">
  <h1>${escapeHtml(slide.title || '')}</h1>
  ${date ? `<p class="date">${escapeHtml(date)}</p>` : ''}
</div>
</body>
</html>`;
}

module.exports = { generateTitleSlideHTML };



