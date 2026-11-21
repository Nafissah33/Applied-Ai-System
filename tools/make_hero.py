"""Generate assets/clinic_team.svg: a shaded, 3D-style illustration of a vet team with pets.

Uses gradients, soft shadows, rim light and depth of field instead of flat colour. No external images needed.
Run: python tools/make_hero.py
"""
from pathlib import Path

W, H = 1200, 560


def _mix(hex_a, hex_b, t):
    a = [int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def lighten(c, t): return _mix(c, "#ffffff", t)
def darken(c, t): return _mix(c, "#000000", t)


_defs = []


def radial(gid, base, cx=".35", cy=".28", r=".85"):
    _defs.append(f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{lighten(base, .38)}"/>'
                 f'<stop offset=".45" stop-color="{base}"/><stop offset="1" stop-color="{darken(base, .38)}"/></radialGradient>')
    return f"url(#{gid})"


def linear(gid, top, bottom, x2="0", y2="1"):
    _defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{top}"/>'
                 f'<stop offset="1" stop-color="{bottom}"/></linearGradient>')
    return f"url(#{gid})"


def person(pid, cx, s, skin, hair, style, scrub, iris):
    sk = radial(f"{pid}sk", skin)
    skshade = darken(skin, .28)
    hr = linear(f"{pid}hr", lighten(hair, .22), darken(hair, .25), "0.4", "1")
    coat = linear(f"{pid}coat", "#ffffff", "#c9dbe4", "0.25", "1")
    scr = linear(f"{pid}scr", lighten(scrub, .25), darken(scrub, .22))
    hair_back = hair_front = ""
    if style == "long":
        hair_back = f'<path d="M-78 -418 Q-84 -515 0 -515 Q84 -515 78 -418 L88 -296 Q62 -284 56 -332 L-56 -332 Q-62 -284 -88 -296Z" fill="{hr}"/>'
    if style == "bun":
        hair_back = f'<circle cx="0" cy="-526" r="27" fill="{hr}"/><circle cx="-6" cy="-533" r="9" fill="#ffffff22"/>'
    top = "-512" if style != "short" else "-502"
    hair_front = (f'<path d="M-68 -418 Q-74 {top} 0 {top} Q74 {top} 68 -418 Q46 -464 0 -468 Q-46 -464 -68 -418Z" fill="{hr}"/>'
                  f'<path d="M-40 -470 Q-10 -500 30 -480" stroke="#ffffff55" stroke-width="7" fill="none" stroke-linecap="round"/>')
    return f'''
<g transform="translate({cx},{H}) scale({s})">
  <ellipse cx="0" cy="-2" rx="190" ry="20" fill="#06263d" opacity=".45" filter="url(#blur8)"/>
  {hair_back}
  <path d="M-168 0 L-168 -238 Q-168 -322 -92 -334 L92 -334 Q168 -322 168 -238 L168 0Z" fill="{coat}"/>
  <path d="M-168 -238 Q-168 -322 -92 -334" stroke="#ffffffcc" stroke-width="5" fill="none"/>
  <path d="M168 -230 Q166 -150 168 0 L130 0 Q136 -140 120 -260Z" fill="#7aa0b5" opacity=".35"/>
  <path d="M-64 -334 L0 -224 L64 -334Z" fill="{scr}"/>
  <path d="M-64 -334 L-12 -192 L-100 -232Z" fill="#f3f9fb" stroke="#bcd0d8" stroke-width="2"/>
  <path d="M64 -334 L12 -192 L100 -232Z" fill="#e4eef2" stroke="#bcd0d8" stroke-width="2"/>
  <rect x="-25" y="-362" width="50" height="40" rx="12" fill="{sk}"/>
  <ellipse cx="0" cy="-343" rx="30" ry="12" fill="{skshade}" opacity=".55" filter="url(#blur4)"/>
  <path d="M-46 -336 Q-74 -250 -22 -220" stroke="#27343b" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M46 -336 Q74 -250 22 -220" stroke="#27343b" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M-46 -336 Q-72 -252 -26 -224" stroke="#ffffff66" stroke-width="2" fill="none"/>
  <circle cx="0" cy="-206" r="17" fill="{radial(f"{pid}st", "#aab7bd")}" stroke="#27343b" stroke-width="5"/>
  <ellipse cx="-66" cy="-414" rx="11" ry="17" fill="{sk}"/><ellipse cx="66" cy="-414" rx="11" ry="17" fill="{sk}"/>
  <ellipse cx="0" cy="-418" rx="66" ry="77" fill="{sk}"/>
  <ellipse cx="0" cy="-362" rx="40" ry="10" fill="{skshade}" opacity=".35" filter="url(#blur4)"/>
  {hair_front}
  <path d="M-42 -444 Q-27 -454 -12 -445" stroke="{darken(hair, .1)}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <path d="M12 -445 Q27 -454 42 -444" stroke="{darken(hair, .1)}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="-26" cy="-424" rx="11" ry="7.5" fill="#fff"/><ellipse cx="26" cy="-424" rx="11" ry="7.5" fill="#fff"/>
  <circle cx="-26" cy="-424" r="5.6" fill="{iris}"/><circle cx="26" cy="-424" r="5.6" fill="{iris}"/>
  <circle cx="-26" cy="-424" r="2.7" fill="#0b0b0b"/><circle cx="26" cy="-424" r="2.7" fill="#0b0b0b"/>
  <circle cx="-24" cy="-426" r="1.6" fill="#fff"/><circle cx="28" cy="-426" r="1.6" fill="#fff"/>
  <path d="M-38 -428 Q-26 -436 -14 -428 M14 -428 Q26 -436 38 -428" stroke="#00000055" stroke-width="2" fill="none"/>
  <path d="M-3 -420 Q-9 -398 -3 -394 Q4 -392 8 -396" stroke="{skshade}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M-27 -378 Q0 -352 27 -378 Q0 -366 -27 -378Z" fill="#fff" stroke="#00000022" stroke-width="1"/>
  <path d="M-29 -379 Q0 -350 29 -379" stroke="#9b3a3a" stroke-width="4.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="-44" cy="-394" rx="12" ry="8" fill="#ff7f7f" opacity=".22" filter="url(#blur4)"/>
  <ellipse cx="44" cy="-394" rx="12" ry="8" fill="#ff7f7f" opacity=".22" filter="url(#blur4)"/>
  <ellipse cx="-30" cy="-470" rx="22" ry="9" fill="#ffffff" opacity=".12" filter="url(#blur4)"/>
  <rect x="62" y="-264" width="64" height="32" rx="5" fill="#fff" stroke="#c4d6dd"/><rect x="62" y="-264" width="64" height="10" rx="4" fill="#1FA89B"/>
  <rect x="70" y="-247" width="42" height="4" rx="2" fill="#9db4bb"/><rect x="70" y="-239" width="28" height="4" rx="2" fill="#9db4bb"/>
</g>'''


