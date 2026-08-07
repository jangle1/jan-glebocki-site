const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Sticky-pill nav offset for in-page links
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    const id = a.getAttribute("href");
    if (!id || id.length < 2) return;
    const target = document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    const navH = document.querySelector(".nav")?.getBoundingClientRect().height ?? 0;
    window.scrollTo({
      top: target.getBoundingClientRect().top + window.scrollY - navH - 28,
      behavior: "smooth",
    });
  });
});

// ---------------------------------------------------------------------------
// Photos rest in a warm sepia wash and resolve to full colour as they reach
// the middle of the viewport. Driven by two CSS custom properties so the
// browser handles the actual filtering.
// ---------------------------------------------------------------------------
const warmImages = [...document.querySelectorAll("img[data-warm]")];

if (warmImages.length && !reducedMotion) {
  let queued = false;

  const paint = () => {
    queued = false;
    const vh = window.innerHeight;
    warmImages.forEach((img) => {
      const rect = img.getBoundingClientRect();
      if (rect.bottom < -100 || rect.top > vh + 100) return;
      // 0 at the viewport edges, 1 when the image sits at the centre
      const centre = rect.top + rect.height / 2;
      const distance = Math.abs(centre - vh / 2) / (vh / 2);
      const t = Math.min(1, Math.max(0, 1 - distance));
      const eased = t * t * (3 - 2 * t);
      img.style.setProperty("--sat", (0.15 + 0.85 * eased).toFixed(3));
      img.style.setProperty("--sep", (0.4 - 0.4 * eased).toFixed(3));
      img.style.setProperty("--zoom", (1.04 - 0.04 * eased).toFixed(3));
    });
  };

  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(paint);
  };

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  warmImages.forEach((img) => img.addEventListener("load", schedule));
  schedule();
}
