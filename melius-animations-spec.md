# Melius.com — pełna specyfikacja animacji (reverse-engineering)

> Źródło: analiza statyczna produkcyjnych bundli melius.com (Next.js/Turbopack, deploy `dpl_zJ5qvjeE2A8AbnapCTjfonU5AnaD`, sierpień 2026).
> Wszystkie wartości (czasy, easingi, progi) wyciągnięte 1:1 z kodu, nie szacowane.

## 1. Stack animacyjny

| Warstwa | Technologia | Rola |
|---|---|---|
| Smooth scroll | **Lenis** (`ReactLenis root`, `smoothWheel: true`, lerp domyślny `0.1`; wyłączany przy `prefers-reduced-motion`) | Globalny płynny scroll + `scrollTo` do dokowania sekcji |
| Animacje UI | **Framer Motion** (`m.` components, `useMotionValue`, `useTransform`, `useSpring`, `useInView`, `AnimatePresence`) | Wejścia sekcji, morphing prompt-bara, sekwencje węzłów |
| Animacje imperatywne | **GSAP** (+ `SplitText`) | Hero swoosh, WebGL timelines, shimmer, auto-scroll stopki |
| 3D | **Three.js + pmndrs postprocessing** (EffectComposer, custom pass) | Hero „wystrzeliwane karty", slider modeli, dither + barrel distortion |
| CSS | Tailwind v4 + custom `@keyframes` | Noise, pixel-arrow, glow, akordeon |
| Komunikacja | własny event-bus (pub/sub) | `WEBGL_HERO_IMAGES_SHOW`, `WEBGL_HERO_ZOOM_OUT`, `WEBGL_MODELS_SHOW/HIDE`, `LENIS_SCROLL_PAUSE/RESUME`, `MODELS_SLIDER_*`, `CARD_CAROUSEL_DRAG_END` |

### Biblioteka easingów (cubic-bezier, używane w całym serwisie)
```js
const easings = {
  easeInQuad:[.11,0,.5,0],   easeOutQuad:[.5,1,.89,1],   easeInOutQuad:[.45,0,.55,1],
  easeInCubic:[.32,0,.67,0], easeOutCubic:[.33,1,.68,1], easeInOutCubic:[.65,0,.35,1],
  easeInQuart:[.5,0,.75,0],  easeOutQuart:[.25,1,.5,1],  easeInOutQuart:[.76,0,.24,1],
  easeInQuint:[.64,0,.78,0], easeOutQuint:[.22,1,.36,1], easeInOutQuint:[.83,0,.17,1],
  easeInExpo:[.7,0,.84,0],   easeOutExpo:[.16,1,.3,1],   easeInOutExpo:[.87,0,.13,1],
  easeInCirc:[.55,0,1,.45],  easeOutCirc:[0,.55,.45,1],  easeInOutCirc:[.85,0,.15,1],
  easeInSine:[.12,0,.39,0],  easeOutSine:[.61,1,.88,1],  easeInOutSine:[.37,0,.63,1],
  easeInBack:[.36,0,.66,-.56], easeOutBack:[.34,1.56,.64,1], easeInOutBack:[.68,-.6,.32,1.6],
}
```
CSS custom properties: `--ease-quart-in-out: cubic-bezier(.76,0,.24,1)`, `--ease-sin-in-out: cubic-bezier(.37,0,.63,1)`, `--ease-in-out: cubic-bezier(.4,0,.2,1)`.

Wszędzie respektowane `prefers-reduced-motion` (duration `*0` albo stan końcowy od razu).

---

## 2. HERO — choreografia intro (`#hero`)

Elementy: dot-grid tło (SVG data-URI 15×15px, kropka 2×2 `rgba(0,0,0,.08)`), gigantyczny SVG „swoosh" Melius (viewBox `0 0 8015 1515`, szer. `200vw` mobile / `120vw` desktop), canvas WebGL (z-30), `h1`, opis + prompt-slot.

Sekwencja (po załadowaniu 24 tekstur hero, fallback `setTimeout 2000ms`):