def shadow(x, y, rx):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*0.18}" fill="#04202f" opacity=".55" filter="url(#blur6)"/>'


def rottweiler(x, y, s=1.0):
    black = radial("rwb", "#34343a", ".38", ".25")
    tan = radial("rwt", "#c0733a", ".4", ".3")
    ear = linear("rwe", "#2a2a2f", "#0a0a0b")
    return shadow(x, y + 160 * s, 100 * s) + f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="0" cy="98" rx="96" ry="66" fill="{black}"/><path d="M-32 62 Q0 124 32 62 Q0 92 -32 62Z" fill="{tan}"/>
  <path d="M-74 -42 Q-122 -8 -100 66 Q-66 48 -54 -6Z" fill="{ear}"/><path d="M74 -42 Q122 -8 100 66 Q66 48 54 -6Z" fill="{ear}"/>
  <ellipse cx="0" cy="0" rx="78" ry="70" fill="{black}"/>
  <path d="M-52 -34 Q-30 -62 0 -62" stroke="#ffffff22" stroke-width="6" fill="none" stroke-linecap="round"/>
  <ellipse cx="-30" cy="-36" rx="13" ry="8" fill="{tan}"/><ellipse cx="30" cy="-36" rx="13" ry="8" fill="{tan}"/>
  <ellipse cx="0" cy="34" rx="46" ry="35" fill="{tan}"/><ellipse cx="-38" cy="22" rx="15" ry="21" fill="{tan}"/><ellipse cx="38" cy="22" rx="15" ry="21" fill="{tan}"/>
  <circle cx="-28" cy="-14" r="9" fill="#3a2410"/><circle cx="28" cy="-14" r="9" fill="#3a2410"/>
  <circle cx="-28" cy="-14" r="4.5" fill="#0b0b0b"/><circle cx="28" cy="-14" r="4.5" fill="#0b0b0b"/>
  <circle cx="-25" cy="-17" r="3" fill="#fff"/><circle cx="31" cy="-17" r="3" fill="#fff"/>
  <ellipse cx="0" cy="14" rx="21" ry="14" fill="#0a0a0b"/><ellipse cx="-6" cy="9" rx="8" ry="3.5" fill="#ffffff66"/>
  <path d="M0 27 L0 43 M-19 50 Q0 64 19 50" stroke="#0a0a0b" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M-9 54 Q0 86 9 54Z" fill="#e8738a"/><path d="M-5 58 Q0 74 5 58" stroke="#ffffff55" stroke-width="2" fill="none"/>
