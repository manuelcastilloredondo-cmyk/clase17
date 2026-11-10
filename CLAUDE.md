# Clase 17 · La clase de los chicos — reglas del repositorio

Web pública y gratuita con la programación diaria de la Clase 17 (Tránsito a la Vida Adulta,
CEE Nuestra Señora de los Volcanes, Teguise, Lanzarote): un juego interactivo y una ficha PDF por día lectivo,
más la programación mensual en PDF para archivo e inspección.
Autor de todos los materiales: **Manuel Castillo Redondo · Manu en clase**. Todo en español.

## Reglas que no se rompen nunca
1. **Ningún dato del alumnado**: ni nombres, ni fotos, ni iniciales, ni datos de salud, ni horarios individuales.
   El registro de evaluación del PDF usa códigos A1…A5.
2. **ARASAAC**: atribución en cada página y en cada PDF (Sergio Palao · ARASAAC · Gobierno de Aragón · CC BY-NC-SA).
   Sin publicidad ni venta de estos materiales.
3. **Nunca publicar directamente en `main`**: cada mes va en una rama `mes/AAAA-MM` con una pull request
   que el docente revisa y aprueba. Solo se fusiona cuando él lo pide.
4. Sin librerías externas ni rastreadores, salvo Google Fonts y pdf.js (cdnjs) en `ficha.html`.

## Identidad visual: marca «Manu en clase» (@manuenclase)
Clase 17 vive dentro de la marca Manu en clase. Mayúsculas en la web (las pone `comun.css`).
Paleta: celeste `#a1d6e2` (superficies grandes), azul `#4497b0`, azul hondo `#2a6f87` (texto de acento), coral `#fa6876`
(único acento: botón principal y «17»; texto encima `#12343d`), tinta `#1e4f5c` (texto), nube `#eef7fa` (fondo), blanco.
Nada de fondos oscuros grandes. Fuentes: Barlow Condensed 800 cursiva (titulares), 800 (botones), 600 espaciada (antetítulos);
Barlow 400/500/700 (texto). Source Serif 4 solo en el PDF de programación (formal, títulos en tinta).
**«Sígueme en Instagram · @manuenclase»** (https://www.instagram.com/manuenclase/) va en el menú, la portada y el pie de
todas las páginas (clase `.ig`) y en el pie de todas las fichas PDF. **No** va en el PDF de programación para inspección
(allí solo la autoría). Si cambias `recursos/comun.css`, sube su versión (`comun.css?v=N`) en todas las páginas y plantillas: si no, los navegadores siguen usando la copia vieja. Logos e iconos en `recursos/logo/` (se regeneran con `scripts/logo_manu.py <icon-512.png de la marca>`).

## Estructura
```
index.html                         portada: HOY, ESTA SEMANA, semanas anteriores, programación del mes
plantillas/dia.html, juego.html, ficha.html  se copian a cada día (leen datos.json); juego.html?modo=… elige el juego
programacion/
  centros-interes.json             centro de interés de cada mes (octubre–junio) + ideas orientativas
  calendario-2026-27.json          calendario escolar: no lectivos, por confirmar, días del centro
  AAAA-MM.json                     programación del mes (fuente única de web y PDF)
  AAAA-MM-programacion.pdf         programación formal del mes
actividades/catalogo.json          todos los días publicados (acumulativo)
actividades/AAAA-MM-DD/            datos.json · dia.html · juego.html · ficha.html · ficha.pdf · puntitos.pdf · extra.pdf
recursos/pictos, pictos-bn         pictos ARASAAC en color y en blanco y negro (descarga construir.py)
scripts/dias_lectivos.py           días lectivos de un mes por semanas
scripts/construir.py               genera los días del mes y actualiza el catálogo
scripts/programacion_pdf.py        genera el PDF formal del mes
```

## Rutina semanal fija (no cambiar sin que lo pida el docente)
Cada día: 4 actividades digitales y 3 fichas PDF, reunidas en `dia.html`.
| Día | Juego del día (`juego`) | Ficha (`ficha`) | Complementaria (`extra`) |
|---|---|---|---|
| Lunes | toca | colorear | igual |
| Martes | une | lineas | sombras |
| Miércoles | memoria (taller ese día) | recortar | diferente |
| Jueves | ordena | secuencia | cuenta |
| Viernes | clasifica | puntos | tamano |

Además, todos los días: **Colorea con el dedo** (pictos en blanco y negro) y **Pinta los puntitos**
(digital y `puntitos.pdf`; el dibujo de puntitos se genera solo con `scripts/arte.py` a partir del primer picto
del día que da círculos grandes). La complementaria tiene versión digital (`juego.html?modo=extra`) y PDF (`extra.pdf`).
Nivel de referencia: equivalente a Infantil 3 años; apoyo en pictos, pero no todo depende de ellos (siluetas, números, tamaños).

## Cómo preparar el mes siguiente (procedimiento de la tarea mensual)
1. `python3 scripts/dias_lectivos.py AAAA-MM` → semanas y días lectivos. Si una semana tiene 1–2 días sueltos,
   únela a la semana contigua (como el lunes 30 de noviembre, que fue "repaso del mes").
2. Lee `programacion/centros-interes.json` para ese mes. Divide el mes en una unidad por semana: subtemas concretos
   y funcionales para TVA (autonomía personal, social y laboral). Las ideas del archivo son orientativas.
   Si el mes trae vacaciones o fiestas, la última unidad puede anticipar el centro de interés siguiente.
3. Para cada unidad, elige **8 palabras** concretas y cotidianas, una **secuencia funcional** de 4–5 pasos
   y una **clasificación** en dos grupos (4+4 o 3+4). Busca cada picto en ARASAAC
   (`https://api.arasaac.org/v1/pictograms/es/search/<palabra>`) y **míralo** (`https://static.arasaac.org/pictograms/<id>/<id>_300.png`):
   el dibujo tiene que representar exactamente la palabra. Si no hay picto adecuado para un paso,
   dibuja una ilustración propia (ver `dibujar_arboles` en `construir.py`) y usa `"dibujo"` en vez de `"id"`.
4. Escribe `programacion/AAAA-MM.json` copiando la estructura de `programacion/2026-11.json`:
   `rutina` (con `extra` por día, como en noviembre), `semanas[]` (id, tema, dias, objetivo, taller {tipo, titulo, dia = miércoles}, casa[3], vocabulario[8], pasos, clasifica, puntos, aula[uno por día]),
   y los textos del PDF: `contexto`, `objetivos` {AP, AS, AL} (4 cada uno), `criterios` (10–12, [ámbito, texto]), `recursos`.
   `puntos` es una figura de `FIGURAS` en `scripts/fichas_dia.py` (estrella, camiseta, diente, jabon);
   si el tema pide otra, añádela allí (coordenadas 0–1, contorno en sentido horario).
5. `python3 scripts/construir.py programacion/AAAA-MM.json` y `python3 scripts/programacion_pdf.py programacion/AAAA-MM.json programacion/AAAA-MM-programacion.pdf`.
6. Revisa: abre 1 ficha de cada tipo como imagen (`pdftoppm`) y el PDF de programación; nada se sale de la página.
7. Rama `mes/AAAA-MM`, commit, push y pull request con el resumen del mes. No fusionar.
