const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const navHeight = () =>
  document.querySelector(".nav")?.getBoundingClientRect().height ?? 0;

const scrollToEl = (el, extra = 8) => {
  const top = el.getBoundingClientRect().top + window.scrollY - navHeight() - extra;
  window.scrollTo({ top, behavior: reducedMotion ? "auto" : "smooth" });
};

// ---------------------------------------------------------------------------
// Sections open in a pop-up rather than further down the page, so picking a
// second card never means scrolling back up to the carousel.
// ---------------------------------------------------------------------------
const modal = document.getElementById("modal");
const modalTitle = document.getElementById("modal-title");
const modalScroll = document.getElementById("modal-scroll");
const modalCloseBtn = modal?.querySelector(".modal-close");
const panels = [...document.querySelectorAll(".panel")];
const galleryCards = [...document.querySelectorAll(".gal-card")];
let lastFocused = null;

// file:// pages reject history writes, so keep the hash update best-effort
const setHash = (id) => {
  try {
    history.replaceState(null, "", id ? `#${id}` : location.pathname);
  } catch {
    /* deep links still work, the URL just does not follow along */
  }
};

const labelFor = (id) => {
  const card = galleryCards.find((c) => c.getAttribute("href") === `#${id}`);
  return card?.querySelector(".gal-label")?.firstChild?.textContent?.trim() || "";
};

const closeModal = ({ restoreFocus = true } = {}) => {
  if (!modal || modal.hidden) return;
  modal.hidden = true;
  document.body.classList.remove("modal-open");
  panels.forEach((p) => { p.hidden = true; });
  galleryCards.forEach((card) => {
    card.classList.remove("is-open");
    card.removeAttribute("aria-current");
  });
  setHash(null);
  if (restoreFocus && lastFocused) lastFocused.focus();
};

const openPanel = (id, { focus = true } = {}) => {
  const panel = document.getElementById(id);
  if (!modal || !panel || !panel.classList.contains("panel")) return false;

  lastFocused = document.activeElement;
  panels.forEach((p) => { p.hidden = p !== panel; });
  galleryCards.forEach((card) => {
    const active = card.getAttribute("href") === `#${id}`;
    card.classList.toggle("is-open", active);
    if (active) card.setAttribute("aria-current", "true");
    else card.removeAttribute("aria-current");
  });

  if (modalTitle) modalTitle.textContent = labelFor(id);
  const wasOpen = !modal.hidden;
  modal.hidden = false;
  document.body.classList.add("modal-open");
  if (modalScroll) modalScroll.scrollTop = 0;

  // replay the pop when switching straight from one section to another
  if (wasOpen) {
    const win = modal.querySelector(".modal-window");
    win.style.animation = "none";
    void win.offsetWidth;
    win.style.animation = "";
  }

  setHash(id);
  if (focus) modalCloseBtn?.focus();
  return true;
};

modal?.addEventListener("click", (e) => {
  if (e.target.closest("[data-modal-close]")) closeModal();
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal && !modal.hidden) closeModal();
});

// Any in-page link pointing at a section opens the pop-up.
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener("click", (e) => {
    const href = a.getAttribute("href");
    if (!href || href === "#" || href.length < 2) return;
    const id = href.slice(1);
    const target = document.getElementById(id);
    if (!target) return;
    // a card that is not at the front of the ring turns to face you first,
    // the carousel's own handler deals with that click
    if (a.classList.contains("gal-card") && !a.classList.contains("is-front")) return;
    e.preventDefault();
    if (target.classList.contains("panel")) openPanel(id);
    else scrollToEl(target, -1);
  });
});

// deep links keep working: /#stack opens the toolkit section on load
if (location.hash.length > 1) openPanel(location.hash.slice(1), { focus: false });

// ---------------------------------------------------------------------------
// "Pick a card", a coverflow deck. The front card and its two neighbours stay
// flat and readable; anything further back bends away into the depth. The
// deck never rewinds, cards wrap around. Dragging, the arrows and keyboard
// focus all steer it; interaction pauses the autoplay.
// ---------------------------------------------------------------------------
const stage = document.querySelector(".gal-stage");
const ring = document.querySelector(".gal-ring");

