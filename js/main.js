/* ============================================================
   main.js — Interactive Modal Logic
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  const openAboutBtn = document.getElementById('open-about');
  const openProjectsBtn = document.getElementById('open-projects');
  const panelAbout = document.getElementById('panel-about');
  const panelProjects = document.getElementById('panel-projects');
  const closeBtns = document.querySelectorAll('.close-panel');
  const panels = document.querySelectorAll('.info-panel');

  // --- Open Panels ---
  openAboutBtn.addEventListener('click', () => {
    panelAbout.classList.add('active');
  });

  openProjectsBtn.addEventListener('click', () => {
    panelProjects.classList.add('active');
  });

  // --- Close Panels ---
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      panels.forEach(p => p.classList.remove('active'));
    });
  });

  // Close on background click
  panels.forEach(panel => {
    panel.addEventListener('click', (e) => {
      if (e.target === panel) {
        panel.classList.remove('active');
      }
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      panels.forEach(p => p.classList.remove('active'));
    }
  });
});
