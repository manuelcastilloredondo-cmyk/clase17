"""Logo de Clase 17 dentro de la marca Manu en clase: la «m» coral sobre celeste + «MANU EN CLASE» + «CLASE 17».

Uso: python3 scripts/logo_manu.py <icon-512.png de manu-en-clase>
Genera en recursos/logo/: logo-horizontal.svg (menú), logo-horizontal-claro.svg/.png (fichas),
icono-17.svg (favicon), m.png, app-192.png, app-512.png, app-512-maskable.png, apple-touch-icon.png.
"""
import base64
import io
import subprocess
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
LOGO = RAIZ / "recursos/logo"
FU = RAIZ / "recursos/fuentes"
TINTA, CORAL, AZUL_HONDO, CELESTE = "#1e4f5c", "#fa6876", "#2a6f87", "#a1d6e2"


def texto(ttf, cadena, tam, espacio=0.0):
    f = TTFont(ttf)
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    esc = tam / upm
    pen = SVGPathPen(gs)
    x = 0.0
    for i, ch in enumerate(cadena):
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (esc, 0, 0, -esc, x, 0)))
        x += gs[g].width * esc + (espacio * tam if i < len(cadena) - 1 else 0)
    return pen.getCommands(), x


def png_b64(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return base64.b64encode(b.getvalue()).decode()


def main(icono_manu):
    LOGO.mkdir(parents=True, exist_ok=True)
    ico = Image.open(icono_manu).convert("RGB").resize((512, 512), Image.LANCZOS)
    # iconos de app
    ico.save(LOGO / "app-512.png")
    ico.save(LOGO / "app-512-maskable.png")
    ico.resize((192, 192), Image.LANCZOS).save(LOGO / "app-192.png")
    ico.resize((180, 180), Image.LANCZOS).save(LOGO / "apple-touch-icon.png")
    # «m» transparente
    rgba = ico.convert("RGBA")
    px = rgba.load()
    for y in range(512):
        for x in range(512):
            r, g, b, _ = px[x, y]
            # distancia al celeste de fondo → alfa
            d = abs(r - 161) + abs(g - 214) + abs(b - 226)
            px[x, y] = (250, 104, 118, max(0, min(255, int((d - 40) * 2.2))))
    rgba.save(LOGO / "m.png")
    # símbolo redondeado (celeste + m) incrustado
    sim = ico.resize((192, 192), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (192, 192), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 191, 191), 42, fill=255)
    sim.putalpha(mask)
    b64 = png_b64(sim)

    d1, w1 = texto(FU / "BarlowCondensed-ExtraBoldItalic.ttf", "MANU EN ", 66, 0.01)
    d2, w2 = texto(FU / "BarlowCondensed-ExtraBoldItalic.ttf", "CLASE", 66, 0.01)
    d3, w3 = texto(FU / "BarlowCondensed-SemiBold.ttf", "CLASE 17 · LA CLASE DE LOS CHICOS", 21, 0.16)
    x0 = 120
    ancho = int(x0 + max(w1 + w2, w3) + 10)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {ancho} 112" role="img" aria-label="Manu en clase · Clase 17">'
           f'<title>Manu en clase · Clase 17</title>'
           f'<image x="0" y="4" width="104" height="104" href="data:image/png;base64,{b64}" xlink:href="data:image/png;base64,{b64}"/>'
           f'<path transform="translate({x0} 62)" d="{d1}" fill="{TINTA}"/>'
           f'<path transform="translate({x0 + w1:.1f} 62)" d="{d2}" fill="{CORAL}"/>'
           f'<path transform="translate({x0 + 2} 96)" d="{d3}" fill="{AZUL_HONDO}"/></svg>')
    for nombre in ("logo-horizontal.svg", "logo-horizontal-claro.svg"):
        (LOGO / nombre).write_text(svg, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-h", "300", str(LOGO / "logo-horizontal-claro.svg"), "-o", str(LOGO / "logo-horizontal-claro.png")], check=True)
    fav = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 192 192">'
           f'<image width="192" height="192" href="data:image/png;base64,{b64}" xlink:href="data:image/png;base64,{b64}"/></svg>')
    (LOGO / "icono-17.svg").write_text(fav, encoding="utf-8")
    print("Logo Manu en clase · Clase 17 creado; ancho", ancho)


if __name__ == "__main__":
    main(sys.argv[1])
