#!/usr/bin/env python3
"""Pixel-art sprite generator for the site.

Each sprite is an ASCII grid; letters map to PALETTE below. Run this file to
rewrite every .svg in this folder. Sprites are tuned for a light background,
so bodies are ink-dark with cream/amber highlights.
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

PALETTE = {
    "K": "#1c1a15",  # ink — main body
    "k": "#3b362c",  # ink shade
    "C": "#f4f0e6",  # cream fill
    "c": "#d9d2c2",  # cream shade
    "W": "#ffffff",  # white
    "O": "#ff6a3d",  # accent orange
    "Q": "#c9400f",  # accent shade
    "B": "#3d6fb5",  # blue
    "b": "#27497a",  # blue shade
    "G": "#3f9d5a",  # terminal green
    "Y": "#e8a33d",  # amber / lit window
    "R": "#d9453a",  # red
    "M": "#8a8375",  # muted gray
    "S": "#e6b18c",  # skin
    "s": "#c98f6b",  # skin shade
    "H": "#4a3524",  # hair
    "h": "#6b4d33",  # hair light
    "P": "#ff6a3d",  # beacon (same orange, animated separately)
}


def grid_to_svg(rows, name, classes=None, extra="", style=""):
    """Render an ASCII grid to SVG.

    classes: char -> css class. Cells of that char are emitted one-per-rect
    (no run-length merging) and carry a --i index so CSS can stagger them.
    extra:   raw SVG markup appended inside the root.
    style:   CSS placed in an internal <style>, so animation survives when the
             file is used as an <img> source.
    """
    classes = classes or {}
    h = len(rows)
    w = max(len(r) for r in rows)
    rects = []
    counter = 0
    for y, row in enumerate(rows):
        x = 0
        n = len(row)
        while x < n:
            ch = row[x]
            if ch not in PALETTE:
                x += 1
                continue
            if ch in classes:
                rects.append(
                    f'<rect x="{x}" y="{y}" width="1" height="1" '
                    f'fill="{PALETTE[ch]}" class="{classes[ch]}" style="--i:{counter}"/>'
                )
                counter += 1
                x += 1
                continue
            x2 = x
            while x2 + 1 < n and row[x2 + 1] == ch:
                x2 += 1
            rects.append(
                f'<rect x="{x}" y="{y}" width="{x2 - x + 1}" height="1" fill="{PALETTE[ch]}"/>'
            )
            x = x2 + 1
    css = f"<style>{style}</style>" if style else ""
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges">{css}{"".join(rects)}{extra}</svg>'
    )
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(svg)
    print(f"{name}.svg  {w}x{h}")


# ---------------------------------------------------------------- sprites

coffee = [
    ".....k..k.......",
    "....k..k........",
    ".....k..k.......",
    "................",
    "..KKKKKKKKKK....",
    "..KOOOOOOOOK.KK.",
    "..KCCCCCCCCK.K.K",
    "..KCCCCCCCCK...K",
    "..KCCCCCCCCK.K.K",
    "..KCCCCCCCCK.KK.",
    "..KCCCCCCCCK....",
    "...KCCCCCCK.....",
    "....KKKKKK......",
    "................",
    ".KKKKKKKKKKKKK..",
]

terminal = [
    "KKKKKKKKKKKKKKKKKKKK",
    "KRKYKGKKKKKKKKKKKKKK",
    "KKKKKKKKKKKKKKKKKKKK",
    "kkkkkkkkkkkkkkkkkkkk",
    "kkkkkkkkkkkkkkkkkkkk",
    "kkGkkkkkkkkkkkkkkkkk",
    "kkkGkkOOkkkkkkkkkkkk",
    "kkkkGkOOkkkkkkkkkkkk",
    "kkkGkkOOkkkkkkkkkkkk",
    "kkGkkkkkkkkkkkkkkkkk",
    "kkkkkkkkkkkkkkkkkkkk",
    "kkMMMMMMMMMkkkkkkkkk",
    "kkkkkkkkkkkkkkkkkkkk",
    "kkMMMMMMkkkkkkkkkkkk",
    "kkkkkkkkkkkkkkkkkkkk",
    "kkkkkkkkkkkkkkkkkkkk",
]

robot = [
    ".......OO.......",
    ".......KK.......",
    "....KKKKKKKK....",
    "...KKKKKKKKKK...",
    "...KWWKKKKWWK...",
    "...KWWKKKKWWK...",
    "...KKKKKKKKKK...",
    "....KKGGGGKK....",
    "......KKKK......",
    "...KKKKKKKKKK...",
    "...KKKKOOKKKK...",
    "...KKKKOOKKKK...",
    "...K.KKKKKK.K...",
    "...K.KKKKKK.K...",
    ".....KK..KK.....",
    "....KK....KK....",
]

gear = [
    "....KK....",
    ".KK.KK.KK.",
    ".KKKKKKKK.",
    "..KKKKKK..",
    "KKKKOOKKKK",
    "KKKKOOKKKK",
    "..KKKKKK..",
    ".KKKKKKKK.",
    ".KK.KK.KK.",
    "....KK....",
]

floppy = [
    "BBBBBBBBBBBBB..",
    "BBBBKKKKKBBBB..",
    "BBBBKKKCKBBBBB.",
    "BBBBKKKCKBBBBBB",
    "BBBBKKKKKBBBBBB",
    "BBBBBBBBBBBBBBB",
    "BbBBBBBBBBBBBbB",
    "BBCCCCCCCCCCCBB",
    "BBCCCCCCCCCCCBB",
    "BBCkkkkkkkkkCBB",
    "BBCCCCCCCCCCCBB",
    "BBCkkkkkkCCCCBB",
    "BBCCCCCCCCCCCBB",
    "BbBBBBBBBBBBBbB",
]

star = [
    "......OO......",
    "......OO......",
    ".....OOOO.....",
    ".....OOOO.....",
    "OOOOOOOOOOOOOO",
    ".OOOOOOOOOOOO.",
    "..OOOOOOOOOO..",
    "...OOOOOOOO...",
    "...OOOOOOOO...",
    "..OOOO..OOOO..",
    "..OOO....OOO..",
    ".OOO......OOO.",
    ".OO........OO.",
]

chart = [
    ".............OOO",
    ".............OOO",
    ".............OOO",
    ".........KKK.OOO",
    ".........KKK.OOO",
    ".........KKK.OOO",
    ".....KKK.KKK.OOO",
    ".....KKK.KKK.OOO",
    ".....KKK.KKK.OOO",
    ".KKK.KKK.KKK.OOO",
    ".KKK.KKK.KKK.OOO",
    ".KKK.KKK.KKK.OOO",
    ".KKK.KKK.KKK.OOO",
    "KKKKKKKKKKKKKKKK",
]

funnel = [
    "KKKKKKKKKKKKKKKK",
    "KOOOOOOOOOOOOOOK",
    "KOOOOOOOOOOOOOOK",
    "KKKKKKKKKKKKKKKK",
    ".KOOOOOOOOOOOOK.",
    ".KOOOOOOOOOOOOK.",
    ".KKKKKKKKKKKKKK.",
    "...KOOOOOOOOK...",
    "...KOOOOOOOOK...",
    "...KKKKKKKKKK...",
    "......KOOK......",
    "......KOOK......",
    "......KKKK......",
    ".......OO.......",
    ".......OO.......",
]

target = [
    ".....KKKKKK.....",
    "...KKCCCCCCKK...",
    "..KCCCCCCCCCCK..",
    ".KCCCKKKKKKCCCK.",
    ".KCCKCCCCCCKCCK.",
    "KCCCKCCOOCCKCCCK",
    "KCCCKCOOOOCKCCCK",
    "KCCCKCOOOOCKCCCK",
    "KCCCKCCOOCCKCCCK",
    "KCCCKCCCCCCKCCCK",
    ".KCCKKKKKKKKCCK.",
    ".KCCCCCCCCCCCCK.",
    "..KCCCCCCCCCCK..",
    "...KKCCCCCCKK...",
    ".....KKKKKK.....",
]

briefcase = [
    ".....KKKKKK.....",
    ".....K....K.....",
    "..KKKKKKKKKKKK..",
    "..KCCCCCCCCCCK..",
    "..KCCCCCCCCCCK..",
    "..KKKKKOOKKKKK..",
    "..KKKKKOOKKKKK..",
    "..KCCCCCCCCCCK..",
    "..KCCCCCCCCCCK..",
    "..KCCCCCCCCCCK..",
    "..KKKKKKKKKKKK..",
]

jan = [
    ".....hHHHHh.......",
    "...HHHHHHHHHh.....",
    "..HHhHHHHHHHHH....",
    "..HHHHHHHHHHHHh...",
    "..HHSSSSSSSSHH....",
    "..HSSSSSSSSSSH....",
    "..HSSKSSSSKSSH....",
    "...SSSSSSSSSS.....",
    "...SSSSSSSSSS.....",
    "...SsSSSSSSsS.....",
    "...SsSSssSSsS.....",
    "...sSSSSSSSSs.....",
    "....sSSSSSSs......",
    "......SSSS........",
    "...KWWWSSWWWK.....",
    "..KWWWWWWWWWWK....",
    ".KWWWWWWWWWWWWK...",
    ".KWWSSSSSSSSWWK...",
    ".KWWWWWWWWWWWWK...",
    ".KKKKKKKKKKKKKK...",
]


# ------------------------------------------------- WAW <-> SF skyline scene

def build_scene():
    """Europe on the left, the United States on the right, one shoreline."""
    W, H = 208, 46
    GROUND = 40
    WATER = 41
    g = [["." for _ in range(W)] for _ in range(H)]

    def px(x, y, ch, only_empty=False):
        if 0 <= x < W and 0 <= y < H:
            if not only_empty or g[y][x] == ".":
                g[y][x] = ch

    def rect(x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px(x, y, ch)

    def windows(x0, y0, x1, y1, stepx=3, stepy=3):
        for y in range(y0, y1 + 1, stepy):
            for x in range(x0, x1 + 1, stepx):
                px(x, y, "Y")

    def block(x0, x1, top):
        rect(x0, top, x1, GROUND, "K")
        windows(x0 + 1, top + 2, x1 - 1, GROUND - 2)

    # --- bay ---------------------------------------------------------
    rect(0, WATER, W - 1, H - 1, "B")
    for i, y in enumerate(range(WATER, H)):
        for x in range((i * 3) % 7, W, 7):
            px(x, y, "b")
    rect(0, GROUND, 159, GROUND, "k")  # quay on the city side

    # =============================================== EUROPE (left) ===
    block(4, 11, 29)
    block(38, 44, 31)
    block(79, 85, 32)

    # Warsaw - Palace of Culture and Science, stepped tiers into a spire
    rect(14, 34, 34, GROUND, "K")
    rect(18, 27, 30, 33, "K")
    rect(20, 20, 28, 26, "K")
    rect(22, 13, 26, 19, "K")
    rect(23, 8, 25, 12, "K")
    rect(24, 3, 24, 7, "K")
    px(24, 2, "P")  # aircraft beacon on the spire
    windows(16, 36, 33, GROUND - 1, stepx=3, stepy=2)
    windows(19, 29, 29, 32, stepx=3, stepy=2)
    windows(21, 22, 27, 25, stepx=2, stepy=2)
    windows(23, 15, 25, 18, stepx=2, stepy=2)

    # Paris - Eiffel Tower: splayed legs, two platforms, a thin spire
    ex = 56
    px(ex, 2, "K")
    rect(ex, 3, ex, 6, "K")
    for y in range(7, GROUND + 1):
        hw = round(1 + 9 * (((y - 7) / (GROUND - 7)) ** 1.9))
        px(ex - hw, y, "K")
        px(ex - hw + 1, y, "K")
        px(ex + hw, y, "K")
        px(ex + hw - 1, y, "K")
    rect(ex - 4, 15, ex + 4, 15, "K")   # upper platform
    rect(ex - 7, 26, ex + 7, 26, "K")   # lower platform
    for x in range(ex - 6, ex + 7):     # arch under the lower platform
        px(x, 27 + round(3 * (1 - (abs(x - ex) / 6) ** 2)), "K", only_empty=True)

    # London - Big Ben
    bx = 70
    rect(bx, 8, bx, 10, "K")
    for y in range(11, 16):             # pointed roof
        hw = y - 11
        rect(bx - hw, y, bx + hw, y, "K")
    rect(bx - 4, 16, bx + 4, GROUND, "K")
    rect(bx - 2, 19, bx + 2, 23, "C")   # clock face
    px(bx, 21, "K")                     # hands
    px(bx, 20, "K")
    px(bx + 1, 21, "K")
    windows(bx - 2, 26, bx + 2, GROUND - 2, stepx=2, stepy=3)

    # ======================================== UNITED STATES (right) ===
    block(118, 124, 31)

    # New York - Empire State Building, stepped setbacks
    nx = 134
    rect(nx, 4, nx, 9, "K")
    rect(nx - 1, 10, nx + 1, 16, "K")
    rect(nx - 3, 17, nx + 3, 24, "K")
    rect(nx - 5, 25, nx + 5, 32, "K")
    rect(nx - 8, 33, nx + 8, GROUND, "K")
    windows(nx - 2, 19, nx + 2, 23, stepx=2, stepy=2)
    windows(nx - 4, 27, nx + 4, 31, stepx=2, stepy=2)
    windows(nx - 7, 35, nx + 7, GROUND - 1, stepx=3, stepy=2)

    # San Francisco - Transamerica pyramid
    apex_x, apex_y = 152, 18
    for y in range(apex_y, GROUND + 1):
        hw = round((y - apex_y) * 0.28)
        rect(apex_x - hw, y, apex_x + hw, y, "K")
    windows(apex_x, apex_y + 4, apex_x, GROUND - 2, stepx=3, stepy=3)

    # San Francisco - Golden Gate
    DECK, TOP = 33, 17
    TX = (174, 200)
    rect(160, DECK, W - 1, DECK, "O")
    rect(160, DECK + 1, W - 1, DECK + 1, "Q")
    for tx in TX:
        rect(tx - 1, TOP, tx - 1, DECK - 1, "O")
        rect(tx + 1, TOP, tx + 1, DECK - 1, "O")
        rect(tx - 1, TOP - 1, tx + 1, TOP - 1, "Q")
        for cy in (21, 26, 30):
            px(tx, cy, "Q")
        rect(tx - 1, DECK + 2, tx - 1, H - 1, "Q")
        rect(tx + 1, DECK + 2, tx + 1, H - 1, "Q")

    mid, half = sum(TX) / 2, (TX[1] - TX[0]) / 2
    for x in range(TX[0], TX[1] + 1):
        px(x, round(TOP + 12 * (1 - ((x - mid) / half) ** 2)), "O", only_empty=True)
    for x in range(160, TX[0]):
        px(x, round(DECK - (DECK - TOP) * ((x - 160) / (TX[0] - 160))), "O", only_empty=True)
    for x in range(TX[1] + 1, W):
        px(x, round(TOP + (DECK - TOP) * ((x - TX[1]) / (W - 1 - TX[1]))), "O", only_empty=True)

    # suspender ropes hanging from the cable down to the deck
    for x in range(162, W, 4):
        top = next((y for y in range(TOP - 1, DECK) if g[y][x] == "O"), None)
        if top is not None:
            for y in range(top + 1, DECK):
                px(x, y, "Q", only_empty=True)

    # the two sides are linked, but nothing flies between them
    ax0, ax1, apex = 92, 112, 12
    for x in range(ax0, ax1 + 1, 3):
        t = (x - (ax0 + ax1) / 2) / ((ax1 - ax0) / 2)
        px(x, round(apex + 14 * t * t), "M", only_empty=True)

    return ["".join(r) for r in g]


# Clouds drift across the sky and a boat crosses the bay. Both live outside
# the grid so they can animate independently.
def _cloud(y, cls, big=False):
    if big:
        rows = ["..XXXX..", ".XXXXXXX", "XXXXXXXX"]
    else:
        rows = ["..XXX.", ".XXXXX"]
    body = "".join(
        f'<rect x="{x}" y="{y + r}" width="1" height="1" fill="#cfc7b4"/>'
        for r, row in enumerate(rows) for x, ch in enumerate(row) if ch == "X")
    return f'<g class="{cls}">{body}</g>'


SCENE_EXTRA = (
    _cloud(6, "cloud1", big=True)
    + _cloud(14, "cloud2")
    + _cloud(3, "cloud3")
    + '<g class="boat">'
      '<rect x="0" y="43" width="8" height="2" fill="#1c1a15"/>'
      '<rect x="1" y="42" width="6" height="1" fill="#3b362c"/>'
      '<rect x="3" y="38" width="1" height="4" fill="#1c1a15"/>'
      '<rect x="4" y="38" width="1" height="1" fill="#ff6a3d"/>'
      '<rect x="4" y="39" width="2" height="1" fill="#ff6a3d"/>'
      '<rect x="4" y="40" width="3" height="1" fill="#ff6a3d"/>'
      "</g>"
)

SCENE_STYLE = (
    # windows flicker off for a beat, staggered so the city feels inhabited
    "@keyframes win{0%,92%{opacity:1}94%,97%{opacity:.18}100%{opacity:1}}"
    ".win{animation:win 9s steps(1,end) infinite;"
    "animation-delay:calc(var(--i) * -0.41s);"
    "animation-duration:calc(7s + (var(--i) % 5) * 1.5s)}"
    # bay speckles drift in and out
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.25}}"
    ".wave{animation:wave 5s ease-in-out infinite;"
    "animation-delay:calc(var(--i) * -0.23s)}"
    # beacon on the Palace spire
    "@keyframes beacon{0%,55%{opacity:1}60%,100%{opacity:.15}}"
    ".beacon{animation:beacon 1.8s steps(1,end) infinite}"
    # clouds cross the whole scene and wrap round
    "@keyframes cross{from{transform:translateX(-14px)}to{transform:translateX(222px)}}"
    ".cloud1{animation:cross 74s linear infinite}"
    ".cloud2{animation:cross 104s linear infinite;animation-delay:-40s;opacity:.75}"
    ".cloud3{animation:cross 132s linear infinite;animation-delay:-88s;opacity:.6}"
    # a boat works its way along the bay
    "@keyframes sail{from{transform:translateX(-10px)}to{transform:translateX(218px)}}"
    ".boat{animation:sail 58s linear infinite}"
    "@media (prefers-reduced-motion:reduce){"
    ".win,.wave,.beacon,.cloud1,.cloud2,.cloud3{animation:none}"
    ".boat{display:none}}"
)


# ----------------------------------------------------- animated coffee scene

def build_coffee_scene():
    """Mug centred on the canvas, handle included in the balance."""
    W, H = 40, 40
    g = [["." for _ in range(W)] for _ in range(H)]

    def px(x, y, ch):
        if 0 <= x < W and 0 <= y < H:
            g[y][x] = ch

    def rect(x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                px(x, y, ch)

    CUP_L, CUP_R = 6, 28
    RIM, BOTTOM = 15, 32

    # handle first, so the cup wall draws over the join
    rect(CUP_R, 19, CUP_R + 5, 20, "K")
    rect(CUP_R + 4, 21, CUP_R + 5, 25, "K")
    rect(CUP_R, 26, CUP_R + 5, 27, "K")

    rect(CUP_L, RIM, CUP_R, RIM, "K")
    rect(CUP_L + 1, RIM + 1, CUP_R - 1, RIM + 2, "Q")      # coffee

    for y in range(RIM + 3, BOTTOM):
        rect(CUP_L, y, CUP_L + 1, y, "K")
        rect(CUP_R - 1, y, CUP_R, y, "K")
        rect(CUP_L + 2, y, CUP_R - 2, y, "C")

    rect(CUP_L + 1, BOTTOM, CUP_R - 1, BOTTOM, "K")
    rect(CUP_L + 2, BOTTOM - 1, CUP_R - 2, BOTTOM - 1, "c")

    # saucer centred under the cup *and* the handle
    rect(3, 35, 36, 35, "K")
    rect(5, 36, 34, 36, "c")

    return ["".join(r) for r in g]


# Steam is kept out of the grid so each wisp can curl on its own path.
def _wisp(x, cls):
    cells = [(0, 0), (2, 1), (0, 2), (2, 3), (0, 4), (2, 5), (0, 6)]
    body = "".join(
        f'<rect x="{x + dx}" y="{6 + dy}" width="2" height="1" fill="#b3ab99"/>'
        for dx, dy in cells
    )
    return f'<g class="{cls}">{body}</g>'


COFFEE_EXTRA = (
    _wisp(9, "st1") + _wisp(15, "st2") + _wisp(21, "st3")
    + '<rect class="shimmer" x="8" y="16" width="6" height="1" fill="#ff8a5f"/>'
)

COFFEE_STYLE = (
    # each wisp drifts on its own curl so the steam never looks like a barcode
    "@keyframes steamA{0%{opacity:0;transform:translate(0,7px)}"
    "22%{opacity:.85}60%{transform:translate(-2px,-3px)}"
    "100%{opacity:0;transform:translate(-4px,-13px)}}"
    "@keyframes steamB{0%{opacity:0;transform:translate(0,7px)}"
    "22%{opacity:.95}60%{transform:translate(2px,-4px)}"
    "100%{opacity:0;transform:translate(3px,-14px)}}"
    "@keyframes steamC{0%{opacity:0;transform:translate(0,7px)}"
    "22%{opacity:.8}60%{transform:translate(-1px,-3px)}"
    "100%{opacity:0;transform:translate(1px,-12px)}}"
    ".st1{animation:steamA 3.4s ease-out infinite}"
    ".st2{animation:steamB 3.4s ease-out infinite;animation-delay:-1.15s}"
    ".st3{animation:steamC 3.4s ease-out infinite;animation-delay:-2.3s}"
    # highlight sliding across the surface of the coffee
    "@keyframes shimmer{0%,100%{transform:translateX(0);opacity:.5}"
    "50%{transform:translateX(13px);opacity:.9}}"
    ".shimmer{animation:shimmer 4.6s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){"
    ".st1,.st2,.st3,.shimmer{animation:none}"
    ".st2{opacity:.85}.st1,.st3{opacity:.5}}"
)


grid_to_svg(
    build_coffee_scene(),
    "coffee-scene",
    extra=COFFEE_EXTRA,
    style=COFFEE_STYLE,
)

grid_to_svg(
    build_scene(),
    "skyline",
    classes={"Y": "win", "b": "wave", "P": "beacon"},
    extra=SCENE_EXTRA,
    style=SCENE_STYLE,
)


# ------------------------------------------------ parallax night band (footer)

def build_parallax():
    """Three silhouette layers scrolling at different speeds, plus a sky."""
    W, H = 200, 44

    def rng(seed):
        state = {"s": seed}
        def nxt():
            state["s"] = (state["s"] * 1103515245 + 12345) & 0x7fffffff
            return state["s"] / 0x7fffffff
        return nxt

    def skyline(seed, lo, hi, wmin, wmax, colour, lit=None):
        """A silhouette spanning exactly 0..W so the two copies tile seamlessly."""
        r = rng(seed)
        out = []
        x = 0
        while x < W:
            w = wmin + int(r() * (wmax - wmin + 1))
            if x + w > W:
                w = W - x
            h = lo + int(r() * (hi - lo + 1))
            top = H - h
            out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{colour}"/>')
            if lit and w >= 4 and h >= 8:
                for wy in range(top + 2, H - 3, 3):
                    for wx in range(x + 1, x + w - 1, 3):
                        roll = r()
                        if roll > 0.55:
                            # a few windows glow in the accent colour.
                            # note: must not shadow `colour`, that is the
                            # silhouette fill used by every later building
                            glow = "#ff6a3d" if roll > 0.94 else lit
                            out.append(
                                f'<rect x="{wx}" y="{wy}" width="1" height="1" fill="{glow}"/>')
            x += w
        return "".join(out)

    def band(cls, body):
        # drawn twice, one width apart, so the scroll never shows a gap
        return (f'<g class="{cls}">{body}'
                f'<g transform="translate({W},0)">{body}</g></g>')

    far = skyline(11, 6, 16, 5, 12, "#3a342a")
    mid = skyline(29, 12, 26, 4, 10, "#29231b", lit="#c08a35")
    near = skyline(47, 6, 12, 6, 14, "#0b0a07")

    r = rng(97)
    stars = "".join(
        f'<rect class="star" style="--i:{i}" x="{int(r() * W)}" y="{int(r() * 18)}" '
        f'width="1" height="1" fill="#f4f0e6"/>'
        for i in range(26)
    )
    moon = ('<g><rect x="172" y="5" width="7" height="7" fill="#e8a33d"/>'
            '<rect x="175" y="4" width="4" height="1" fill="#e8a33d"/>'
            '<rect x="175" y="12" width="4" height="1" fill="#e8a33d"/>'
            '<rect x="176" y="6" width="2" height="2" fill="#c9400f"/>'
            '<rect x="174" y="9" width="2" height="1" fill="#c9400f"/></g>')

    style = (
        "@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-200px)}}"
        ".far{animation:drift 96s linear infinite}"
        ".mid{animation:drift 54s linear infinite}"
        ".near{animation:drift 28s linear infinite}"
        "@keyframes twinkle{0%,88%{opacity:.85}92%,96%{opacity:.12}100%{opacity:.85}}"
        ".star{animation:twinkle 6s steps(1,end) infinite;"
        "animation-delay:calc(var(--i) * -0.29s);"
        "animation-duration:calc(4s + (var(--i) % 5) * 1.3s)}"
        "@media (prefers-reduced-motion:reduce){"
        ".far,.mid,.near,.star{animation:none}}"
    )

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'shape-rendering="crispEdges" preserveAspectRatio="none">'
            f'<style>{style}</style>{stars}{moon}'
            f'{band("far", far)}{band("mid", mid)}{band("near", near)}</svg>')


with open(os.path.join(OUT, "parallax.svg"), "w") as f:
    f.write(build_parallax())
print("parallax.svg  200x44")


# ------------------------------------------- ragged pixel frame for the photo

def build_photo_frame(W=50, H=40, seed=17):
    """A stepped silhouette plus a matching 2-cell border.

    Both files come from the same grid, so the mask and the frame line up
    exactly however the element is scaled.
    """
    state = {"s": seed}

    def rnd():
        state["s"] = (state["s"] * 1103515245 + 12345) & 0x7fffffff
        return state["s"] / 0x7fffffff

    inside = [[True] * W for _ in range(H)]

    def bite(x, y, w, h):
        for yy in range(y, min(y + h, H)):
            for xx in range(x, min(x + w, W)):
                if 0 <= xx < W and 0 <= yy < H:
                    inside[yy][xx] = False

    # ragged top and bottom edges
    for x in range(W):
        if rnd() > 0.62:
            bite(x, 0, 1, 1 if rnd() > 0.35 else 2)
        if rnd() > 0.62:
            depth = 1 if rnd() > 0.35 else 2
            bite(x, H - depth, 1, depth)
    # ragged left and right edges
    for y in range(H):
        if rnd() > 0.62:
            bite(0, y, 1 if rnd() > 0.35 else 2, 1)
        if rnd() > 0.62:
            depth = 1 if rnd() > 0.35 else 2
            bite(W - depth, y, depth, 1)
    # stepped corners, so the shape reads as deliberate pixel art
    for cx, cy in ((0, 0), (W - 3, 0), (0, H - 3), (W - 3, H - 3)):
        bite(cx, cy, 3, 1)
        bite(cx, cy, 1, 3)
        if cx:
            bite(cx + 2, cy, 1, 2)
            bite(cx, cy + 2, 3, 1) if cy else None

    def is_in(x, y):
        return 0 <= x < W and 0 <= y < H and inside[y][x]

    # border = the two innermost rings of the silhouette
    ring1 = {(x, y) for y in range(H) for x in range(W)
             if inside[y][x] and not all(is_in(x + dx, y + dy)
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    ring2 = {(x, y) for y in range(H) for x in range(W)
             if inside[y][x] and (x, y) not in ring1
             and any((x + dx, y + dy) in ring1
                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}

    def svg(cells, colour):
        rects = "".join(
            f'<rect x="{x}" y="{y}" width="1" height="1" fill="{colour}"/>'
            for x, y in sorted(cells))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
                f'preserveAspectRatio="none" shape-rendering="crispEdges">{rects}</svg>')

    # One overlay does both jobs: the bitten-out cells are painted in the page
    # colour so the photo appears to have ragged edges, and the two inner rings
    # form the border. A CSS mask would be cleaner, but Chrome refuses to load
    # mask images from file:// (opaque origin) and hides the element entirely.
    outside = [(x, y) for y in range(H) for x in range(W) if not inside[y][x]]
    rects = "".join(
        f'<rect x="{x}" y="{y}" width="1" height="1" fill="#f4f0e6"/>'
        for x, y in outside)
    rects += "".join(
        f'<rect x="{x}" y="{y}" width="1" height="1" fill="#1c1a15"/>'
        for x, y in sorted(ring1 | ring2))
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'preserveAspectRatio="none" shape-rendering="crispEdges">{rects}</svg>')
    with open(os.path.join(OUT, "photo-frame.svg"), "w") as f:
        f.write(out)
    print(f"photo-frame.svg  {W}x{H}  ({len(outside)} bitten, {len(ring1 | ring2)} border)")


build_photo_frame()
