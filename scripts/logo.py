"""Genera los logos de CLASE 17 como SVG con el texto convertido a trazados
(no dependen de ninguna fuente instalada).

Uso: python3 scripts/logo.py <LeagueSpartan[wght].ttf> <carpeta_salida>
"""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

# Paleta (la misma que la web)
BOSQUE = "#1c3d1f"   # verde muy oscuro: contornos
PINO = "#2f5d31"     # verde oscuro: cinta
SALVIA = "#6b9a67"   # verde medio: relleno
MENTA = "#bedab4"    # verde claro: detalles
CREMA = "#f3efd8"    # crema: letras

_fuentes = {}


def fuente(ttf, peso):
    if peso not in _fuentes:
        f = TTFont(ttf)
        _fuentes[peso] = instancer.instantiateVariableFont(f, {"wght": peso})
    return _fuentes[peso]


def texto(ttf, cadena, tam, peso=800, espacio=0.0):
    """Devuelve (d, ancho, alto_mayus) del texto a tamaño `tam`, con origen en la línea base."""
    f = fuente(ttf, peso)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    esc = tam / upm
    cap = f["OS/2"].sCapHeight * esc
    pen = SVGPathPen(gs)
    x = 0.0
    for i, ch in enumerate(cadena):
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (esc, 0, 0, -esc, x, 0))
        gs[g].draw(tp)
        x += gs[g].width * esc
        if i < len(cadena) - 1:
            x += espacio * tam
    return pen.getCommands(), x, cap


def centrado(ttf, cadena, tam, cx, base, peso=800, espacio=0.0, **attrs):
    d, w, _ = texto(ttf, cadena, tam, peso, espacio)
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path transform="translate({cx - w / 2:.2f} {base:.2f})" d="{d}" {extra}/>'


ESCUDO = "M70 40 H530 Q570 40 570 80 V350 Q570 520 300 650 Q30 520 30 350 V80 Q30 40 70 40 Z"


def escudo(ttf, con_cinta=True):
    partes = []
    partes.append(f'<clipPath id="corte"><path d="{ESCUDO}"/></clipPath>')
    # contorno grueso exterior + anillo crema + relleno salvia
    partes.append(f'<path d="{ESCUDO}" fill="{BOSQUE}" stroke="{BOSQUE}" stroke-width="56" stroke-linejoin="round"/>')
    partes.append(f'<path d="{ESCUDO}" fill="{SALVIA}" stroke="{CREMA}" stroke-width="18" stroke-linejoin="round"/>')
    # banda superior con CLASE
    partes.append(f'<g clip-path="url(#corte)"><rect x="0" y="0" width="600" height="150" fill="{BOSQUE}"/>'
                  f'<rect x="0" y="150" width="600" height="12" fill="{MENTA}"/></g>')
    partes.append(centrado(ttf, "CLASE", 78, 300, 128, peso=900, espacio=0.12, fill=CREMA))
    # rayas diagonales de fondo, discretas
    rayas = "".join(f'<rect x="{x}" y="160" width="14" height="520" fill="{MENTA}" opacity=".18" transform="skewX(-20)"/>'
                    for x in range(140, 760, 46))
    partes.append(f'<g clip-path="url(#corte)">{rayas}</g>')
    # 17 grande, inclinado, con sombra y contorno grueso
    d, w, cap = texto(ttf, "17", 330, peso=900, espacio=-0.02)
    x0 = 300 - w / 2 + 14
    base = 175 + cap + 18
    t = f"translate({x0:.2f} {base:.2f}) skewX(-9)"
    partes.append(f'<path transform="translate(12 12) {t}" d="{d}" fill="{BOSQUE}" stroke="{BOSQUE}" stroke-width="20" stroke-linejoin="round"/>')
    partes.append(f'<path transform="{t}" d="{d}" fill="{CREMA}" stroke="{BOSQUE}" stroke-width="16" stroke-linejoin="round" paint-order="stroke"/>')
    if con_cinta:
        cinta = "M-6 520 H606 L582 552 L606 584 H-6 L18 552 Z"
        partes.append(f'<path d="{cinta}" fill="{PINO}" stroke="{BOSQUE}" stroke-width="12" stroke-linejoin="round"/>')
        partes.append(centrado(ttf, "LA CLASE DE LOS CHICOS", 31, 300, 564, peso=800, espacio=0.06, fill=CREMA))
    return "\n".join(partes)


def svg(cuerpo, vb):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="Clase 17">\n'
            f'<title>CLASE 17 · LA CLASE DE LOS CHICOS</title>\n{cuerpo}\n</svg>\n')


def horizontal(ttf, color_texto=CREMA, color_sub=MENTA):
    """Escudo pequeño + CLASE 17 + LA CLASE DE LOS CHICOS, para el menú."""
    partes = [f'<g transform="translate(0 4) scale(.2)">{escudo(ttf, con_cinta=False)}</g>']
    d, w, _ = texto(ttf, "CLASE 17", 64, peso=900, espacio=0.04)
    partes.append(f'<path transform="translate(150 72)" d="{d}" fill="{color_texto}"/>')
    d2, w2, _ = texto(ttf, "LA CLASE DE LOS CHICOS", 22.5, peso=700, espacio=0.12)
    partes.append(f'<path transform="translate(152 112)" d="{d2}" fill="{color_sub}"/>')
    ancho = 150 + max(w, w2) + 8
    return "\n".join(partes), ancho


def roseta(ttf):
    """Marca secundaria: 17 en círculo, para icono de pestaña y redes."""
    p = [f'<circle cx="150" cy="150" r="138" fill="{BOSQUE}"/>',
         f'<circle cx="150" cy="150" r="112" fill="{SALVIA}" stroke="{CREMA}" stroke-width="12"/>']
    d, w, cap = texto(ttf, "17", 160, peso=900, espacio=-0.02)
    t = f"translate({150 - w / 2 + 6:.2f} {150 + cap / 2:.2f}) skewX(-9)"
    p.append(f'<path transform="translate(6 6) {t}" d="{d}" fill="{BOSQUE}" stroke="{BOSQUE}" stroke-width="10" stroke-linejoin="round"/>')
    p.append(f'<path transform="{t}" d="{d}" fill="{CREMA}" stroke="{BOSQUE}" stroke-width="9" stroke-linejoin="round" paint-order="stroke"/>')
    return "\n".join(p)


def main(ttf, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "logo-clase17.svg").write_text(svg(escudo(ttf), "-20 -20 640 710"), encoding="utf-8")
    cuerpo, ancho = horizontal(ttf)
    (salida / "logo-horizontal.svg").write_text(svg(cuerpo, f"0 0 {ancho:.0f} 140"), encoding="utf-8")
    cuerpo2, ancho2 = horizontal(ttf, color_texto=BOSQUE, color_sub=PINO)
    (salida / "logo-horizontal-claro.svg").write_text(svg(cuerpo2, f"0 0 {ancho2:.0f} 140"), encoding="utf-8")
    (salida / "icono-17.svg").write_text(svg(roseta(ttf), "0 0 300 300"), encoding="utf-8")
    print("Logos creados en", salida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
