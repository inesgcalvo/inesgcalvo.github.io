/* ============================================================
   mail.js — Reveals the contact address only on demand.

   The address never appears in the HTML source: it is stored as two
   base64 chunks and the "@" is added at runtime, so scrapers looking
   for a name@domain pattern in the markup find nothing.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('mail-btn');
  if (!btn) return;

  const note = document.getElementById('mail-note');
  const copyBtn = document.getElementById('mail-copy');

  const address = () =>
    atob(btn.dataset.u) + String.fromCharCode(64) + atob(btn.dataset.d);

  const reveal = () => {
    const mail = address();
    if (note) {
      note.textContent = mail;
      note.hidden = false;
    }
    if (copyBtn) copyBtn.hidden = false;
    return mail;
  };

  btn.addEventListener('click', () => {
    const mail = reveal();
    window.location.href =
      'mailto:' + mail + '?subject=' + encodeURIComponent('Hello from your website');
  });

  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(address());
        copyBtn.textContent = 'Copied ✓';
      } catch {
        copyBtn.textContent = 'Select the address above';
      }
    });
  }
});
