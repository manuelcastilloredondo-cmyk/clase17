"""Programación de aula en PDF (formato formal, para archivo e inspección).

Uso: python3 scripts/programacion_pdf.py programacion/2026-11.json salida.pdf

Toma el mismo JSON que genera la web, así el documento y la web dicen lo mismo.
No incluye datos personales del alumnado: el registro usa códigos A1…A5.
"""
import json
import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

RAIZ = Path(__file__).resolve().parent.parent
FU = RAIZ / "recursos/fuentes"
pdfmetrics.registerFont(TTFont("Serif", str(FU / "SourceSerif4-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Serif-SB", str(FU / "SourceSerif4-Semibold.ttf")))
pdfmetrics.registerFont(TTFont("Serif-I", str(FU / "SourceSerif4-Italic.ttf")))
pdfmetrics.registerFont(TTFont("Serif-D", str(FU / "SourceSerif4-BoldDisplay.ttf")))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-SB", italic="Serif-I", boldItalic="Serif-SB")

TINTA = colors.HexColor("#1a1a1a")
GRIS = colors.HexColor("#5c5c5c")
FILETE = colors.HexColor("#9a9a9a")
FONDO = colors.HexColor("#eeeeea")
VERDE = colors.HexColor("#1e4f5c")  # tinta de la marca Manu en clase

CENTRO = "CEE Nuestra Señora de los Volcanes · Teguise (Lanzarote)"
GRUPO = "Clase 17 · Tránsito a la Vida Adulta"
AUTOR = "Manuel Castillo Redondo"
MARCA = "Manu en clase"
CURSO = "Curso 2026-2027"

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

JUEGO = {
    "toca": ("Toca y escucha", "Discriminación auditiva y comprensión de vocabulario: la consigna oral pide un pictograma y el alumno lo selecciona entre 2, 4 o 6 opciones (8 ensayos).", "AS"),
    "une": ("Une cada dibujo", "Asociación pictograma–palabra escrita (lectura global): emparejar cada dibujo con su nombre en grupos de 4.", "AS"),
    "memoria": ("Memoria", "Atención sostenida y memoria visual de trabajo: localizar parejas de pictogramas (4 o 6 parejas).", "AL"),
    "ordena": ("Ordena los pasos", "Secuenciación de una rutina funcional mediante análisis de tareas; la aplicación solo admite el paso correcto (aprendizaje sin error).", "AP"),
    "clasifica": ("Clasifica", "Categorización: asignar cada pictograma a una de dos categorías según un criterio dado.", "AP"),
}
FICHA = {
    "colorear": ("Colorea", "Coloreado de 4 pictogramas en blanco y negro con su nombre (motricidad fina, control del trazo).", "AL"),
    "lineas": ("Sigue la línea", "Grafomotricidad: repaso de trazos (ondas, zigzag, escalones) desde el pictograma hasta su nombre.", "AL"),
    "recortar": ("Recorta y pega", "Recortado y pegado de 6 pictogramas junto a su nombre (coordinación bimanual, lectura global).", "AL"),
    "secuencia": ("Ordena los pasos", "Recortado de los pasos de la rutina y pegado en orden numerado (secuenciación temporal).", "AP"),
    "puntos": ("Une los puntos", "Unión de puntos numerados, coloreado de la figura y repaso de la palabra (conteo, trazo, lectura).", "AL"),
}
EXTRA = {"igual": "Busca el igual", "sombras": "Cada uno con su sombra", "diferente": "Busca el diferente",
         "cuenta": "Cuenta (1–3)", "tamano": "Grande y pequeño"}
AMBITO = {"AP": "Autonomía Personal", "AS": "Autonomía Social", "AL": "Autonomía Laboral"}

# ── estilos ──
def E(nombre, **kw):
    base = dict(fontName="Serif", fontSize=10, leading=14, textColor=TINTA, alignment=TA_JUSTIFY, allowWidows=0, allowOrphans=0)
    base.update(kw)
    return ParagraphStyle(nombre, **base)

S = {
    "titulo": E("titulo", fontName="Serif-D", fontSize=22, leading=27, alignment=TA_LEFT, textColor=VERDE),
    "subtitulo": E("subtitulo", fontName="Serif-I", fontSize=12, leading=16, alignment=TA_LEFT, textColor=GRIS),
    "h1": E("h1", fontName="Serif-SB", fontSize=12.5, leading=16, spaceBefore=14, spaceAfter=6, alignment=TA_LEFT, textColor=VERDE),
    "h2": E("h2", fontName="Serif-SB", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3, alignment=TA_LEFT),
    "p": E("p", spaceAfter=5),
    "li": E("li", leftIndent=14, bulletIndent=3, spaceAfter=2),
    "nota": E("nota", fontName="Serif-I", fontSize=8.5, leading=11.5, textColor=GRIS, alignment=TA_LEFT),
    "celda": E("celda", fontSize=8.6, leading=11, alignment=TA_LEFT),
    "celda_c": E("celda_c", fontSize=8.6, leading=11, alignment=TA_CENTER),
    "cab": E("cab", fontName="Serif-SB", fontSize=8.6, leading=11, alignment=TA_LEFT),
    "cab_c": E("cab_c", fontName="Serif-SB", fontSize=8.6, leading=11, alignment=TA_CENTER),
    "dato_k": E("dato_k", fontName="Serif-SB", fontSize=9.5, leading=13, alignment=TA_LEFT),
    "dato_v": E("dato_v", fontSize=9.5, leading=13, alignment=TA_LEFT),
}


def P(t, s="p"):
    return Paragraph(t, S[s])


def lista(items):
    return [Paragraph(i, S["li"], bulletText="–") for i in items]


def tabla(filas, anchos, cabecera=True, centrar=()):
    datos = []
    for r, fila in enumerate(filas):
        datos.append([c if not isinstance(c, str) else
                      P(c, ("cab_c" if k in centrar else "cab") if (cabecera and r == 0) else ("celda_c" if k in centrar else "celda"))
                      for k, c in enumerate(fila)])
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0)
    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, TINTA),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, TINTA),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, FILETE),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    if cabecera:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), FONDO), ("LINEBELOW", (0, 0), (-1, 0), 0.6, TINTA)]
    t.setStyle(TableStyle(estilo))
    return t


