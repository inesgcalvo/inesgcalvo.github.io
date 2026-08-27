/* ============================================================
   gallery.js — Photo grid lightbox

   Progressive enhancement: the grid in the page is plain HTML and
   already works on its own. This adds the full-size viewer on top,
   reading the display copy's URL and dimensions from the data
   attributes the build script wrote onto each thumbnail's button.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const gallery  = document.getElementById('gallery');
  const lightbox = document.getElementById('lightbox');
  if (!gallery || !lightbox) return;

  const shots = Array.from(gallery.querySelectorAll('.shot-open'));
  if (!shots.length) return;

  const img     = lightbox.querySelector('.lightbox-img');
  const caption = lightbox.querySelector('.lightbox-caption');
  const closeBtn = lightbox.querySelector('.lightbox-close');
  const prevBtn = lightbox.querySelector('.lightbox-prev');
  const nextBtn = lightbox.querySelector('.lightbox-next');

  let index = -1;
  let lastFocused = null;

  const show = (i) => {
    // Wrap around, so the arrows never dead-end.
    index = (i + shots.length) % shots.length;
    const btn = shots[index];
    const thumb = btn.querySelector('img');

    // Reserve the right box before the full image arrives: without this
    // the viewer jumps from the previous photo's shape to this one's.
    // aspect-ratio rather than width/height, because the stylesheet sizes
    // this image from the viewport and would override both attributes.
    img.style.aspectRatio = `${btn.dataset.fullW} / ${btn.dataset.fullH}`;
    img.src = btn.dataset.full;
    img.alt = thumb ? thumb.alt : '';
    caption.textContent = btn.dataset.caption || '';
  };

  const open = (i) => {
    lastFocused = document.activeElement;
    show(i);
    lightbox.hidden = false;
    // The page behind must not scroll while the viewer is over it.
    document.body.classList.add('lightbox-open');
    closeBtn.focus();
  };

  const close = () => {
    lightbox.hidden = true;
    document.body.classList.remove('lightbox-open');
    img.src = '';
    if (lastFocused) lastFocused.focus();
  };

  shots.forEach((btn, i) => btn.addEventListener('click', () => open(i)));

  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', () => show(index - 1));
  nextBtn.addEventListener('click', () => show(index + 1));

  // Clicking the backdrop — but not the photo or a control — closes.
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox || e.target.classList.contains('lightbox-figure')) close();
  });

  document.addEventListener('keydown', (e) => {
    if (lightbox.hidden) return;
    if (e.key === 'Escape')     { close(); }
    if (e.key === 'ArrowLeft')  { show(index - 1); }
    if (e.key === 'ArrowRight') { show(index + 1); }
    // Keep Tab inside the viewer while it is open.
    if (e.key === 'Tab') {
      const stops = [closeBtn, prevBtn, nextBtn];
      const at = stops.indexOf(document.activeElement);
      e.preventDefault();
      stops[(at + (e.shiftKey ? -1 : 1) + stops.length) % stops.length].focus();
    }
  });

  // Swipe between photographs on a touch screen.
  let startX = null;
  lightbox.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
  lightbox.addEventListener('touchend', (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
    startX = null;
  }, { passive: true });
});