</g>'''


def husky(x, y, s=1.0):
    gray = radial("hkg", "#8d9aa8", ".38", ".25")
    white = radial("hkw", "#f6f9fb", ".4", ".3", ".95")
    return shadow(x, y + 160 * s, 100 * s) + f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="0" cy="98" rx="96" ry="66" fill="{gray}"/><ellipse cx="0" cy="108" rx="48" ry="52" fill="{white}"/>
  <path d="M-72 -30 L-60 -116 L-18 -52Z" fill="{gray}"/><path d="M72 -30 L60 -116 L18 -52Z" fill="{gray}"/>
  <path d="M-62 -48 L-55 -92 L-33 -57Z" fill="#f2b6c0"/><path d="M62 -48 L55 -92 L33 -57Z" fill="#f2b6c0"/>
  <ellipse cx="0" cy="2" rx="76" ry="68" fill="{gray}"/>
  <path d="M0 -64 Q-14 -34 -45 -26 Q-62 12 -35 54 Q0 76 35 54 Q62 12 45 -26 Q14 -34 0 -64Z" fill="{white}"/>
  <path d="M0 -64 L0 -30" stroke="#8d9aa8" stroke-width="11" stroke-linecap="round"/>
  <circle cx="-27" cy="-10" r="10" fill="#5fc4ee"/><circle cx="27" cy="-10" r="10" fill="#5fc4ee"/>
  <circle cx="-27" cy="-10" r="5" fill="#0d2438"/><circle cx="27" cy="-10" r="5" fill="#0d2438"/>
  <circle cx="-24" cy="-13" r="2.6" fill="#fff"/><circle cx="30" cy="-13" r="2.6" fill="#fff"/>
  <ellipse cx="0" cy="22" rx="18" ry="12" fill="#101216"/><ellipse cx="-5" cy="18" rx="7" ry="3" fill="#ffffff66"/>
  <path d="M0 33 L0 47 M-19 51 Q0 66 19 51" stroke="#101216" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M-9 55 Q0 86 9 55Z" fill="#ef7f95"/>
</g>'''


