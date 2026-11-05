"""Construye los materiales de un mes a partir de programacion/AAAA-MM.json.

Uso:  python3 scripts/construir.py programacion/2026-11.json

Para cada día lectivo crea actividades/AAAA-MM-DD/ con:
  datos.json  · juego.html (copia de plantillas/juego.html) · ficha.pdf
y regenera actividades/catalogo.json. Los pictos se guardan una sola vez en
recursos/pictos/ (color) y recursos/pictos-bn/ (blanco y negro, para colorear).
"""
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fichas_dia  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PICTOS = RAIZ / "recursos/pictos"
PICTOS_BN = RAIZ / "recursos/pictos-bn"
DIBUJOS = RAIZ / "recursos/dibujos"
DIAS_SEMANA = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
DIAS_TXT = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
MESES_TXT = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
JUEGOS = {"toca": "TOCA Y ESCUCHA", "une": "UNE CADA DIBUJO", "memoria": "MEMORIA",
          "ordena": "ORDENA LOS PASOS", "clasifica": "CLASIFICA"}


def bajar(pid):
    for carpeta, url in ((PICTOS, f"https://static.arasaac.org/pictograms/{pid}/{pid}_500.png"),
                         (PICTOS_BN, f"https://api.arasaac.org/v1/pictograms/{pid}?color=false&resolution=500&download=false")):
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / f"{pid}.png"
        if not destino.exists():
            urllib.request.urlretrieve(url, destino)


def dibujar_arboles():
    """Árbol de Navidad en 4 pasos (dibujo propio, no ARASAAC)."""
    DIBUJOS.mkdir(parents=True, exist_ok=True)
    tronco = '<rect x="225" y="400" width="50" height="60" rx="6" fill="#8a5a2b" stroke="#1c3d1f" stroke-width="10"/>'
    maceta = '<path d="M170 440 H330 L310 490 H190 Z" fill="#c0392b" stroke="#1c3d1f" stroke-width="10" stroke-linejoin="round"/>'
    copa = '<path d="M250 70 L380 250 H320 L410 400 H90 L180 250 H120 Z" fill="#2f8f3a" stroke="#1c3d1f" stroke-width="12" stroke-linejoin="round"/>'
    luces = ('<path d="M150 235 Q250 280 350 235 M115 375 Q250 430 385 375" fill="none" stroke="#1c3d1f" stroke-width="5"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="11" fill="{c}" stroke="#1c3d1f" stroke-width="4"/>' for x, y, c in
                       [(170, 245, "#f5c518"), (215, 258, "#e74c3c"), (260, 262, "#3498db"), (305, 255, "#f5c518"), (340, 240, "#e74c3c"),
                        (140, 385, "#3498db"), (190, 400, "#f5c518"), (245, 405, "#e74c3c"), (300, 400, "#3498db"), (355, 388, "#f5c518")]))
    bolas = "".join(f'<circle cx="{x}" cy="{y}" r="20" fill="{c}" stroke="#1c3d1f" stroke-width="7"/>' for x, y, c in
                    [(230, 170, "#e74c3c"), (285, 200, "#f5c518"), (200, 310, "#3498db"), (300, 320, "#e74c3c"), (250, 345, "#f5c518")])
    estrella = '<path d="M250 10 L268 52 L314 55 L279 84 L290 129 L250 105 L210 129 L221 84 L186 55 L232 52 Z" fill="#f5c518" stroke="#1c3d1f" stroke-width="9" stroke-linejoin="round"/>'
    capas = [tronco + maceta + copa, tronco + maceta + copa + luces, tronco + maceta + copa + luces + bolas,
             tronco + maceta + copa + luces + bolas + estrella]
    for i, cuerpo in enumerate(capas, 1):
        svg = DIBUJOS / f"arbol-{i}.svg"
        svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">{cuerpo}</svg>', encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", "500", str(svg), "-o", str(DIBUJOS / f"arbol-{i}.png")], check=True)


def item(e, rel="../../"):
    """Elemento con rutas relativas para el juego y absolutas para el PDF."""
    if "dibujo" in e:
        web = f"{rel}recursos/dibujos/{e['dibujo']}.png"
        color = bn = DIBUJOS / f"{e['dibujo']}.png"
    else:
        bajar(e["id"])
        web = f"{rel}recursos/pictos/{e['id']}.png"
        color, bn = PICTOS / f"{e['id']}.png", PICTOS_BN / f"{e['id']}.png"
    return {"palabra": e["palabra"], "voz": e["voz"], "picto": web, **({"grupo": e["grupo"]} if "grupo" in e else {})}, \
           {"palabra": e["palabra"], "color": color, "bn": bn}