if (stage && ring) {
  const cards = [...ring.querySelectorAll(".gal-card")];
  const count = cards.length;
  const DRAG_THRESHOLD = 6;   // px before a press counts as a drag, not a click
  const PX_PER_STEP = 190;    // drag distance that advances one card
  const AUTOPLAY_MS = 4200;

  // `pos` is a continuous card index. It is unbounded, so the deck never
  // rewinds; cards wrap around it.
  let pos = 0;
  let target = 0;
  let metrics = { x1: 220, x2: 340 };
  let dragging = false;
  let dragged = false;
  let pointerId = null;
  let startX = 0;
  let startPos = 0;
  let autoplayTimer = null;
  let paused = false;

  // Depth profile by distance from the front. The first three cards stay flat
  // and fully readable; only the ones behind them bend away.
  const KNOTS = [
    { d: 0, x: 0.0, z: 0, ry: 0, op: 1, sc: 1 },
    { d: 1, x: 1.0, z: -70, ry: 4, op: 1, sc: 0.94 },
    { d: 2, x: 1.42, z: -290, ry: 54, op: 0.5, sc: 0.88 },
    { d: 3, x: 1.6, z: -430, ry: 66, op: 0, sc: 0.84 },
  ];

  const lerp = (a, b, t) => a + (b - a) * t;

  const sample = (dist) => {
    const clamped = Math.min(dist, 3);
    const i = Math.min(Math.floor(clamped), 2);
    const t = clamped - i;
    const a = KNOTS[i];
    const b = KNOTS[i + 1];
    return {
      x: lerp(a.x, b.x, t),
      z: lerp(a.z, b.z, t),
      ry: lerp(a.ry, b.ry, t),
      op: lerp(a.op, b.op, t),
      sc: lerp(a.sc, b.sc, t),
    };
  };

  const measure = () => {
    const w = cards[0].getBoundingClientRect().width || 220;
    const half = stage.clientWidth / 2;
    // neighbours sit as far out as the stage allows, but never further than
    // one card width, so three cards always read as a row
    metrics.x1 = Math.max(w * 0.52, Math.min(w * 1.06, half - w * 0.42));
    metrics.x2 = metrics.x1 * 1.42;
    render();
  };

  const render = () => {
    const front = ((Math.round(pos) % count) + count) % count;
    cards.forEach((card, i) => {
      // shortest signed distance from the front slot, wrapping both ways
      let rel = i - pos;
      rel -= Math.round(rel / count) * count;
      const dist = Math.abs(rel);
      const dir = rel < 0 ? -1 : 1;
      const s = sample(dist);
      const px = s.x <= 1 ? s.x * metrics.x1 : metrics.x1 + (s.x - 1) * (metrics.x2 - metrics.x1);

      card.style.transform =
        `translateX(${(dir * px).toFixed(1)}px) translateZ(${s.z.toFixed(0)}px) ` +
        `rotateY(${(-dir * s.ry).toFixed(1)}deg) scale(${s.sc.toFixed(3)})`;
      card.style.opacity = s.op.toFixed(2);
      card.style.zIndex = String(100 - Math.round(dist * 10));
      card.style.pointerEvents = s.op < 0.2 ? "none" : "auto";

      const isFront = i === front;
      card.classList.toggle("is-front", isFront);
      card.tabIndex = isFront ? 0 : -1;
      card.setAttribute("aria-hidden", isFront ? "false" : "true");
    });
  };

  const glide = (animated = true) => {
    ring.classList.toggle("is-animating", animated && !reducedMotion);
    pos = target;
    render();
  };

  const goTo = (next) => { target = next; glide(true); };

  const goToCard = (cardIndex) => {
    const current = ((Math.round(target) % count) + count) % count;
    let delta = cardIndex - current;
    if (delta > count / 2) delta -= count;
    if (delta < -count / 2) delta += count;
    goTo(Math.round(target) + delta);
  };

  // --- autoplay ---
  const stopAutoplay = () => { clearInterval(autoplayTimer); autoplayTimer = null; };
  const startAutoplay = () => {
    if (autoplayTimer || paused || reducedMotion) return;
    autoplayTimer = setInterval(() => goTo(target + 1), AUTOPLAY_MS);
  };
  const pause = () => { paused = true; stopAutoplay(); };
  const resume = () => { paused = false; startAutoplay(); };

  stage.addEventListener("pointerenter", pause);
  stage.addEventListener("pointerleave", resume);
  stage.addEventListener("focusin", pause);
  stage.addEventListener("focusout", resume);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopAutoplay();
    else startAutoplay();
  });

  // --- drag to spin ---
  // cards are links, so the browser would otherwise start a native link drag
  // and swallow the pointer stream
  stage.addEventListener("dragstart", (e) => e.preventDefault());

  stage.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "mouse" && e.button !== 0) return;
    pointerId = e.pointerId;
    startX = e.clientX;
    startPos = pos;
    dragging = true;
    dragged = false;
    pause();
    ring.classList.remove("is-animating");
  });

  stage.addEventListener("pointermove", (e) => {
    if (!dragging || e.pointerId !== pointerId) return;
    const dx = e.clientX - startX;
    if (!dragged) {
      if (Math.abs(dx) < DRAG_THRESHOLD) return;
      dragged = true;
      stage.classList.add("is-dragging");
      // only now: capturing earlier would retarget the click away from the card
      try { stage.setPointerCapture(pointerId); } catch { /* not capturable */ }
    }
    pos = startPos - dx / PX_PER_STEP;
    render();
  });

  const endDrag = (e) => {
    if (!dragging || (e && e.pointerId !== pointerId)) return;
    dragging = false;
    if (dragged) {
      try { stage.releasePointerCapture(pointerId); } catch { /* already gone */ }
    }
    pointerId = null;
    stage.classList.remove("is-dragging");
    if (dragged) {
      goTo(Math.round(pos));
      requestAnimationFrame(() => { dragged = false; });
    }
    resume();
  };
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointercancel", endDrag);

  // a drag must never trigger the card's link
  stage.addEventListener("click", (e) => {
    if (!dragged) return;
    e.preventDefault();
    e.stopPropagation();
  }, true);

  // clicking a card that is not at the front brings it round instead
  cards.forEach((card, i) => {
    card.addEventListener("click", (e) => {
      if (!card.classList.contains("is-front")) {
        e.preventDefault();
        goToCard(i);
      }
    });
    card.addEventListener("focus", () => goToCard(i));
  });

  document.querySelectorAll(".gal-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      goTo(target + (Number(btn.dataset.dir) || 1));
      if (!paused) { stopAutoplay(); startAutoplay(); }
    });
  });

  window.addEventListener("resize", measure);
  measure();
  glide(false);
  startAutoplay();
}