def cat(x, y, s, fur, stripe, eye, belly, cid):
    f = radial(f"{cid}f", fur, ".38", ".28")
    b = radial(f"{cid}b", belly, ".4", ".3")
    return shadow(x, y + 126 * s, 70 * s) + f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="0" cy="82" rx="64" ry="53" fill="{f}" stroke="#00000028" stroke-width="2.5"/><ellipse cx="0" cy="94" rx="31" ry="37" fill="{b}"/>
  <path d="M-54 -30 L-50 -94 L-8 -50Z" fill="{f}" stroke="#00000028" stroke-width="2.5"/><path d="M54 -30 L50 -94 L8 -50Z" fill="{f}" stroke="#00000028" stroke-width="2.5"/>
  <path d="M-46 -46 L-44 -78 L-22 -54Z" fill="#f4b6c0"/><path d="M46 -46 L44 -78 L22 -54Z" fill="#f4b6c0"/>
  <ellipse cx="0" cy="0" rx="66" ry="55" fill="{f}" stroke="#00000028" stroke-width="2.5"/>
  <path d="M-12 -52 L-8 -34 M0 -54 L0 -32 M12 -52 L8 -34" stroke="{stripe}" stroke-width="5" stroke-linecap="round"/>
  <path d="M-64 4 L-42 8 M-64 18 L-42 16 M64 4 L42 8 M64 18 L42 16" stroke="{stripe}" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="-22" cy="-6" rx="11" ry="13" fill="{eye}"/><ellipse cx="22" cy="-6" rx="11" ry="13" fill="{eye}"/>
  <ellipse cx="-22" cy="-6" rx="3.6" ry="11" fill="#10201a"/><ellipse cx="22" cy="-6" rx="3.6" ry="11" fill="#10201a"/>
  <circle cx="-19" cy="-12" r="3" fill="#fff"/><circle cx="25" cy="-12" r="3" fill="#fff"/>
  <path d="M-6 14 L6 14 L0 22Z" fill="#e8798f"/><path d="M0 22 Q-10 34 -18 28 M0 22 Q10 34 18 28" stroke="#6b4a3a" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <path d="M-64 -14 L-98 -22 M-64 -2 L-100 0 M64 -14 L98 -22 M64 -2 L100 0" stroke="#ffffffb0" stroke-width="2.5" stroke-linecap="round"/>
</g>'''


def snake(x, y, s=1.0):
    return shadow(x, y + 60 * s, 90 * s) + f'''
<g transform="translate({x},{y}) scale({s})">
  <path d="M-70 20 Q-90 -20 -40 -22 Q10 -24 14 8 Q18 40 -30 44 Q-80 48 -52 18" stroke="#1d6e47" stroke-width="26" fill="none" stroke-linecap="round"/>
  <path d="M-70 20 Q-90 -20 -40 -22 Q10 -24 14 8 Q18 40 -30 44 Q-80 48 -52 18" stroke="#3cb878" stroke-width="20" fill="none" stroke-linecap="round"/>
  <path d="M-70 20 Q-90 -20 -40 -22 Q10 -24 14 8 Q18 40 -30 44 Q-80 48 -52 18" stroke="#16573a" stroke-width="20" fill="none" stroke-linecap="round" stroke-dasharray="3 22"/>
  <path d="M-70 14 Q-86 -22 -40 -28 Q6 -30 8 4" stroke="#ffffff55" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M14 8 Q52 -16 66 -58" stroke="#1d6e47" stroke-width="26" fill="none" stroke-linecap="round"/>
  <path d="M14 8 Q52 -16 66 -58" stroke="#3cb878" stroke-width="20" fill="none" stroke-linecap="round"/>
  <path d="M14 8 Q52 -16 66 -58" stroke="#16573a" stroke-width="20" fill="none" stroke-linecap="round" stroke-dasharray="3 22"/>
  <ellipse cx="72" cy="-74" rx="23" ry="17" fill="{radial("snh", "#3cb878")}"/><circle cx="77" cy="-78" r="5.5" fill="#fff"/><circle cx="78" cy="-78" r="3" fill="#111"/>
  <path d="M92 -72 L114 -68 M114 -68 L122 -74 M114 -68 L122 -62" stroke="#d2335b" stroke-width="3" stroke-linecap="round" fill="none"/>
</g>'''


def turtle(x, y, s=1.0):
    shell = radial("tsh", "#3f8f5b", ".4", ".25")
    skin = radial("tsk", "#9ad586")
    return shadow(x, y + 46 * s, 70 * s) + f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="62" cy="14" rx="21" ry="17" fill="{skin}"/><circle cx="70" cy="9" r="3.5" fill="#222"/><circle cx="71" cy="8" r="1.2" fill="#fff"/>
  <ellipse cx="-30" cy="38" rx="17" ry="11" fill="{skin}"/><ellipse cx="30" cy="38" rx="17" ry="11" fill="{skin}"/>
  <path d="M-62 36 Q-62 -36 0 -36 Q62 -36 62 36Z" fill="{shell}"/>
  <path d="M-42 32 L-23 -14 L23 -14 L42 32 M-23 -14 L-9 -32 M23 -14 L9 -32 M0 -14 L0 32" stroke="#1f5a38" stroke-width="4" fill="none" stroke-linejoin="round"/>
  <path d="M-40 -8 Q-20 -34 10 -32" stroke="#ffffff55" stroke-width="5" fill="none" stroke-linecap="round"/>
</g>'''


