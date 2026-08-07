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
// "Pick a card", a 3D ring carousel. Cards sit on a circle; the ring keeps
// turning in one direction so it always completes full revolutions. Dragging,
// the arrows and keyboard focus all steer it; interaction pauses the autoplay.
// ---------------------------------------------------------------------------
const stage = document.querySelector(".gal-stage");
const ring = document.querySelector(".gal-ring");

if (stage && ring) {
  const cards = [...ring.querySelectorAll(".gal-card")];
  const count = cards.length;
  const STEP = 360 / count;
  const DRAG_THRESHOLD = 6; // px before a press counts as a drag, not a click
  const DEG_PER_PX = 0.28;
  const AUTOPLAY_MS = 4200;

  // `index` is unbounded, it keeps counting up so the ring never rewinds
  let index = 0;
  let angle = 0;
  let radius = 320;
  let dragging = false;
  let dragged = false;
  let pointerId = null;
  let startX = 0;
  let startAngle = 0;
  let autoplayTimer = null;
  let paused = false;

  const measure = () => {
    const w = cards[0].getBoundingClientRect().width || 220;
    // radius that spaces n cards of width w evenly around the circle
    const ideal = (w / 2 + 26) / Math.tan(Math.PI / count);
    // on a narrow screen that radius throws the neighbouring cards off the
    // edge, so cap it at whatever keeps them inside the stage
    const stepRad = (2 * Math.PI) / count;
    const fit =
      (stage.clientWidth / 2 - (w / 2) * Math.abs(Math.cos(stepRad))) /
      Math.sin(stepRad);
    radius = Math.round(Math.max(140, Math.min(ideal, fit)));
    cards.forEach((card, i) => {
      card.style.transform = `rotateY(${i * STEP}deg) translateZ(${radius}px)`;
    });
    render();
  };

  const render = () => {
    // slight downward tilt so the ring reads as a solid object, not a fan
    ring.style.transform = `translateZ(${-radius}px) rotateX(-4deg) rotateY(${angle}deg)`;
    const frontIndex = ((Math.round(-angle / STEP) % count) + count) % count;
    cards.forEach((card, i) => {
      // how square-on this card is to the viewer: 1 = front, -1 = behind
      const facing = Math.cos(((i * STEP + angle) * Math.PI) / 180);
      card.style.setProperty("--dim", (0.72 - 0.72 * Math.max(0, facing)).toFixed(3));
      card.style.zIndex = String(Math.round(100 + facing * 100));
      const isFront = i === frontIndex;
      card.classList.toggle("is-front", isFront);
      // only the front card is a reachable link
      card.tabIndex = isFront ? 0 : -1;
      card.setAttribute("aria-hidden", isFront ? "false" : "true");
    });
  };

  const glide = (animated = true) => {
    ring.classList.toggle("is-animating", animated);
    angle = -index * STEP;
    render();
  };

  const goTo = (next) => {
    index = next;
    glide(true);
  };

  // rotate to whichever card is nearest the given list position
  const goToCard = (cardIndex) => {
    const current = ((index % count) + count) % count;
    let delta = cardIndex - current;
    if (delta > count / 2) delta -= count;
    if (delta < -count / 2) delta += count;
    goTo(index + delta);
  };

  // --- autoplay ---
  const stopAutoplay = () => {
    clearInterval(autoplayTimer);
    autoplayTimer = null;
  };
  const startAutoplay = () => {
    if (autoplayTimer || paused || reducedMotion) return;
    autoplayTimer = setInterval(() => goTo(index + 1), AUTOPLAY_MS);
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
    startAngle = angle;
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
    angle = startAngle + dx * DEG_PER_PX;
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
      // snap to the nearest card, keeping the unbounded index in step
      index = Math.round(-angle / STEP);
      glide(true);
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
      goTo(index + (Number(btn.dataset.dir) || 1));
      // nudge the timer so it doesn't fire straight after a manual move
      if (!paused) { stopAutoplay(); startAutoplay(); }
    });
  });

  window.addEventListener("resize", measure);
  measure();
  glide(false);
  startAutoplay();
}
