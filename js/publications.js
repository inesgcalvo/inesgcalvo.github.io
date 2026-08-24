/* ============================================================
   publications.js — Citation style switcher (APA / MLA / Harvard)

   Every entry carries the three citations in the markup; CSS shows
   only the one matching the list's data-style. This script just moves
   that attribute, so the page still renders APA without JavaScript.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const list = document.getElementById('pub-list');
  const buttons = document.querySelectorAll('.cite-btn');
  if (!list || !buttons.length) return;

  const STORE_KEY = 'citation-style';

  const apply = (style) => {
    list.dataset.style = style;
    buttons.forEach(btn => {
      const on = btn.dataset.style === style;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-pressed', String(on));
    });
    try {
      localStorage.setItem(STORE_KEY, style);
    } catch {
      /* private browsing — the choice just won't survive a reload */
    }
  };

  buttons.forEach(btn => {
    btn.addEventListener('click', () => apply(btn.dataset.style));
  });

  let saved = null;
  try {
    saved = localStorage.getItem(STORE_KEY);
  } catch {
    /* ignore */
  }
  if (saved && [...buttons].some(b => b.dataset.style === saved)) apply(saved);
});