def background():
    out = [
        f'<rect width="{W}" height="{H}" fill="{linear("bg", "#0b3f66", "#16a39a", "1", "1")}"/>',
        # blurred clinic interior for depth of field: window, shelves, plant
        '<g filter="url(#blur14)" opacity=".85">',
        '<rect x="80" y="40" width="250" height="260" rx="10" fill="#bfeee9" opacity=".55"/>',
        '<rect x="210" y="40" width="6" height="260" fill="#0b3f66" opacity=".4"/><rect x="80" y="165" width="250" height="6" fill="#0b3f66" opacity=".4"/>',
        '<rect x="880" y="60" width="250" height="14" rx="4" fill="#d8f7f2" opacity=".6"/><rect x="880" y="140" width="250" height="14" rx="4" fill="#d8f7f2" opacity=".6"/>',
        '<rect x="900" y="20" width="26" height="40" rx="5" fill="#8fe0c8" opacity=".7"/><rect x="960" y="100" width="30" height="40" rx="5" fill="#7fc8ff" opacity=".7"/>',
        '<rect x="1040" y="20" width="24" height="40" rx="5" fill="#bdf3e6" opacity=".7"/><rect x="930" y="180" width="30" height="50" rx="5" fill="#9ad8ff" opacity=".6"/>',
        '<ellipse cx="560" cy="170" rx="46" ry="62" fill="#3bb98a" opacity=".55"/><ellipse cx="610" cy="150" rx="40" ry="56" fill="#2fa07a" opacity=".5"/>',
        '</g>',
        # bokeh lights
        '<g filter="url(#blur6)" fill="#ffffff">'
        '<circle cx="140" cy="90" r="22" opacity=".22"/><circle cx="420" cy="60" r="16" opacity=".18"/>'
        '<circle cx="800" cy="70" r="26" opacity=".2"/><circle cx="1110" cy="230" r="20" opacity=".18"/>'
        '<circle cx="60" cy="300" r="18" opacity=".16"/><circle cx="700" cy="30" r="12" opacity=".2"/></g>',
        # light beam behind the vet
        f'<ellipse cx="600" cy="220" rx="300" ry="260" fill="{radial("beam", "#7ff0e0", ".5", ".4", ".7")}" opacity=".28"/>',
        # floor
        f'<rect y="{H-92}" width="{W}" height="92" fill="{linear("floor", "#0f6f78", "#082f45")}" opacity=".9"/>',
        f'<rect y="{H-92}" width="{W}" height="3" fill="#ffffff55"/>',
    ]
    return "".join(out)


def build() -> str:
    _defs.clear()
    body = [
        background(),
        person("a1", 300, 0.80, "#c68a5a", "#2b1d14", "bun", "#1FA89B", "#5a3a22"),
        person("a2", 900, 0.80, "#f1c9a3", "#6b3f1d", "long", "#1D6FA5", "#3b7a9e"),
        person("v", 600, 0.96, "#8d5a3b", "#16110e", "short", "#0E4C7A", "#3a2616"),
        rottweiler(150, 392, 0.98),
        cat(398, 440, 0.82, "#e6954a", "#b86a22", "#7fcf6b", "#fbe3c4", "c1"),
        turtle(548, 508, 0.72),
        snake(742, 480, 0.82),
        cat(900, 448, 0.8, "#f4f1ee", "#4a4a4f", "#f2c94c", "#ffffff", "c2"),
        husky(1052, 392, 0.98),
        # vignette for a cinematic finish
        f'<rect width="{W}" height="{H}" fill="url(#vig)"/>',
    ]
    _defs.append('<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/>'
                 '<stop offset="1" stop-color="#021625" stop-opacity=".45"/></radialGradient>')
    filters = ('<filter id="blur4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>'
               '<filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>'
               '<filter id="blur8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>'
               '<filter id="blur14" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" style="overflow:hidden" role="img" aria-label="A veterinarian in the centre with two '
            'veterinary assistants beside them, with a Rottweiler, a husky, two cats, a snake and a turtle in a bright clinic">'
            f'<defs>{filters}{"".join(_defs)}</defs>' + "\n".join(body) + "</svg>")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "clinic_team.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
