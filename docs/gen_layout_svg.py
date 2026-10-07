#!/usr/bin/env python3
"""Generate docs/layout.svg from the hand-maintained layer data below.

NOTE: If config/cradio.keymap changes, have an LLM (e.g. Claude Code) update the
layer and combo data in this script to match, then regenerate the SVG.

Update the data when config/cradio.keymap changes, then run:
    python3 docs/gen_layout_svg.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

KEY, GAP, HALF_GAP = 46, 4, 36
STEP = KEY + GAP
PANEL_W = 10 * STEP + HALF_GAP
PANEL_H = 4 * STEP + 56
MARGIN = 24

COLORS = {  # kind: (fill, stroke, text)
    "n": ("#ffffff", "#9aa3b2", "#1f2937"),
    "trans": ("#f3f4f6", "#d1d5db", "#9ca3af"),
    "mod": ("#fef3c7", "#d97706", "#78350f"),
    "layer": ("#dbeafe", "#2563eb", "#1e3a8a"),
    "sys": ("#fee2e2", "#dc2626", "#7f1d1d"),
}


def esc(t):
    return escape(t, {"'": "&#39;", '"': "&#34;"})


def K(main, sub=None, kind="n"):
    return (main, sub, kind)


T = K("", None, "trans")


def plain(s):
    return [K(c) for c in s.split()]


def autoshift(pairs):
    return [K(a, b) for a, b in pairs]


DEFAULT = (
    autoshift(zip("qwfpb", "QWFPB")) + autoshift(zip("jluy", "JLUY")) + [K(";", ":")]
    + autoshift(zip("arstg", "ARSTG")) + autoshift(zip("mneio", "MNEIO"))
    + autoshift(zip("zxcdv", "ZXCDV")) + autoshift(zip("khc", "KHC"))[:2]
    + [K(",", "<"), K(".", ">"), K("/", "?")]
    + [K("NAV", "hold", "layer"), K("Space", "hold Shift", "mod"),
       K("Enter", "hold Gui", "mod"), K("SYM", "hold", "layer")]
)

NAV = (
    [T] * 5 + [T, K("Home"), K("PgDn"), K("PgUp"), K("End")]
    + [K("Alt", "sticky", "mod"), K("Gui", "sticky", "mod"), K("Shift", "sticky", "mod"),
       K("Ctrl", "sticky", "mod"), T, T, K("←"), K("↓"), K("↑"), K("→")]
    + [K("^Z"), K("^X"), K("^C"), K("Esc"), K("^V"), T, K("Tab"), K("^−"), K("^+"), T]
    + [T] * 4
)

SYM = (
    plain("! @ # $ %") + [T] * 5
    + plain("/ * - +") + [T, T,
       K("Ctrl", "sticky", "mod"), K("Shift", "sticky", "mod"),
       K("Gui", "sticky", "mod"), K("Alt", "sticky", "mod")]
    + [K("^"), K("&"), K("`", "~"), K("\\", "|"), T, T, K("Tab"), K("Vol−"), K("Vol+"), K("Play")]
    + [T] * 4
)

NUM = (
    plain("F1 F2 F3 F4") + [K("Ins")] + [K("Del"), K("7"), K("8"), K("9"), K(";", ":")]
    + plain("F5 F6 F7 F8") + [K("PrtSc")] + [K("Bksp"), K("4"), K("5"), K("6"), K("0")]
    + plain("F9 F10 F11 F12") + [K("Boot", None, "sys")] + [K(","), K("1"), K("2"), K("3"), K(".")]
    + [T] * 4
)

GAMING = (
    plain("Tab Q W E R Y U I O P")
    + [K("Shift")] + plain("A S D F H J K L '")
    + [K("Ctrl")] + plain("Z X C V N M , . /")
    + [K("Space"), K("Esc"), K("Esc"), K("Space")]
)

BLUETOOTH = (
    [T] * 10
    + [T] * 5 + [T, K("BT 0"), K("BT 1"), K("BT 2"), K("BT 3")]
    + [T] * 5 + [T, K("BT 4"), K("Clear", None, "sys"), K("Studio", "unlock", "sys"), T]
    + [T] * 4
)

PANELS = [
    ("DEFAULT", "base layer · letters auto-shift (hold = shifted)", DEFAULT),
    ("NAV", "hold left thumb", NAV),
    ("SYM", "hold right thumb", SYM),
    ("NUM", "hold NAV + SYM together", NUM),
    ("GAMING", "toggle: F + R + T", GAMING),
    ("BLUETOOTH", "toggle: Q + A + Z", BLUETOOTH),
]

# (what it does, extra note, key positions as numbered in config/cradio.keymap)
COMBOS = [
    ("Del", "", [1, 2]),
    ("Backspace", "not on NAV", [11, 12]),
    ("Esc", "not on NAV", [21, 22]),
    ("Tab", "", [27, 28]),
    ("Gui", "not on NAV", [11, 12, 13]),
    ("Right Alt", "left side", [21, 22, 23]),
    ("Right Alt", "right side", [26, 27, 28]),
    ('" (double quote)', "", [7, 8]),
    ("' (quote)", "not on SYM", [17, 18]),
    ("-", "hold for _", [13, 14]),
    ("_", "", [23, 24]),
    ("=", "hold for +", [15, 16]),
    ("+", "", [25, 26]),
    ("{", "", [2, 3]),
    ("}", "", [6, 7]),
    ("(", "not on NAV", [12, 13]),
    (")", "not on SYM", [16, 17]),
    ("[", "", [22, 23]),
    ("]", "", [26, 27]),
    ("Caps word", "", [31, 32]),
    ("Alt-Tab / hold Ctrl", "", [30, 31]),
    ("Gui-Tab / hold Alt", "", [32, 33]),
    ("Gui+Ctrl+Enter", "", [30, 31, 32, 33]),
    ("Terminal", "Gui+Alt+T", [16, 17, 18]),
    ("Gaming layer", "toggle", [2, 11, 13]),
    ("Bluetooth layer", "toggle", [0, 10, 20]),
    ("Reboot half", "reset", [1, 2, 7, 8]),
    ("Bootloader", "UF2 flash mode", [3, 4, 5, 6]),
]


def key_svg(x, y, k, w=KEY):
    main, sub, kind = k
    fill, stroke, text = COLORS[kind]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{KEY}" rx="6" fill="{fill}" stroke="{stroke}"/>']
    cx, cy = x + w / 2, y + KEY / 2
    if kind == "trans":
        out.append(f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="13" fill="{text}">▽</text>')
        return "".join(out)
    size = 16 if len(main) <= 2 else 12 if len(main) <= 5 else 10
    if sub:
        out.append(f'<text x="{cx}" y="{cy - 1}" text-anchor="middle" font-size="{size}" font-weight="600" fill="{text}">{esc(main)}</text>')
        out.append(f'<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-size="9" fill="{text}" opacity="0.75">{esc(sub)}</text>')
    else:
        out.append(f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="{size}" font-weight="600" fill="{text}">{esc(main)}</text>')
    return "".join(out)


def panel_svg(ox, oy, title, subtitle, keys):
    out = [f'<text x="{ox}" y="{oy + 16}" font-size="15" font-weight="700" fill="#111827">{escape(title)}</text>',
           f'<text x="{ox + len(title) * 11 + 12}" y="{oy + 16}" font-size="11" fill="#6b7280">{escape(subtitle)}</text>']
    top = oy + 28
    for i, k in enumerate(keys[:30]):
        row, col = divmod(i, 10)
        x = ox + col * STEP + (HALF_GAP if col >= 5 else 0)
        out.append(key_svg(x, top + row * STEP, k))
    # thumbs sit under the two inner columns of each half
    for j, k in enumerate(keys[30:]):
        col = [3, 4, 5, 6][j]
        x = ox + col * STEP + (HALF_GAP if col >= 5 else 0)
        out.append(key_svg(x, top + 3 * STEP, k))
    return "".join(out)


MK, MG, MHALF = 11, 2, 10  # mini key size, gap, gap between halves
MSTEP = MK + MG
MINI_W = 10 * MSTEP + MHALF - MG
MINI_H = 4 * MSTEP - MG


def mini_svg(ox, oy, lit):
    out = []
    for i in range(34):
        if i < 30:
            row, col = divmod(i, 10)
        else:
            row, col = 3, [3, 4, 5, 6][i - 30]
        x = ox + col * MSTEP + (MHALF - MG if col >= 5 else 0)
        y = oy + row * MSTEP
        fill, stroke = ("#2563eb", "#1e3a8a") if i in lit else ("#ffffff", "#c4cad4")
        out.append(f'<rect x="{x}" y="{y}" width="{MK}" height="{MK}" rx="2.5" fill="{fill}" stroke="{stroke}"/>')
    return "".join(out)


def main():
    cols = 2
    rows = (len(PANELS) + 1) // 2
    width = MARGIN * 2 + cols * PANEL_W + (cols - 1) * 40
    panels_h = rows * (PANEL_H + 12)
    combo_cols = 6
    combo_rows = -(-len(COMBOS) // combo_cols)
    CELL_H = 110
    height = MARGIN * 2 + 30 + panels_h + 40 + combo_rows * CELL_H + 10
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="ui-sans-serif, system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#f9fafb"/>',
        f'<text x="{MARGIN}" y="{MARGIN + 14}" font-size="20" font-weight="700" fill="#111827">Cradio layout</text>',
    ]
    y0 = MARGIN + 30
    for i, (t, s, keys) in enumerate(PANELS):
        r, c = divmod(i, cols)
        parts.append(panel_svg(MARGIN + c * (PANEL_W + 40), y0 + r * (PANEL_H + 12), t, s, keys))
    cy = y0 + panels_h + 24
    parts.append(f'<text x="{MARGIN}" y="{cy}" font-size="15" font-weight="700" fill="#111827">COMBOS</text>')
    parts.append(f'<text x="{MARGIN + 90}" y="{cy}" font-size="11" fill="#6b7280">'
                 f'press the highlighted keys together · all combos work on every layer unless noted</text>')
    colw = (width - 2 * MARGIN) / combo_cols
    for i, (name, note, lit) in enumerate(COMBOS):
        r, c = divmod(i, combo_cols)
        x, y = MARGIN + c * colw, cy + 14 + r * CELL_H
        parts.append(f'<rect x="{x}" y="{y}" width="{colw - 10}" height="{CELL_H - 10}" rx="8" fill="#ffffff" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{x + 10}" y="{y + 19}" font-size="12" font-weight="700" fill="#111827">{esc(name)}</text>')
        if note:
            parts.append(f'<text x="{x + 10}" y="{y + 33}" font-size="10" fill="#6b7280">{esc(note)}</text>')
        parts.append(mini_svg(x + (colw - 10 - MINI_W) / 2, y + 40, lit))
    parts.append("</svg>")
    out = Path(__file__).with_name("layout.svg")
    out.write_text("\n".join(parts), encoding="utf-8")
    print("wrote", out)


main()
