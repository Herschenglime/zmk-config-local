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
    plain("F1 F2 F3 F4") + [K("Ins")] + [K("Del"), K("7"), K("8"), K("9"), K("Enter")]
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

COMBOS = [
    ("Del", "W F"), ("Bksp*", "R S"), ("Esc*", "X C"), ("Tab", ", ."),
    ("Gui*", "R S T"), ("RAlt", "X C D / H , ."), ('"', "U Y"), ("'†", "E I"),
    ("− (hold _)", "T G"), ("_", "D V"), ("= (hold +)", "M N"), ("+", "K H"),
    ("{", "F P"), ("}", "L U"), ("(*", "S T"), (")†", "N E"),
    ("[", "C D"), ("]", "H ,"), ("Caps word", "inner thumbs"),
    ("Alt-Tab/Ctrl", "left thumbs"), ("Gui-Tab/Alt", "right thumbs"),
    ("Gui^Ret", "all 4 thumbs"), ("Terminal", "N E I"),
    ("Gaming", "F R T"), ("Bluetooth", "Q A Z"),
    ("Reset", "W F U Y"), ("Bootloader", "P B J L"),
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


def main():
    cols = 2
    rows = (len(PANELS) + 1) // 2
    width = MARGIN * 2 + cols * PANEL_W + (cols - 1) * 40
    panels_h = rows * (PANEL_H + 12)
    combo_cols = 3
    combo_rows = -(-len(COMBOS) // combo_cols)
    height = MARGIN * 2 + 30 + panels_h + 40 + combo_rows * 20 + 30
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
                 f'press the keys on the DEFAULT layer together · * not on NAV · † not on SYM</text>')
    colw = (width - 2 * MARGIN) / combo_cols
    for i, (name, keys) in enumerate(COMBOS):
        c, r = divmod(i, combo_rows)
        x, y = MARGIN + c * colw, cy + 24 + r * 20
        parts.append(f'<text x="{x}" y="{y}" font-size="12" font-weight="600" fill="#1f2937">{esc(name)}</text>')
        parts.append(f'<text x="{x + 130}" y="{y}" font-size="12" fill="#6b7280" '
                     f'font-family="ui-monospace, Menlo, Consolas, monospace">{esc(keys)}</text>')
    parts.append("</svg>")
    out = Path(__file__).with_name("layout.svg")
    out.write_text("\n".join(parts), encoding="utf-8")
    print("wrote", out)


main()
