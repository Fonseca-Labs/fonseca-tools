(() => {
  'use strict';

  const guard = document.getElementById('golscopeFrameGuard');
  if (window.self === window.top) {
    guard?.remove();
    document.documentElement.dataset.frameGuard = 'top-level';
    return;
  }

  // Static GitHub Pages cannot emit frame-ancestors/X-Frame-Options headers.
  // Keep all UI invisible and inert when embedded by another browsing context.
  document.documentElement.dataset.frameGuard = 'blocked';
  document.addEventListener('DOMContentLoaded', () => {
    document.body?.setAttribute('aria-hidden', 'true');
    if (document.body) {
      document.body.style.pointerEvents = 'none';
      document.body.inert = true;
    }
  }, { once: true });
})();
