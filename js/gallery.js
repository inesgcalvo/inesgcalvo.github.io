/* ============================================================
   gallery.js — Carousel: one photograph large, the rest as a filmstrip

   Progressive enhancement. Every frame is already in the page as static
   HTML; the stylesheet shows one at a time and this drives which. Without
   scripts a <noscript> rule reveals them all as a plain vertical list, so
   the page degrades to something readable rather than to a single photo.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const gallery = document.getElementById('gallery');
  if (!gallery) return;

  const carousel = gallery.querySelector('.carousel');
  const slides   = Array.from(gallery.querySelectorAll('.slide'));
  const thumbs   = Array.from(gallery.querySelectorAll('.thumb'));
  const strip    = gallery.querySelector('.filmstrip');
  const prevBtn  = gallery.querySelector('.stage-prev');
  const nextBtn  = gallery.querySelector('.stage-next');
  if (!carousel || slides.length < 2) return;

  let index = 0;

  /* The neighbours of the current frame are the ones most likely to be
     asked for next. Nudging them into the cache means the arrows feel
     instant instead of showing a blank stage while a JPEG arrives. */
  const preload = (i) => {
    [i - 1, i + 1].forEach((n) => {
      const img = slides[(n + slides.length) % slides.length].querySelector('img');
      if (img && img.loading === 'lazy') img.loading = 'eager';
    });
  };

  const show = (i) => {
    // Wrap around, so the arrows never dead-end.
    index = (i + slides.length) % slides.length;

    slides.forEach((s, n) => s.classList.toggle('is-active', n === index));
    thumbs.forEach((t, n) => {
      const on = n === index;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
    });

    // Keep the current frame visible in the strip without yanking the
    // whole page around it.
    const active = thumbs[index];
    if (active && strip) {
      const stripBox = strip.getBoundingClientRect();
      const thumbBox = active.getBoundingClientRect();
      if (thumbBox.left < stripBox.left || thumbBox.right > stripBox.right) {
        strip.scrollTo({
          left: active.offsetLeft - (strip.clientWidth - active.offsetWidth) / 2,
          behavior: 'smooth',
        });
      }
    }

    preload(index);
  };

  thumbs.forEach((t, i) => t.addEventListener('click', () => show(i)));
  if (prevBtn) prevBtn.addEventListener('click', () => show(index - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => show(index + 1));

  /* Arrow keys steer the carousel, but only once it is what the visitor is
     working with — otherwise they would hijack scrolling the page. */
  gallery.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft')  { e.preventDefault(); show(index - 1); thumbs[index].focus(); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); thumbs[index].focus(); }
    if (e.key === 'Home')       { e.preventDefault(); show(0); thumbs[0].focus(); }
    if (e.key === 'End')        { e.preventDefault(); show(slides.length - 1); thumbs[index].focus(); }
  });

  // Swipe across the stage on a touch screen.
  const stage = gallery.querySelector('.stage');
  let startX = null;
  if (stage) {
    stage.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      startX = null;
    }, { passive: true });
  }

  show(0);
});
