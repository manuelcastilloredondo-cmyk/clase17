"""Fichas A4 del día (identidad CLASE 17). Cinco tipos:
colorear · lineas · recortar · secuencia · puntos
Se llama desde construir.py; no hace falta usarlo a mano.
"""
import math
import random
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

RAIZ = Path(__file__).resolve().parent.parent
pdfmetrics.registerFont(TTFont("Titulo", str(RAIZ / "recursos/fuentes/LeagueSpartan-ExtraBold.ttf")))
pdfmetrics.registerFont(TTFont("Texto", str(RAIZ / "recursos/fuentes/Quicksand-SemiBold.ttf")))

ANCHO, ALTO = A4
M = 36
BOSQUE, PINO, SALVIA, MENTA, CREMA = (HexColor(c) for c in ("#1c3d1f", "#2f5d31", "#6b9a67", "#bedab4", "#f3efd8"))
GRIS = HexColor("#9aa59a")
AUTORIA = "FICHA ELABORADA POR MANUEL CASTILLO REDONDO · MANU EN CLASE · CLASE 17"
CREDITO = "PICTOGRAMAS: SERGIO PALAO. ORIGEN: ARASAAC (ARASAAC.ORG). LICENCIA CC BY-NC-SA. PROPIEDAD: GOBIERNO DE ARAGÓN."
LOGO = RAIZ / "recursos/logo/logo-horizontal-claro.png"

NOMBRES = {
    "colorear": ("COLOREA", "COLOREA LOS DIBUJOS Y LEE SU NOMBRE."),
    "lineas": ("SIGUE LA LÍNEA", "REPASA EL CAMINO DESDE EL DIBUJO HASTA SU NOMBRE."),
    "recortar": ("RECORTA Y PEGA", "RECORTA LOS DIBUJOS Y PÉGALOS JUNTO A SU NOMBRE."),
    "secuencia": ("ORDENA LOS PASOS", "RECORTA LOS PASOS Y PÉGALOS EN ORDEN."),
    "puntos": ("UNE LOS PUNTOS", "UNE LOS PUNTOS DEL 1 AL ÚLTIMO, COLOREA Y REPASA LA PALABRA."),
}

# Figuras para unir puntos (coordenadas 0..1, sentido horario, y = arriba)
def _estrella():
    p = []
    for i in range(10):
        r = 0.5 if i % 2 == 0 else 0.21
        a = math.pi / 2 - i * math.pi / 5
        p.append((0.5 + r * math.cos(a), 0.47 + r * math.sin(a)))
    return p

FIGURAS = {
    "estrella": ("ESTRELLA", _estrella()),
    "camiseta": ("CAMISETA", [(0.36, 0.95), (0.5, 0.86), (0.64, 0.95), (0.95, 0.80), (0.86, 0.60), (0.74, 0.66),
                              (0.74, 0.08), (0.26, 0.08), (0.26, 0.66), (0.14, 0.60), (0.05, 0.80)]),
    "diente": ("DIENTE", [(0.18, 0.80), (0.30, 0.94), (0.42, 0.90), (0.50, 0.84), (0.58, 0.90), (0.70, 0.94), (0.82, 0.80),
                          (0.80, 0.55), (0.72, 0.30), (0.66, 0.06), (0.58, 0.20), (0.50, 0.38), (0.42, 0.20),
                          (0.34, 0.06), (0.28, 0.30), (0.20, 0.55)]),
    "jabon": ("JABÓN", [(0.18, 0.70), (0.26, 0.78), (0.50, 0.80), (0.74, 0.78), (0.82, 0.70), (0.84, 0.50),
                        (0.82, 0.30), (0.74, 0.22), (0.50, 0.20), (0.26, 0.22), (0.18, 0.30), (0.16, 0.50)]),
}


def cabecera(c, titulo_ficha, consigna, tema, fecha_txt):
    c.setFillColor(CREMA)
    c.rect(0, ALTO - 118, ANCHO, 118, stroke=0, fill=1)
    c.setFillColor(SALVIA)
    c.rect(0, ALTO - 124, ANCHO, 6, stroke=0, fill=1)
    c.drawImage(str(LOGO), M, ALTO - 66, height=40, width=40 * 1300 / 300, preserveAspectRatio=True, anchor="w", mask="auto")
    c.setFillColor(BOSQUE)
    c.setFont("Texto", 10)
    c.drawRightString(ANCHO - M, ALTO - 38, f"{fecha_txt} · {tema}")
    c.drawRightString(ANCHO - M, ALTO - 58, "NOMBRE: ______________________________")
    c.setFont("Titulo", 26)
    c.drawString(M, ALTO - 98, titulo_ficha)
    c.setFillColor(PINO)
    c.setFont("Texto", 11.5)
    c.drawString(M, ALTO - 150, consigna)
    c.setFillColor(BOSQUE)