def rotar(lista, n):
    n %= len(lista)
    return lista[n:] + lista[:n]


def main(ruta):
    prog = json.loads((RAIZ / ruta).read_text(encoding="utf-8"))
    dibujar_arboles()
    catalogo = []
    plantilla = RAIZ / "plantillas/juego.html"
    for s_idx, sem in enumerate(prog["semanas"]):
        lunes_vistos = 0
        for d_idx, fecha in enumerate(sem["dias"]):
            f = date.fromisoformat(fecha)
            dia = DIAS_SEMANA[f.weekday()]
            rut = prog["rutina"][dia]
            vocab = rotar(sem["vocabulario"], d_idx * 2)
            tema = sem["tema"].upper()
            if dia == "lunes":
                lunes_vistos += 1
            repaso = sem.get("repaso_ultimo_lunes", True) and dia == "lunes" and lunes_vistos > 1
            if repaso:  # segundo lunes de la semana larga: repaso del mes
                vocab = [v for s in prog["semanas"] for v in s["vocabulario"][:2]]
                tema = "REPASO DEL MES"
            web_el, pdf_el = zip(*[item(e) for e in vocab])
            datos = {"fecha": fecha, "tema": tema, "juego": rut["juego"],
                     "titulo": f"{JUEGOS[rut['juego']]}: {tema}", "ficha_titulo": f"{fichas_dia.NOMBRES[rut['ficha']][0]}: {tema}",
                     "elementos": list(web_el)}
            web_pasos, pdf_pasos = zip(*[item(e) for e in sem["pasos"]["lista"]])
            datos["pasos"] = {"titulo": sem["pasos"]["titulo"], "lista": list(web_pasos)}
            cl = sem["clasifica"]
            web_cl, _ = zip(*[item(e) for e in cl["elementos"]])
            for k in ("a", "b"):
                bajar(cl[k]["id"])
            datos["clasifica"] = {"pregunta": cl["pregunta"], "elementos": list(web_cl),
                                  **{k: {"nombre": cl[k]["nombre"], "picto": f"../../recursos/pictos/{cl[k]['id']}.png"} for k in ("a", "b")}}
            carpeta = RAIZ / "actividades" / fecha
            carpeta.mkdir(parents=True, exist_ok=True)
            (carpeta / "datos.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
            shutil.copyfile(plantilla, carpeta / "juego.html")
            shutil.copyfile(RAIZ / "plantillas/ficha.html", carpeta / "ficha.html")
            fecha_txt = f"{DIAS_TXT[f.weekday()]} {f.day} DE {MESES_TXT[f.month - 1]}"
            fichas_dia.generar(carpeta / "ficha.pdf", rut["ficha"], tema, fecha_txt, list(pdf_el),
                               pasos=list(pdf_pasos), figura=sem["puntos"] if not repaso else "estrella", semilla=f.day)
            catalogo.append({
                "id": fecha, "fecha": fecha, "semana": sem["id"], "tema": tema, "centro": prog["centro_interes"].upper(),
                "titulo": JUEGOS[rut["juego"]], "ficha_tipo": fichas_dia.NOMBRES[rut["ficha"]][0],
                "portada": f"recursos/pictos/{vocab[0]['id']}.png", "juego": "juego.html", "ficha": "ficha.html", "pdf": "ficha.pdf",
                "taller": sem["taller"]["titulo"] if sem["taller"]["dia"] == fecha else None,
            })
            print(f"{fecha} {dia:9} {rut['juego']:9} {rut['ficha']:9} {tema}")
    ruta_cat = RAIZ / "actividades/catalogo.json"
    previo = json.loads(ruta_cat.read_text(encoding="utf-8")) if ruta_cat.exists() else []
    nuevos = {a["id"] for a in catalogo}
    todo = [a for a in previo if a["id"] not in nuevos and not a["fecha"].startswith(prog["mes"])] + catalogo
    todo.sort(key=lambda a: a["fecha"])
    ruta_cat.write_text(json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
    # todas las fichas del mes en un solo PDF, para imprimir de una vez
    from pypdf import PdfWriter
    w = PdfWriter()
    for a in catalogo:
        w.append(str(RAIZ / "actividades" / a["id"] / "ficha.pdf"))
    w.write(str(RAIZ / "programacion" / f"{prog['mes']}-fichas.pdf"))
    print(f"{len(catalogo)} días creados")


if __name__ == "__main__":
    main(sys.argv[1])
