"""Lista los días lectivos (lunes a viernes) de un mes según el calendario escolar.

Uso: python3 scripts/dias_lectivos.py 2026-12
Imprime un JSON con las semanas (lunes a viernes) y sus días lectivos, más los días por confirmar.
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main(mes):
    cal = json.loads((RAIZ / "programacion/calendario-2026-27.json").read_text(encoding="utf-8"))
    a, m = map(int, mes.split("-"))
    inicio, fin = date.fromisoformat(cal["inicio"]), date.fromisoformat(cal["fin"])
    bloqueos = cal["no_lectivos"] + cal.get("dias_del_centro", [])

    def lectivo(d):
        if d.weekday() > 4 or d < inicio or d > fin:
            return False
        return not any(date.fromisoformat(b["desde"]) <= d <= date.fromisoformat(b["hasta"]) for b in bloqueos)

    d = date(a, m, 1)
    semanas, actual = [], None
    while d.month == m:
        if lectivo(d):
            lunes = d - timedelta(days=d.weekday())
            if actual is None or actual["lunes"] != lunes.isoformat():
                actual = {"lunes": lunes.isoformat(), "dias": []}
                semanas.append(actual)
            actual["dias"].append(d.isoformat())
        d += timedelta(days=1)
    dudas = [p for p in cal.get("por_confirmar", []) if p["fecha"].startswith(mes)]
    print(json.dumps({"mes": mes, "semanas": semanas, "total": sum(len(s["dias"]) for s in semanas), "por_confirmar": dudas},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
