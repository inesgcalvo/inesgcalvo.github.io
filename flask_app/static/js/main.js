// Year
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Sticky nav
const nav = document.getElementById('app-nav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  }, { passive: true });
}

// Scroll reveal
const ro = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); ro.unobserve(e.target); }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => ro.observe(el));
document.querySelectorAll('.proj-card, .highlight-card, .cv-section, .cv-entry, .cv-pub').forEach(el => {
  el.classList.add('reveal');
  ro.observe(el);
});
