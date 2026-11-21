"""Generate assets/clinic_team.svg: a flat illustration of a vet team with pets (no external images needed).

Run: python tools/make_hero.py
"""
from pathlib import Path

W, H = 1200, 560


def person(cx, s, skin, hair, style, coat, scrub, badge="#1FA89B"):
    """A front-facing vet or assistant. Origin is bottom-centre; s is scale."""
    hair_back = ""
    hair_front = f'<path d="M-68 -415 Q-72 -505 0 -505 Q72 -505 68 -415 Q44 -462 0 -465 Q-44 -462 -68 -415Z" fill="{hair}"/>'
    if style == "long":
        hair_back = f'<path d="M-76 -420 Q-80 -510 0 -510 Q80 -510 76 -420 L84 -300 Q60 -290 56 -330 L-56 -330 Q-60 -290 -84 -300Z" fill="{hair}"/>'
    if style == "bun":
        hair_back = f'<circle cx="0" cy="-520" r="26" fill="{hair}"/>'
    if style == "short":
        hair_front = f'<path d="M-66 -420 Q-70 -495 0 -497 Q70 -495 66 -420 Q50 -455 0 -452 Q-50 -455 -66 -420Z" fill="{hair}"/>'
    return f'''
<g transform="translate({cx},{H}) scale({s})">
  {hair_back}
  <path d="M-165 0 L-165 -240 Q-165 -320 -90 -332 L90 -332 Q165 -320 165 -240 L165 0Z" fill="{coat}"/>
  <path d="M-62 -332 L0 -226 L62 -332Z" fill="{scrub}"/>
  <path d="M-62 -332 L-14 -196 L-96 -230Z" fill="#e8f3f5"/>
  <path d="M62 -332 L14 -196 L96 -230Z" fill="#e8f3f5"/>
  <rect x="-24" y="-356" width="48" height="36" rx="10" fill="{skin}"/>
  <path d="M-44 -334 Q-70 -250 -22 -222" stroke="#2b3a42" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M44 -334 Q70 -250 22 -222" stroke="#2b3a42" stroke-width="7" fill="none" stroke-linecap="round"/>
  <circle cx="0" cy="-208" r="16" fill="#c9d3d8" stroke="#2b3a42" stroke-width="5"/>
  <ellipse cx="0" cy="-415" rx="64" ry="74" fill="{skin}"/>
  <ellipse cx="-65" cy="-412" rx="10" ry="16" fill="{skin}"/><ellipse cx="65" cy="-412" rx="10" ry="16" fill="{skin}"/>
  {hair_front}
  <path d="M-38 -437 Q-26 -445 -14 -437" stroke="#2b2b2b" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M14 -437 Q26 -445 38 -437" stroke="#2b2b2b" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="-26" cy="-418" r="6" fill="#222"/><circle cx="26" cy="-418" r="6" fill="#222"/>
  <circle cx="-24" cy="-420" r="2" fill="#fff"/><circle cx="28" cy="-420" r="2" fill="#fff"/>
  <path d="M-4 -405 Q0 -392 6 -400" stroke="#00000030" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M-28 -380 Q0 -352 28 -380" stroke="#8a2f2f" stroke-width="5" fill="none" stroke-linecap="round"/>
  <circle cx="-42" cy="-392" r="9" fill="#ff8c8c" opacity=".35"/><circle cx="42" cy="-392" r="9" fill="#ff8c8c" opacity=".35"/>
  <rect x="62" y="-262" width="62" height="30" rx="5" fill="#fff"/><rect x="62" y="-262" width="62" height="9" rx="4" fill="{badge}"/>
  <rect x="70" y="-246" width="40" height="4" rx="2" fill="#9db4bb"/><rect x="70" y="-238" width="28" height="4" rx="2" fill="#9db4bb"/>
</g>'''


def rottweiler(x, y, s=1.0):
    return f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="0" cy="95" rx="92" ry="64" fill="#1c1c1e"/><path d="M-30 60 Q0 120 30 60 Q0 90 -30 60Z" fill="#b8692a"/>
  <path d="M-72 -40 Q-118 -10 -98 62 Q-64 44 -52 -6Z" fill="#141416"/><path d="M72 -40 Q118 -10 98 62 Q64 44 52 -6Z" fill="#141416"/>
  <ellipse cx="0" cy="0" rx="76" ry="68" fill="#1f1f22"/>
  <ellipse cx="-30" cy="-34" rx="12" ry="8" fill="#b8692a"/><ellipse cx="30" cy="-34" rx="12" ry="8" fill="#b8692a"/>
  <ellipse cx="0" cy="32" rx="44" ry="34" fill="#b8692a"/><ellipse cx="-36" cy="22" rx="14" ry="20" fill="#b8692a"/><ellipse cx="36" cy="22" rx="14" ry="20" fill="#b8692a"/>
  <circle cx="-28" cy="-14" r="8" fill="#2a1a0a"/><circle cx="28" cy="-14" r="8" fill="#2a1a0a"/>
  <circle cx="-26" cy="-17" r="3" fill="#fff"/><circle cx="30" cy="-17" r="3" fill="#fff"/>
  <ellipse cx="0" cy="14" rx="20" ry="13" fill="#0c0c0d"/><ellipse cx="-5" cy="10" rx="6" ry="3" fill="#ffffff55"/>
  <path d="M0 27 L0 42 M-18 48 Q0 62 18 48" stroke="#0c0c0d" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M-8 52 Q0 82 8 52Z" fill="#e8738a"/>