def fecha_larga(f):
    d = date.fromisoformat(f)
    return f"{DIAS[d.weekday()]} {d.day}"


def construir(prog_path, salida):
    prog = json.loads((RAIZ / prog_path).read_text(encoding="utf-8"))
    a, m = map(int, prog["mes"].split("-"))
    mes_txt = f"{MESES[m - 1]} de {a}"
    sem = prog["semanas"]
    primero = date.fromisoformat(sem[0]["dias"][0])
    ultimo = date.fromisoformat(sem[-1]["dias"][-1])
    n_dias = sum(len(s["dias"]) for s in sem)
    ancho_util = A4[0] - 2 * 2.2 * cm

    def pagina(c, doc):
        c.saveState()
        c.setFont("Serif", 7.8)
        c.setFillColor(GRIS)
        c.drawString(2.2 * cm, A4[1] - 1.3 * cm, CENTRO)
        c.drawRightString(A4[0] - 2.2 * cm, A4[1] - 1.3 * cm, f"Programación de aula · {mes_txt}")
        c.setStrokeColor(FILETE)
        c.setLineWidth(0.4)
        c.line(2.2 * cm, A4[1] - 1.45 * cm, A4[0] - 2.2 * cm, A4[1] - 1.45 * cm)
        c.line(2.2 * cm, 1.45 * cm, A4[0] - 2.2 * cm, 1.45 * cm)
        c.drawString(2.2 * cm, 1.05 * cm, f"Programación elaborada por {AUTOR} · {MARCA}")
        c.drawRightString(A4[0] - 2.2 * cm, 1.05 * cm, f"Clase 17 · {CURSO} · Página {doc.page}")
        c.restoreState()

    doc = BaseDocTemplate(str(salida), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.0 * cm, bottomMargin=1.9 * cm,
                          title=f"Programación de aula · {mes_txt} · Clase 17", author=AUTOR, creator=f"{MARCA} · {AUTOR}",
                          subject=prog["centro_interes"])
    doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=pagina)])

    h = []
    # ── Portada / identificación ──
    h += [P("PROGRAMACIÓN DE AULA", "nota"), Spacer(1, 4),
          P(f"Programación mensual · {mes_txt.capitalize()}", "titulo"), Spacer(1, 4),
          P(f"Centro de interés: «{prog['centro_interes']}»", "subtitulo"), Spacer(1, 2),
          P(f"Autor: {AUTOR} · {MARCA}", "subtitulo"), Spacer(1, 14)]
    datos = [
        ["Centro", CENTRO],
        ["Etapa / referente curricular", "Período de formación para la Transición a la Vida Adulta. Referente: Concreción Curricular de Transición a la Vida Adulta (CCTVA) y Adaptaciones Curriculares Significativas (ACUS) del alumnado."],
        ["Grupo", "Clase 17"],
        ["Curso escolar", "2026-2027"],
        ["Temporalización", f"Del {primero.day} al {ultimo.day} de {MESES[m - 1]} de {a} · {n_dias} sesiones diarias · {len(sem)} unidades semanales"],
        ["Autor · maestro tutor (PT)", f"{AUTOR}"],
        ["Profesorado de apoyo implicado", "Audición y Lenguaje · Educación Física · Música (según horario de aula)"],
    ]
    t = Table([[P(k, "dato_k"), P(v, "dato_v")] for k, v in datos], colWidths=[5.0 * cm, ancho_util - 5.0 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEABOVE", (0, 0), (-1, 0), 0.9, TINTA), ("LINEBELOW", (0, -1), (-1, -1), 0.9, TINTA),
                           ("LINEBELOW", (0, 0), (-1, -2), 0.3, FILETE), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4)]))
    h += [t]

    # 1. Marco normativo
    h += [P("1. Marco normativo", "h1"),
          P("La presente programación se elabora conforme a la normativa vigente de ámbito estatal y autonómico:")]
    h += lista([
        "Ley Orgánica 2/2006, de 3 de mayo, de Educación, modificada por la Ley Orgánica 3/2020, de 29 de diciembre (LOMLOE).",
        "Decreto 25/2018, de 26 de febrero, por el que se regula la atención a la diversidad en el ámbito de las enseñanzas no universitarias de la Comunidad Autónoma de Canarias (BOC n.º 46, de 6 de marzo de 2018).",
        "Orden de 13 de diciembre de 2010, por la que se regula la atención al alumnado con necesidades específicas de apoyo educativo en la Comunidad Autónoma de Canarias (BOC n.º 250, de 22 de diciembre de 2010).",
        "Resolución de 9 de febrero de 2011, de la Dirección General de Ordenación, Innovación y Promoción Educativa, por la que se dictan instrucciones sobre los procedimientos y los plazos para la atención educativa del alumnado con necesidades específicas de apoyo educativo (BOC n.º 40, de 24 de febrero de 2011), que establece la CCTVA y sus tres ámbitos de autonomía: personal, social y laboral.",
        "Programación General Anual, Proyecto Educativo y Concreción Curricular de TVA del centro para el curso 2026-2027.",
    ])

    # 2. Contextualización
    h += [P("2. Justificación y contextualización", "h1"),
          P("El grupo está formado por alumnado con necesidades educativas especiales escolarizado en el período de Transición a la Vida Adulta. "
            "La respuesta educativa prioriza la autonomía personal, social y laboral, tal como dispone la CCTVA, y se concreta para cada alumno en su ACUS "
            "y, en su caso, en programas educativos personalizados."),
          P(prog["contexto"]),
          P("Este documento no contiene datos personales del alumnado. Las referencias individuales se recogen en los documentos de seguimiento custodiados por el tutor.", "nota")]

    # 3. Temporalización
    h += [P("3. Temporalización y secuencia de unidades", "h1")]
    filas = [["Ud.", "Fechas", "Contenido central", "Taller"]]
    for i, s in enumerate(sem, 1):
        d1, d2 = date.fromisoformat(s["dias"][0]), date.fromisoformat(s["dias"][-1])
        filas.append([f"U{i}", f"{d1.day}–{d2.day} {MESES[m - 1][:3]}.", f"<b>{s['tema']}</b>. {s['objetivo']}",
                      f"{s['taller']['tipo']}: {s['taller']['titulo'].lower()} ({fecha_larga(s['taller']['dia']).lower()})"])
    h += [tabla(filas, [1.2 * cm, 2.0 * cm, 8.4 * cm, ancho_util - 11.6 * cm])]

    # 4. Objetivos
    h += [P("4. Objetivos didácticos por ámbito de la CCTVA", "h1")]
    obj = prog["objetivos"]
    for k in ("AP", "AS", "AL"):
        h += [P(f"Ámbito de {AMBITO[k]} ({k})", "h2")] + lista(obj[k])

    # 5. Contenidos
    h += [P("5. Contenidos por unidad", "h1")]
    filas = [["Ud.", "Vocabulario (8 pictogramas)", "Secuencia funcional", "Categorización"]]
    for i, s in enumerate(sem, 1):
        voc = ", ".join(v["palabra"].lower() for v in s["vocabulario"])
        pasos = " → ".join(p["palabra"].lower() for p in s["pasos"]["lista"])
        cl = s["clasifica"]
        filas.append([f"U{i}", voc, f"<i>{s['pasos']['titulo']}</i>: {pasos}", f"{cl['pregunta']} ({cl['a']['nombre'].lower()} / {cl['b']['nombre'].lower()})"])
    h += [tabla(filas, [1.2 * cm, 5.2 * cm, 5.4 * cm, ancho_util - 11.8 * cm])]
    h += [P("Contenidos procedimentales y actitudinales comunes: seguimiento de rutinas, discriminación visual y auditiva, percepción figura-fondo (sombras), conteo hasta 3–5, conceptos de tamaño, lectura global, grafomotricidad, "
            "uso funcional de los objetos, hábitos de higiene y cuidado personal, respeto de turnos y valoración del trabajo propio.", "p")]

    # 6. Metodología
    h += [P("6. Metodología", "h1")]
    h += lista([
        "<b>Enseñanza estructurada y rutina estable.</b> Cada día de la semana mantiene el mismo tipo de actividad digital y de ficha, de modo que el alumnado domina la mecánica y centra el esfuerzo en el contenido.",
        "<b>Apoyo visual (SAAC).</b> Todo el vocabulario, las consignas y las secuencias se presentan con pictogramas ARASAAC y palabra escrita en mayúsculas, con locución sintetizada de la consigna.",
        "<b>Aprendizaje sin error y refuerzo positivo.</b> Las actividades digitales no penalizan el error: señalan la respuesta incorrecta, invitan a reintentar y refuerzan verbalmente cada acierto.",
        "<b>Análisis de tareas.</b> Las rutinas de higiene y vestido se descomponen en 4–5 pasos que se trabajan en la aplicación, en la ficha y en la situación real.",
        "<b>Funcionalidad y generalización.</b> Lo trabajado en pantalla y en papel se traslada el mismo día a una situación real del aula, del baño o del taller.",
        "<b>Graduación de la dificultad.</b> Las aplicaciones permiten variar el número de opciones (2, 4 o 6 pictogramas; 4 o 6 parejas) para ajustar la demanda a cada alumno.",
        "<b>Actividades complementarias de nivel inicial.</b> Cada día se añaden tres actividades digitales (colorear con el dedo, pintar puntitos y un juego de percepción o de conceptos básicos: igual, sombras, diferente, cuenta, grande y pequeño) y dos fichas imprimibles equivalentes, para trabajar atención, discriminación visual, conteo y motricidad fina con distintos niveles de exigencia.",
        "<b>Agrupamientos.</b> Actividad digital en gran grupo en la pizarra digital o individual en tableta; ficha individual; taller en pequeño grupo con apoyo del adulto.",
    ])

    # 7. Programación diaria
    h += [PageBreak(), P("7. Programación diaria", "h1"),
          P("Cada sesión incluye una actividad interactiva (pizarra digital o tableta), una ficha imprimible y una actividad funcional en el aula. "
            "Los ámbitos se indican con las siglas AP (Autonomía Personal), AS (Autonomía Social) y AL (Autonomía Laboral).")]
    for i, s in enumerate(sem, 1):
        bloque = [CondPageBreak(5 * cm), P(f"Unidad {i} · {s['tema']}", "h2")]
        filas = [["Día", "Actividad interactiva", "Ficha", "Actividad funcional en el aula", "Ámb."]]
        for k, f in enumerate(s["dias"]):
            d = date.fromisoformat(f)
            rut = prog["rutina"][["lunes", "martes", "miercoles", "jueves", "viernes"][d.weekday()]]
            j, fi = JUEGO[rut["juego"]], FICHA[rut["ficha"]]
            aula = s["aula"][k]
            amb = sorted({j[2], fi[2]} | ({"AP", "AL"} if s["taller"]["dia"] == f else set()), key=["AP", "AS", "AL"].index)
            repaso = d.weekday() == 0 and k == len(s["dias"]) - 1 and k > 0
            juego_txt = f"<b>{j[0]}</b>{' (repaso del mes)' if repaso else ''}. {j[1]}"
            if rut["juego"] == "ordena":
                juego_txt += f" Rutina: {s['pasos']['titulo'].lower()}."
            if rut["juego"] == "clasifica":
                juego_txt += f" Criterio: {s['clasifica']['pregunta'].lower()}"
            ex = EXTRA.get(rut.get("extra"), "")
            if ex:
                juego_txt += f"<br/><i>Complementarias:</i> Colorea con el dedo · Pinta los puntitos · {ex}."
            ficha_txt = f"<b>{fi[0]}</b>. {fi[1]}" + (f"<br/><i>Complementarias:</i> Pinta los puntitos · {ex}." if ex else "")
            filas.append([f"{DIAS[d.weekday()][:3]}. {d.day}", juego_txt, ficha_txt, aula, " ".join(amb)])
        bloque += [tabla(filas, [1.35 * cm, 5.6 * cm, 4.2 * cm, ancho_util - 12.75 * cm, 1.6 * cm], centrar=(4,))]
        h += bloque

    # 8. Atención a la diversidad
    h += [P("8. Atención a la diversidad", "h1")]
    h += lista([
        "Las actividades se ajustan a la ACUS de cada alumno: número de opciones, tipo de respuesta (señalar, tocar, verbalizar) y nivel de apoyo (físico, gestual, verbal o visual), con retirada progresiva de la ayuda.",
        "Las fichas admiten distintos niveles de ejecución: coloreado libre o dentro del contorno, repaso con o sin guía de la mano, recortado con tijera adaptada o de piezas pretroqueladas.",
        "Las secuencias funcionales se trabajan por encadenamiento hacia delante o hacia atrás según el perfil de cada alumno.",
        "Coordinación con la maestra de Audición y Lenguaje para reforzar el vocabulario del mes y con el profesorado de Educación Física y Música en las sesiones compartidas.",
    ])

    # 9. Evaluación
    h += [P("9. Evaluación", "h1"),
          P("La evaluación es continua, formativa y referida a los objetivos de la ACUS de cada alumno. "
            "Se valora con la escala de la CCTVA: <b>NI</b> (no iniciado), <b>I</b> (iniciado), <b>P</b> (en proceso) y <b>A</b> (adquirido)."),
          P("Instrumentos", "h2")]
    h += lista(["Observación sistemática durante las actividades interactivas, las rutinas y los talleres.",
                "Registro mensual por criterio (tabla siguiente).",
                "Producciones del alumnado: fichas diarias archivadas en la carpeta individual.",
                "Comunicación con las familias sobre la generalización de las rutinas en el hogar."])
    criterios = prog["criterios"]
    filas = [["Ámb.", "Criterio de evaluación", "A1", "A2", "A3", "A4", "A5"]]
    for amb, c in criterios:
        filas.append([amb, c, "", "", "", "", ""])
    anch = [1.1 * cm, ancho_util - 1.1 * cm - 5 * 1.25 * cm] + [1.25 * cm] * 5
    t = tabla(filas, anch, centrar=(0, 2, 3, 4, 5, 6))
    t.setStyle(TableStyle([("LINEBEFORE", (2, 0), (-1, -1), 0.3, FILETE)]))
    h += [KeepTogether([P("Registro de evaluación · " + mes_txt, "h2"), t]),
          Spacer(1, 3), P("A1–A5: códigos de alumno. La correspondencia con cada alumno se custodia en el expediente de tutoría. Anotar NI, I, P o A en cada casilla.", "nota")]

    # 10. Familias y recursos
    h += [P("10. Coordinación con las familias", "h1"),
          P("Las actividades interactivas y las fichas de cada día se publican en la web de aula, de acceso libre y sin datos personales, junto con orientaciones semanales para reforzar en casa:")]
    filas = [["Ud.", "Orientaciones para el hogar"]]
    for i, s in enumerate(sem, 1):
        filas.append([f"U{i}", " ".join(s["casa"])])
    h += [tabla(filas, [1.4 * cm, ancho_util - 1.4 * cm])]

    h += [P("11. Recursos", "h1")]
    h += lista([
        "Pizarra digital interactiva del aula y tabletas táctiles.",
        f"Web de aula «Clase 17 · La clase de los chicos»: {n_dias * 4} actividades interactivas y {n_dias * 3} fichas imprimibles del mes (4 y 3 por día).",
        *prog["recursos"],
        f"Pictogramas de ARASAAC (autor: Sergio Palao; origen: ARASAAC, https://arasaac.org; propiedad: Gobierno de Aragón; licencia CC BY-NC-SA). Materiales, actividades interactivas e ilustraciones propias elaborados por {AUTOR} ({MARCA}).",
    ])

    # Firma
    hoy = date.today()
    firma = Table([[P(f"En Teguise, a {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}.", "dato_v"), ""],
                   [Spacer(1, 1.6 * cm), ""],
                   [P(f"Fdo.: {AUTOR}<br/>Maestro tutor (Pedagogía Terapéutica)", "dato_v"), P("V.º B.º Jefatura de Estudios", "dato_v")]],
                  colWidths=[ancho_util / 2, ancho_util / 2])
    firma.setStyle(TableStyle([("LINEABOVE", (0, 2), (0, 2), 0.5, TINTA), ("LINEABOVE", (1, 2), (1, 2), 0.5, TINTA),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, -1), 24)]))
    h += [Spacer(1, 18), KeepTogether([firma])]

    doc.build(h)
    print("Creado", salida)


if __name__ == "__main__":
    construir(sys.argv[1], sys.argv[2])
