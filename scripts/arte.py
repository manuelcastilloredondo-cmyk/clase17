"""Arte derivado de los pictos: dibujo de puntitos (dot markers) y siluetas (sombras)."""
import math
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
SOMBRAS = RAIZ / "recursos/sombras"

# Colores de rotulador de puntos / gomets
PALETA = {
    "ROJO": (229, 57, 53), "AZUL": (30, 136, 229), "AMARILLO": (253, 216, 53), "VERDE": (67, 160, 71),
    "NARANJA": (251, 140, 0), "MORADO": (142, 36, 170), "MARRÓN": (109, 76, 65), "ROSA": (236, 64, 122),
}
HEX = {k: "#%02x%02x%02x" % v for k, v in PALETA.items()}


def _cercano(rgb, opciones):
    return min(opciones, key=lambda k: sum((a - b) ** 2 for a, b in zip(rgb, PALETA[k])))


def puntitos(ruta_png, max_puntos=26, max_colores=4):
    """Devuelve {"puntos":[{"x","y","c"}], "r", "colores":[...]} en coordenadas 0..1 (y hacia abajo)."""
    im = Image.open(ruta_png).convert("RGBA").resize((400, 400), Image.LANCZOS)
    a = np.asarray(im).astype(int)
    mask = a[:, :, 3] > 128
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    elegido = None
    for s in range(18, 120, 2):
        r = s * 0.40
        pts = []
        fila = 0
        y = y0 + r
        while y <= y1 - r * 0.3:
            off = (s / 2) if fila % 2 else 0
            x = x0 + r + off
            while x <= x1 - r * 0.3:
                yy, xx = np.ogrid[-int(r):int(r) + 1, -int(r):int(r) + 1]
                disco = (xx ** 2 + yy ** 2) <= r * r
                cy, cx = int(y), int(x)
                sub = mask[max(cy - int(r), 0):cy + int(r) + 1, max(cx - int(r), 0):cx + int(r) + 1]
                if sub.shape == disco.shape and (sub & disco).sum() / disco.sum() > 0.62:
                    pts.append((x, y))
                x += s
            y += s * 0.866
            fila += 1
        if len(pts) <= max_puntos:
            elegido = (s, r, pts)
            break
    if not elegido or len(elegido[2]) < 4:
        return None
    s, r, pts = elegido
    rgb = a[:, :, :3]
    lum = rgb.mean(axis=2)
    crudos = []
    for x, y in pts:
        yy, xx = np.ogrid[:400, :400]
        d = (xx - x) ** 2 + (yy - y) ** 2 <= (r * 0.9) ** 2
        sel = d & mask & (lum > 70)                     # sin las líneas negras
        color = (sel & (lum < 225)).sum() > sel.sum() * 0.3  # zona con color (no blanca)
        if color:
            px = rgb[sel & (lum < 225)]
            crudos.append(tuple(int(v) for v in px.mean(axis=0)))
        else:
            crudos.append(None)
    nombres = [_cercano(c, PALETA) if c else None for c in crudos]
    usados = [n for n in nombres if n]
    top = [k for k, _ in sorted(((k, usados.count(k)) for k in set(usados)), key=lambda t: -t[1])][:max_colores] or ["AZUL"]
    # zonas blancas: un color que no se haya usado, para que se note la forma
    blanco = next((k for k in ["AMARILLO", "AZUL", "ROSA", "NARANJA", "VERDE"] if k not in top), "AMARILLO")
    final = []
    for (x, y), n, c in zip(pts, nombres, crudos):
        if n is None:
            k = blanco
        else:
            k = n if n in top else _cercano(c, top)
        final.append({"x": round(x / 400, 4), "y": round(y / 400, 4), "c": k})
    colores = sorted({p["c"] for p in final}, key=list(PALETA).index)
    return {"puntos": final, "r": round(r / 400, 4), "colores": [{"nombre": k, "hex": HEX[k]} for k in colores]}


def sombra(pid, ruta_png):
    """Silueta gris oscura del picto (para fichas de sombras)."""
    SOMBRAS.mkdir(parents=True, exist_ok=True)
    destino = SOMBRAS / f"{pid}.png"
    if not destino.exists():
        im = Image.open(ruta_png).convert("RGBA")
        alfa = im.split()[3].point(lambda v: 255 if v > 100 else 0)
        sil = Image.new("RGBA", im.size, (60, 66, 62, 0))
        sil.putalpha(alfa)
        sil.save(destino)
    return destino
