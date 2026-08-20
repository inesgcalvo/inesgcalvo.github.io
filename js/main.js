/* ============================================================
   main.js — Molecule branches + modal panels
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const molecule = document.getElementById('molecule');
  const hubs = document.querySelectorAll('.node[data-hub]');
  const branches = document.querySelectorAll('.branch');
  const triggers = document.querySelectorAll('[data-panel]');
  const closeBtns = document.querySelectorAll('.close-panel');
  const panels = document.querySelectorAll('.info-panel');

  // --- Branches (sub-nodes bonded to a vertex) ---
  const closeBranches = () => {
    branches.forEach(b => b.classList.remove('open'));
    hubs.forEach(h => {
      h.classList.remove('active');
      h.setAttribute('aria-expanded', 'false');
    });
    if (molecule) molecule.classList.remove('has-open');
  };

  hubs.forEach(hub => {
    const branch = document.getElementById('branch-' + hub.dataset.hub);
    if (!branch) return;

    hub.setAttribute('aria-controls', branch.id);

    hub.addEventListener('click', (e) => {
      e.stopPropagation();
      const wasOpen = branch.classList.contains('open');
      closeBranches();
      if (!wasOpen) {
        branch.classList.add('open');
        hub.classList.add('active');
        hub.setAttribute('aria-expanded', 'true');
        if (molecule) molecule.classList.add('has-open');
      }
    });
  });

  // Clicking anywhere outside a node/branch folds the open branch
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.vertex')) closeBranches();
  });

  // --- Panels ---
  const closePanels = () => panels.forEach(p => p.classList.remove('active'));

  triggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      const panel = document.getElementById(trigger.dataset.panel);
      if (!panel) return;
      e.stopPropagation();
      closePanels();
      closeBranches();
      panel.classList.add('active');
    });
  });

  closeBtns.forEach(btn => btn.addEventListener('click', closePanels));

  // Close on background click
  panels.forEach(panel => {
    panel.addEventListener('click', (e) => {
      if (e.target === panel) closePanels();
    });
  });

  // Close everything on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closePanels();
      closeBranches();
    }
  });
});
