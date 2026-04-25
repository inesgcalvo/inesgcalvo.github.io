/* ============================================================
   main.js — Portal animations & neuron particle canvas
   ============================================================ */

// --- Year ---
document.getElementById('year').textContent = new Date().getFullYear();

// --- Sticky nav on scroll ---
const nav = document.getElementById('portal-nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

// --- Scroll reveal ---
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll(
  '.section-header, .about-text, .about-stats, .stat-card, .project-card, .cta-ornament, .cta-title, .cta-text, .cta-buttons'
).forEach(el => {
  el.classList.add('reveal');
  revealObserver.observe(el);
});

// --- Staggered stat cards ---
document.querySelectorAll('.stat-card').forEach((card, i) => {
  card.style.transitionDelay = `${i * 0.1}s`;
});

// --- Staggered project cards ---
document.querySelectorAll('.project-card').forEach((card, i) => {
  card.style.transitionDelay = `${i * 0.08}s`;
});

// ============================================================
//   NEURON PARTICLE CANVAS
// ============================================================
(function () {
  const canvas = document.getElementById('neuron-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let W, H, nodes, animFrameId;

  const CONFIG = {
    count:         70,
    maxRadius:     2.8,
    minRadius:     0.8,
    speed:         0.28,
    linkDist:      160,
    linkOpacity:   0.18,
    nodeOpacity:   0.55,
    color:         '120, 72, 54',   // warm sepia RGB
    pulseSpeed:    0.015,
  };

  class Node {
    constructor() { this.reset(true); }

    reset(init = false) {
      this.x   = Math.random() * W;
      this.y   = init ? Math.random() * H : -10;
      this.vx  = (Math.random() - 0.5) * CONFIG.speed;
      this.vy  = (Math.random() - 0.5) * CONFIG.speed;
      this.r   = CONFIG.minRadius + Math.random() * (CONFIG.maxRadius - CONFIG.minRadius);
      this.phase = Math.random() * Math.PI * 2;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.phase += CONFIG.pulseSpeed;

      // Bounce off edges
      if (this.x < 0 || this.x > W) this.vx *= -1;
      if (this.y < 0 || this.y > H) this.vy *= -1;
    }

    draw() {
      const pulse = 0.7 + 0.3 * Math.sin(this.phase);
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r * pulse, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${CONFIG.color}, ${CONFIG.nodeOpacity * pulse})`;
      ctx.fill();
    }
  }

  function init() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
    nodes = Array.from({ length: CONFIG.count }, () => new Node());
  }

  function drawLinks() {
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx   = nodes[i].x - nodes[j].x;
        const dy   = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CONFIG.linkDist) {
          const alpha = (1 - dist / CONFIG.linkDist) * CONFIG.linkOpacity;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = `rgba(${CONFIG.color}, ${alpha})`;
          ctx.lineWidth   = 0.7;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    nodes.forEach(n => { n.update(); n.draw(); });
    drawLinks();
    animFrameId = requestAnimationFrame(animate);
  }

  // Resize handler (debounced)
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(init, 200);
  });

  init();
  animate();
})();

// --- Smooth anchor scroll for nav links ---
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