def pie(c):
    c.setFont("Texto", 6.5)
    c.setFillColor(GRIS)
    c.drawCentredString(ANCHO / 2, 27, AUTORIA)
    c.drawCentredString(ANCHO / 2, 17, CREDITO)
    c.setFillColor(BOSQUE)


def caja(c, x, y, w, h, grosor=2.5, radio=10, discontinua=False, color=BOSQUE):
    c.setStrokeColor(color)
    c.setLineWidth(grosor)
    if discontinua:
        c.setDash(6, 4)
    c.roundRect(x, y, w, h, radio, stroke=1, fill=0)
    c.setDash()
    c.setStrokeColor(BOSQUE)


def picto(c, ruta, x, y, lado):
    c.drawImage(str(ruta), x, y, lado, lado, preserveAspectRatio=True, anchor="c", mask="auto")


def texto_ajustado(c, s, x, y, ancho_max, tam=18, fuente="Titulo", centrado=True):
    while tam > 8 and c.stringWidth(s, fuente, tam) > ancho_max:
        tam -= 0.5
    c.setFont(fuente, tam)
    (c.drawCentredString if centrado else c.drawString)(x, y, s)


# ── tipos ──
def colorear(c, el, **_):
    items = el[:4]
    w = (ANCHO - 2 * M - 20) / 2
    h = (ALTO - 190 - 50 - 20) / 2
    for i, e in enumerate(items):
        x = M + (i % 2) * (w + 20)
        y = ALTO - 175 - (i // 2 + 1) * (h + 10)
        caja(c, x, y, w, h)
        lado = min(w, h) - 70
        picto(c, e["bn"], x + (w - lado) / 2, y + 48, lado)
        texto_ajustado(c, e["palabra"], x + w / 2, y + 18, w - 20, 20)


def lineas(c, el, semilla=1, **_):
    items = el[:4]
    alto_fila = (ALTO - 190 - 50) / 4
    for i, e in enumerate(items):
        yc = ALTO - 180 - (i + 0.5) * alto_fila
        lado = alto_fila - 36
        caja(c, M, yc - lado / 2 - 6, lado + 12, lado + 12)
        picto(c, e["color"], M + 6, yc - lado / 2, lado)
        wx = ANCHO - M - 170
        caja(c, wx, yc - 26, 170, 52)
        texto_ajustado(c, e["palabra"], wx + 85, yc - 7, 150, 18)
        x0, x1 = M + lado + 30, wx - 14
        c.setStrokeColor(SALVIA)
        c.setLineWidth(3)
        c.setDash(2, 6)
        c.setLineCap(1)
        p = c.beginPath()
        p.moveTo(x0, yc)
        estilo = (i + semilla) % 4
        pasos = 120
        for k in range(1, pasos + 1):
            t = k / pasos
            x = x0 + (x1 - x0) * t
            if estilo == 0:
                y = yc + 26 * math.sin(t * math.pi * 4)
            elif estilo == 1:
                y = yc + 26 * (1 - 2 * abs((t * 5) % 2 - 1))
            elif estilo == 2:
                y = yc + (24 if int(t * 6) % 2 else -24)
            else:
                y = yc + 30 * math.sin(t * math.pi * 2) * (1 - t * 0.3)
            p.lineTo(x, y)
        c.drawPath(p, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(BOSQUE)
        c.circle(x0, yc, 5, stroke=0, fill=1)
        c.circle(x1, yc, 5, stroke=0, fill=1)
        c.setStrokeColor(BOSQUE)


def recortar(c, el, semilla=1, **_):
    items = el[:6]
    # parte de arriba: nombre + hueco
    w = (ANCHO - 2 * M - 16) / 2
    h = 118
    for i, e in enumerate(items):
        x = M + (i % 2) * (w + 16)
        y = ALTO - 175 - (i // 2 + 1) * (h + 8)
        caja(c, x, y, w, h)
        caja(c, x + w - 104, y + 9, 96, 100, grosor=1.5, discontinua=True, color=SALVIA)
        texto_ajustado(c, e["palabra"], x + (w - 104) / 2, y + h / 2 - 7, w - 124, 17)
    # tira para recortar
    yt = 60
    c.setFont("Texto", 10)
    c.setFillColor(PINO)
    c.drawString(M, yt + 128, "✂  RECORTA POR LA LÍNEA DE PUNTOS")
    c.setFillColor(BOSQUE)
    orden = items[:]
    random.Random(semilla).shuffle(orden)
    cw = (ANCHO - 2 * M) / 6
    for i, e in enumerate(orden):
        x = M + i * cw
        c.setDash(4, 3)
        c.setLineWidth(1)
        c.rect(x, yt, cw, 116, stroke=1, fill=0)
        c.setDash()
        picto(c, e["color"], x + 8, yt + 12, cw - 16)


def secuencia(c, pasos, semilla=1, **_):
    n = len(pasos)
    w = (ANCHO - 2 * M - (n - 1) * 10) / n
    y = ALTO - 175 - w - 40
    for i in range(n):
        x = M + i * (w + 10)
        caja(c, x, y, w, w + 30)
        c.setFillColor(SALVIA)
        c.setFont("Titulo", 22)
        c.drawString(x + 8, y + w + 6, str(i + 1))
        c.setFillColor(BOSQUE)
    c.setFont("Texto", 10)
    c.setFillColor(PINO)
    c.drawString(M, 270, "✂  RECORTA POR LA LÍNEA DE PUNTOS")
    c.setFillColor(BOSQUE)
    orden = pasos[:]
    azar = random.Random(semilla)
    while n > 1 and any(a is b for a, b in zip(orden, pasos)):
        azar.shuffle(orden)
    for i, p in enumerate(orden):
        x = M + i * (w + 10)
        yy = 60
        c.setDash(4, 3)
        c.setLineWidth(1)
        c.rect(x, yy, w, w + 30, stroke=1, fill=0)
        c.setDash()
        picto(c, p["color"], x + 6, yy + 30, w - 12)
        texto_ajustado(c, p["palabra"], x + w / 2, yy + 10, w - 10, 11)


def puntos(c, el=None, figura="estrella", **_):
    nombre, pts = FIGURAS[figura]
    area = 400
    ox, oy = (ANCHO - area) / 2, 200
    c.setFont("Texto", 13)
    for i, (px, py) in enumerate(pts):
        x, y = ox + px * area, oy + py * area * 0.92
        c.setFillColor(BOSQUE)
        c.circle(x, y, 5.5, stroke=0, fill=1)
        dx = 12 if px >= 0.5 else -12
        c.setFillColor(PINO)
        (c.drawString if dx > 0 else c.drawRightString)(x + dx, y + 6, str(i + 1))
    c.setFillColor(SALVIA)
    c.setFont("Texto", 9)
    x0, y0 = ox + pts[0][0] * area, oy + pts[0][1] * area * 0.92
    (c.drawString if pts[0][0] >= 0.5 else c.drawRightString)(x0 + (14 if pts[0][0] >= 0.5 else -14), y0 - 12, "EMPIEZA AQUÍ")
    # repasa la palabra
    c.setFillColor(BOSQUE)
    t = c.beginText()
    t.setTextRenderMode(1)
    t.setFont("Titulo", 64)
    c.setStrokeColor(GRIS)
    c.setLineWidth(1.2)
    c.setDash(3, 3)
    ancho = c.stringWidth(nombre, "Titulo", 64)
    t.setTextOrigin((ANCHO - ancho) / 2, 120)
    t.textOut(nombre)
    t.setTextRenderMode(0)
    c.drawText(t)
    c.setDash()
    c.setStrokeColor(BOSQUE)
    c.setLineWidth(1)
    c.line(M, 108, ANCHO - M, 108)


TIPOS = {"colorear": colorear, "lineas": lineas, "recortar": recortar, "secuencia": secuencia, "puntos": puntos}


def generar(salida, tipo, tema, fecha_txt, elementos, pasos=None, figura="estrella", semilla=1):
    titulo, consigna = NOMBRES[tipo]
    c = canvas.Canvas(str(salida), pagesize=A4)
    c.setTitle(f"{titulo} · {tema} · Clase 17")
    c.setAuthor("Manuel Castillo Redondo")
    c.setCreator("Manu en clase · Manuel Castillo Redondo")
    cabecera(c, titulo, consigna, tema, fecha_txt)
    TIPOS[tipo](c, elementos if tipo != "secuencia" else None, pasos=pasos, figura=figura, semilla=semilla) if tipo != "secuencia" \
        else secuencia(c, pasos, semilla=semilla)
    pie(c)
    c.showPage()
    c.save()