1. **Swoosh SVG**: GSAP `scale 0 → 0.45`, `duration: 3s`, `delay: 0.3s`, `ease: power3.out`.
2. **Event `WEBGL_HERO_IMAGES_SHOW`** → w scenie WebGL:
   - `distortionCylindricalFactor: 1 → 0.7`, `2s`, `power4.out` (efekt „rozprostowania" ekranu),
   - `cards.startFiring({interval: 750ms, duration: 8s})` — patrz §3,
   - `cards.animateZoomOut()`: scale grupy `1.2 → 0.5`, `1.5s`, `power3.inOut`,
   - reveal kart: `revealFactor 0 → 1`, `1.75s`, `power3.inOut`.
3. Po `1000ms` od startu → `onIntroComplete` → animacje tekstu (Framer Motion):
   - `h1`: `{opacity: 0, scale: 1.2} → {opacity: 1, scale: 1}`, `1.5s`, ease `easeOutExpo [.16,1,.3,1]`, delay `0`,
   - blok opisu + prompt-slot: to samo, delay `0.2s`.

**SSR initial state**: `style="opacity:0;transform:scale(1.2)"` wprost w HTML (brak FOUC).

### Typewriter w prompt-barze (placeholder)
- pisze **22 ms/znak**; po dopisaniu całości pauza **1800 ms**; fade-out **350 ms** (klasa `opacity-0 duration-[350ms]`); **400 ms** przerwy i następny prompt (pętla po tablicy promptów).
- Ręcznie wpisany tekst zatrzymuje pętlę; CTA linkuje do `signup?prompt=<encodeURIComponent>`.

### Shimmer border (hover na prompt-barze / CTA)
Nakładka border-gradient (mask XOR `padding-box/content-box`, `--border-width: 1px`):
`backgroundImage: linear-gradient(120deg, transparent 35%, var(--color-accent) 50%, transparent 65%)`, `backgroundSize: 300% 300%`.
GSAP: `set backgroundPosition 5% 5%` → `to 95% 95%`, `2s`; loop: `ease:"none", repeat:-1`; one-shot: `power1.inOut` + fade `autoAlpha 0` w `0.5s power2.out` @ `t=1.8s`. Na touch (`hover: none`) gra w pętli od razu.

---

## 3. HERO WebGL — „wystrzeliwane karty" (Three.js)

- Kamera: `PerspectiveCamera(fov 45, near .1, far 1000)`, pozycja `(0,0,5)`.
- Post-processing: `EffectComposer` (HalfFloat, MSAA 2× desktop) → RenderPass → **custom pass: dither + EffectBarrel**.
  - `EffectBarrel` uniforms: `uDistortionK1 = -0.15` desktop / `-0.075` mobile, `uDistortionK2 = 0`, `uDistortionCylindricalFactor = 0.7`.
- 24 obrazki (webp 512px desktop / 256px mobile, q75), plane'y `PlaneGeometry(1,1)`, szerokość mesha `0.75 * viewportWidth` desktop / `1.2 * vw` mobile.
- Karty w dwóch pulach: parzyste → **left**, nieparzyste → **right**. Cel lotu: `x = ±1.65 * viewportWidth`.
- **Firing loop**: co `750ms` odpalana jest para (lewa+prawa); lot trwa `8s`; na starcie karty są pre-dystrybuowane z `initialProgress = i * (interval / (1000*duration))` (żeby ekran był od razu zapełniony).
- Matematyka lotu (per frame, `p` = progress 0→1 pomnożony przez `revealFactor`):
  ```js
  s = smoothstep(0,1,p); s = 0.5*easeInQuad(s) + 0.5*s;      // pozycja x = fireTargetX * s
  a = 0.125*smoothstep(0, .15, p) + 0.875*smoothstep(r, 1, p) // skala (r = .2 desktop / .3 mobile)
  renderOrder = s + a
  ```
  Efekt: karta rośnie od 0, przyspiesza i „wylatuje" za krawędź z dystorsją beczkową.

---

## 4. Sekcja CANVAS (`#canvas`) — dokowanie prompt-bara + sekwencje węzłów

Layout: sekcja `bg-black` z dziećmi `canvas-showcase-{advertising,e-commerce,filmmaking,fashion,branding}`; tło i prompt-bar w osobnych warstwach `sticky top-0 h-lvh`.

### Morph / dokowanie
- `T = useSpring(scrollYProgress, { stiffness: 140, damping: 26 })`.
- Frame intro (pozycja z hero) → frame docka; interpolacja liniowa `lerp(intro, dock, clamp01(T))` dla `x, y, width`.
- Stałe docka (design 1440×812): `dockWidth: 353`, `dockIntroWidth: 320`, `dockIntroHeight: 55`, `dockIntroOverlapRatio: 71/812`, `dockLeftRatio: 0.16875`, `dockTopRatio: 195/812`; mobile: `x=12`, `y=max(16, headerSpace)`, szer. pełna −24.
- `borderRadius = 16 − 8 * clamp01(T)` (16→8), wysokość `introHeight → 49 + (liczbaLinii−1)*15` (`0.3s easeOutCubic`), rotacja strzałki `0→360°` sprzężona z T.
- Progi: `T > 0.05` → intro ready; `T > 0.82` → **isDocked** (start sekwencji).
- Crossfade zawartości: stary widok `opacity 1→0` przy `T ∈ [0, .3]`, nowy `0→1` przy `T ∈ [.5, .8]`.

### Nawigacja kategorii (pigułka)
- Kontener: variants `show/hide` ze `staggerChildren .12`/`.06 reverse`; wskaźnik (pomarańczowy bg) `x/width` animowane spring; pojawienie `opacity 0→1, 0.2s, delay 0.5s, easeOutCubic`.
- Klik → `lenis.scrollTo(sekcja, { offset: -viewportHeight * dockTopRatio })`.
- **Auto-powrót**: jeśli user przescrollował w dół i progress jest w `(0.05, 0.82)` przez `5s` bez ruchu → `scrollTo(kategoria[0])`.

### Sekwencja sceny (per kategoria) — stany: `typing → pressing → loading → complete`
1. **typing**: prompt kategorii pisany 22 ms/znak w docku.
2. **pressing**: przycisk „wciska się".
3. **loading**: spinner — dokończenie obrotu do 360° w `(360−kąt)/360 * 0.65s easeInSine`, potem pętla `0.6s linear infinite`; po zakończeniu sceny → domknięcie obrotu `dur = pozostałyKąt/300 easeOutQuad`.
4. Węzły sceny (płótno 780×559 jedn. proj., pełna szer. sceny do 1428):
   - Węzeł: `hidden {opacity: 0, translateY(16px) scale(0.98)}` → `show`, `0.75s easeOutCubic`.
   - Kamera panuje do kolejnego węzła: `translate3d` motion values, `easeInOutQuart`;
     timingi: ta sama grupa węzłów → `{linger .18s, pan .45s, lineStart .3s, lineDraw .3s}`;
     nowa grupa → `{linger .85s→.5s, pan .8s, lineStart .6s, lineDraw .45s}`.
   - **Wire/connection**: SVG path z `pathLength` animowanym `0→1` (`lineDrawDuration`, `easeInOutCubic`), a po narysowaniu „wędrujący glow": `@keyframes wire-glow-travel { 0% {stroke-dashoffset: .24px} 52%,100% {stroke-dashoffset: -1px} }` (dasharray znormalizowany do 1).
   - Po ostatnim węźle `+0.75s` → scena complete.
5. Scena jest draggable (pointer capture): inercja `target = pos + velocity*180`, clamp, `0.45s easeOutCubic`.

### Tło kategorii (sticky)
- Crossfade obrazów/wideo: kontener `staggerChildren .1, delayChildren .35` (hide: `.05 reverse`), warstwa `opacity 0→1, 0.6s easeOutCubic` / hide `0.3s`.
- Obrazy ładowane z blur-placeholder: `transition-[filter,opacity] duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]`, `opacity-60 blur-sm → opacity-100 blur-none`.
- Grupy węzłów: kontener `staggerChildren .1, delayChildren .5`; dziecko `scale .7→1 opacity 0→1 0.6s easeOutCubic` (hide `.3s easeInCubic, stagger .06 reverse`).

Assety: `/media/pages/home/canvas-showcase/<kategoria>/{background.webp|webm, node-*.webp|webm}`.

---

## 5. Sekcja PERSONAS (`#personas`) — talia kart 3D

- Kontener `perspective-[30rem]`, karty absolutnie na stosie, `transform-style: preserve-3d`, `backface-visibility: hidden`.
- Pozycja w talii sterowana `useMotionValue` → `animate(A, index, { duration: 0.7, ease: "circOut" })` (klik = przełożenie karty).
- Flip: variant `flipped: { rotateY: 180 }`.
- Reveal sekcji: `useInView(ref, { once: true, amount: 0.3 })`.
- Hover na karcie: wideo `.webm` (`/images/personas/*.webm`), `group-hover:scale-[1.03]`/`[1.06]`, transition-colors `300ms`.

## 6. Sekcja MODELS (`#models`) — WebGL slider kart

- Scena Three.js jak hero (ta sama kamera + dither/barrel post; `cylindricalFactor` show: `1 → 0.7` desktop / `0.85` mobile, `1.5s expo.out`).
- Karta: `PlaneGeometry(width = 1.1 desktop / 0.9 mobile * cardScale)`, tekstury z canvasa (SRGB, LinearFilter).
- Wejście karty (`animateShow`): `y: −0.85 (desktop) / −0.65 → 0`, `1.25s power4.out`; `scale {x:.75, y:.85} → 1`, `0.75s power3.out`; `uAlpha 0→1`, `0.75s power2.out` — wszystko równolegle (position 0).
- Slider: `cardSpacing 1.3` desktop / `1.1` mobile, `dragSpeed 1`, `wheelSpeed 0.003`, autoplay (`autoPlaySpeed` konfigurowane, pauza przy dragu), emituje `MODELS_SLIDER_PROGRESS`.
- Trigger: `useInView` → event `WEBGL_MODELS_SHOW`; opuszczenie → `WEBGL_MODELS_HIDE` (fade `uAlpha`, `opacity grupy 0 → 1s power2.inOut`).

## 7. PRICING (`#pricing`)
- Wyróżniona karta: `@keyframes pricing-card-glow-breathe` — box-shadow oddycha `0 0 14px orange22% / 24px 12% ↔ 0 0 20px 30% / 26px 15%`, `3.5s`, `var(--ease-sin-in-out)`, infinite.

## 8. FAQ (`#faq`)
- Radix-style akordeon: `@keyframes accordion-down/up` (height `0 ↔ var(--radix-accordion-content-height)`), `0.3s var(--ease-quart-in-out)`.

## 9. Stopka — easter egg (karuzela + auto-dojazd)
- **Trigger**: user na dole strony „dościska" scroll — akumulacja `deltaY ≥ 240px` (touch: `delta*2.5`) → start.
- **Auto-scroll**: blokada inputu (`preventDefault` wheel/touchmove), `lenis.stop()`, GSAP scrolluje do końca dokumentu: `duration = clamp(0.95, 1.2, 0.85 + 0.3*(remaining/viewportH))`, `ease: sine.inOut`; motion value `Y` rośnie z postępem; przy `progress ≥ 0.78` odpala finał.
- **Transformacje sceny** (`useTransform(Y, [0, 1, 1.16], …)`): scale `1→.75→.7`, opacity `1→1→0`/`1→1→.1`, translateY `0→−70vh→−70vh−10vh` (mobile 55vh), itd.
- **Finał** (motion `animate()` sequence):
  - `Y → 1.16`, `1.2s easeInOutSine`,
  - CTA panel `{opacity 1, y 0, scale 1}` `0.35s easeOutCubic` @ `1.18`,
  - napis (GSAP **SplitText** na znaki): `scale .85→1`, `color #F04E23 → #fff`, `0.55s easeOutCubic`, stagger `0.02s/znak` @ `1.22`,
  - ikona `scale .8→1 opacity 0→1` `0.25s` @ `1.22`,
  - karty `scale .85→1 opacity 0→1` `0.5s easeOutCubic`, stagger `0.05s` @ `1.32`.
- **Karuzela kart** (rAF, bez biblioteki): karty rozłożone na łuku `topRatio = 0.7 − 0.2*sin(...)` (mobile `.75/.1`), szer. karty `134px @1024` (`h = w*1.2388`), krok `w*0.5` (mobile `.35`);
  - baza: przesuw `28px/s` desktop / `42..28` (mobile 28), wrap modulo;
  - hover (mysz nad kartą): prędkość → 0 (lerp `0.22`/`0.08`), karta `scale 1 + 0.3*max(0, 1 − dist/300)`;
  - bobbing: `sin(0.025*offset + faza)*bob` (bob `7–12px`, pseudo-random z `sin(i)*43758.5453`), rotacja `±2.5°` (`0.018*offset`), parallax kursora `±8px` (lerp `.1/.14`).
  - kolory brandowe easter-egga: `#F04E23, #E8A33D, #2B86CB, #0A2C49`.

## 10. Mikrointerakcje globalne

### Przycisk „pixel arrow" (CTA)
- Strzałka z pikseli 2×2 (`--pixel-size: 2px`); trzy keyframes:
  - `button-pixel-arrow-draw`: `opacity 0→1, scale .6→1`, `--pixel-step-duration: 0.25s`, `cubic-bezier(.165,.84,.44,1)`,
  - `button-pixel-arrow-erase`: odwrotnie, z opóźnieniem `--pixel-erase-delay`,
  - `button-pixel-arrow-cycle`: `--pixel-cycle-duration: 0.9s linear` (sekwencja piksel po pikselu na hover).

### Noise / grain overlay
- `@keyframes noise` — skoki `background-position` co 20% (`96,-64 / -80,112 / 128,48 / -48,-96 px`), `3s steps(5,end) infinite`.

### Nagłówek / menu mobilne
- Ikona hamburgera: morph SVG path (`d: "M3 6H21" ↔ "M3 12H21"`, druga linia `M3 18H21 ↔ M3 12H21`) — linie schodzą się do środka.
- Dropdowny: `initial {opacity 0, y −4/+5} → {opacity 1, y 0}`; tw-animate klasy `fade-in-0 zoom-in-95 slide-in-from-top` itp.

### Obrazy (globalnie)
- Next/Image + blur placeholder (SVG gradient), po load: `blur-sm opacity-60 → blur-none opacity-100`, `500ms cubic-bezier(0.23,1,0.32,1)`.

### Brand hero (podstrony)
- `brand-hero-fade-in`: `opacity 0→1, scale 1.04→1`, `1.4s ease-out both`.
- `brand-hero-gradient-drift`: `translate3d Y ±5%` (`--brand-hero-gradient-drift-distance`, wariant 8%), `12s ease-in-out infinite alternate` (i `8s alternate-reverse` dla drugiej warstwy).

---

## 11. Ściąga do odtworzenia (rekomendowany stack)

```bash
npm i gsap lenis framer-motion three postprocessing
```

Minimalna architektura jak u nich:
1. `ReactLenis root` + `prefers-reduced-motion` gate.
2. Jeden globalny event-bus (mitt/własny) między Reactem a klasami Three.js.
3. WebGL: jeden renderer + composer, sceny per sekcja (`Scene Hero`, `Scene Models`), pass barrel+dither (uniforms jak w §3).
4. Sekcje UI w Framer Motion z variants + wartości z §2/§4; wszystkie easingi z tablicy w §1.
5. CSS keyframes skopiowane z §7–§10.

Pobrane artefakty analizy (HTML + 27 chunków JS + 2 CSS) leżą w scratchpadzie sesji:
`/private/tmp/claude-501/-Users-jan-glebocki-Desktop-Personal-website/09336808-eded-480f-ab11-47a5036b69ec/scratchpad/melius/`.