</g>'''


def husky(x, y, s=1.0):
    return f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="0" cy="95" rx="92" ry="64" fill="#8b98a5"/><ellipse cx="0" cy="104" rx="46" ry="50" fill="#f4f7f9"/>
  <path d="M-70 -30 L-58 -112 L-18 -52Z" fill="#6f7c88"/><path d="M70 -30 L58 -112 L18 -52Z" fill="#6f7c88"/>
  <path d="M-60 -48 L-54 -90 L-32 -56Z" fill="#f2b6c0"/><path d="M60 -48 L54 -90 L32 -56Z" fill="#f2b6c0"/>
  <ellipse cx="0" cy="2" rx="74" ry="66" fill="#8b98a5"/>
  <path d="M0 -62 Q-14 -34 -44 -26 Q-60 12 -34 52 Q0 74 34 52 Q60 12 44 -26 Q14 -34 0 -62Z" fill="#f7fafc"/>
  <path d="M0 -62 L0 -30" stroke="#8b98a5" stroke-width="10" stroke-linecap="round"/>
  <circle cx="-27" cy="-10" r="9" fill="#5fc4ee"/><circle cx="27" cy="-10" r="9" fill="#5fc4ee"/>
  <circle cx="-27" cy="-10" r="4.5" fill="#102a43"/><circle cx="27" cy="-10" r="4.5" fill="#102a43"/>
  <circle cx="-25" cy="-13" r="2.2" fill="#fff"/><circle cx="29" cy="-13" r="2.2" fill="#fff"/>
  <ellipse cx="0" cy="22" rx="17" ry="11" fill="#14161a"/>
  <path d="M0 33 L0 46 M-18 50 Q0 64 18 50" stroke="#14161a" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M-8 54 Q0 84 8 54Z" fill="#ef7f95"/>
</g>'''


def cat(x, y, s, fur, stripe, eye, belly):
    return f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="0" cy="80" rx="62" ry="52" fill="{fur}" stroke="#00000030" stroke-width="3"/><ellipse cx="0" cy="92" rx="30" ry="36" fill="{belly}"/>
  <path d="M-52 -30 L-48 -92 L-8 -50Z" fill="{fur}"/><path d="M52 -30 L48 -92 L8 -50Z" fill="{fur}"/>
  <path d="M-44 -46 L-42 -76 L-22 -54Z" fill="#f4b6c0"/><path d="M44 -46 L42 -76 L22 -54Z" fill="#f4b6c0"/>
  <ellipse cx="0" cy="0" rx="64" ry="54" fill="{fur}" stroke="#00000030" stroke-width="3"/>
  <path d="M-12 -52 L-8 -34 M0 -54 L0 -32 M12 -52 L8 -34" stroke="{stripe}" stroke-width="5" stroke-linecap="round"/>
  <path d="M-62 4 L-42 8 M-62 18 L-42 16 M62 4 L42 8 M62 18 L42 16" stroke="{stripe}" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="-22" cy="-6" rx="10" ry="12" fill="{eye}"/><ellipse cx="22" cy="-6" rx="10" ry="12" fill="{eye}"/>
  <ellipse cx="-22" cy="-6" rx="3.5" ry="10" fill="#10201a"/><ellipse cx="22" cy="-6" rx="3.5" ry="10" fill="#10201a"/>
  <circle cx="-19" cy="-11" r="2.5" fill="#fff"/><circle cx="25" cy="-11" r="2.5" fill="#fff"/>
  <path d="M-6 14 L6 14 L0 22Z" fill="#e8798f"/><path d="M0 22 Q-10 34 -18 28 M0 22 Q10 34 18 28" stroke="#6b4a3a" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <path d="M-62 -14 L-96 -22 M-62 -2 L-98 0 M62 -14 L96 -22 M62 -2 L98 0" stroke="#ffffffaa" stroke-width="2.5" stroke-linecap="round"/>
</g>'''


def snake(x, y, s=1.0):
    return f'''
<g transform="translate({x},{y}) scale({s})">
  <path d="M-70 20 Q-90 -20 -40 -22 Q10 -24 14 8 Q18 40 -30 44 Q-80 48 -52 18" stroke="#2f9e63" stroke-width="22" fill="none" stroke-linecap="round"/>
  <path d="M-70 20 Q-90 -20 -40 -22 Q10 -24 14 8 Q18 40 -30 44 Q-80 48 -52 18" stroke="#1b6b43" stroke-width="22" fill="none" stroke-linecap="round" stroke-dasharray="3 22"/>
  <path d="M14 8 Q52 -16 66 -58" stroke="#2f9e63" stroke-width="22" fill="none" stroke-linecap="round"/>
  <path d="M14 8 Q52 -16 66 -58" stroke="#1b6b43" stroke-width="22" fill="none" stroke-linecap="round" stroke-dasharray="3 22"/>
  <ellipse cx="72" cy="-72" rx="21" ry="16" fill="#35a96c"/><circle cx="76" cy="-76" r="5" fill="#fff"/><circle cx="77" cy="-76" r="2.6" fill="#111"/>
  <path d="M90 -70 L112 -66 M112 -66 L120 -72 M112 -66 L120 -60" stroke="#d2335b" stroke-width="3" stroke-linecap="round" fill="none"/>
</g>'''


def turtle(x, y, s=1.0):
    return f'''
<g transform="translate({x},{y}) scale({s})">
  <ellipse cx="62" cy="14" rx="20" ry="16" fill="#8fcf7e"/><circle cx="70" cy="9" r="3.5" fill="#222"/>
  <ellipse cx="-30" cy="36" rx="16" ry="10" fill="#8fcf7e"/><ellipse cx="30" cy="36" rx="16" ry="10" fill="#8fcf7e"/>
  <path d="M-60 34 Q-60 -34 0 -34 Q60 -34 60 34Z" fill="#3f8f5b"/>
  <path d="M-40 30 L-22 -14 L22 -14 L40 30 M-22 -14 L-8 -30 M22 -14 L8 -30 M0 -14 L0 30" stroke="#2a6b43" stroke-width="4" fill="none" stroke-linejoin="round"/>
</g>'''


def paws():
    out = []
    for (px, py, r) in [(70, 90, 1.0), (1130, 110, 1.0), (260, 70, 0.7), (960, 60, 0.7)]:
        out.append(f'<g transform="translate({px},{py}) scale({r})" fill="#ffffff" opacity=".18">'
                   '<ellipse cx="0" cy="8" rx="16" ry="13"/><ellipse cx="-17" cy="-9" rx="6" ry="8"/>'
                   '<ellipse cx="-6" cy="-17" rx="6" ry="8"/><ellipse cx="6" cy="-17" rx="6" ry="8"/><ellipse cx="17" cy="-9" rx="6" ry="8"/></g>')
    return "".join(out)


def build() -> str:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
        'aria-label="Illustration of a veterinarian in the centre with two veterinary assistants on either side, '
        'surrounded by a Rottweiler, a husky, two cats, a snake and a turtle">',
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0E4C7A"/>'
        '<stop offset=".55" stop-color="#14908F"/><stop offset="1" stop-color="#3BB98A"/></linearGradient>'
        '<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity=".05"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
        '<circle cx="180" cy="150" r="190" fill="#ffffff" opacity=".07"/><circle cx="1040" cy="120" r="230" fill="#ffffff" opacity=".07"/>',
        '<circle cx="600" cy="250" r="270" fill="#ffffff" opacity=".10"/>',
        '<g fill="#ffffff" opacity=".22"><rect x="580" y="52" width="40" height="12" rx="3"/><rect x="594" y="38" width="12" height="40" rx="3"/></g>',
        paws(),
        f'<rect y="{H-95}" width="{W}" height="95" fill="url(#floor)"/>',
        # assistants (behind, sides) then the vet (centre, front)
        person(300, 0.80, "#c68a5a", "#2b1d14", "bun", "#ffffff", "#1FA89B"),
        person(900, 0.80, "#f0c8a0", "#6b3f1d", "long", "#ffffff", "#1D6FA5"),
        person(600, 0.95, "#8d5a3b", "#16110e", "short", "#ffffff", "#0E4C7A"),
        # pets in the foreground
        rottweiler(150, 392, 0.98),
        cat(398, 440, 0.82, "#e6954a", "#b86a22", "#7fcf6b", "#fbe3c4"),
        turtle(548, 508, 0.72),
        snake(742, 480, 0.82),
        cat(900, 448, 0.8, "#f4f1ee", "#4a4a4f", "#f2c94c", "#ffffff"),
        husky(1052, 392, 0.98),
        '</svg>',
    ]
    return "\n".join(parts)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "assets" / "clinic_team.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
