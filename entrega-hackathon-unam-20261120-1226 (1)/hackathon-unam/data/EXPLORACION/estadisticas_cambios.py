"""Imprime media, mediana y moda de jugadores que entran, con tres agrupaciones distintas.
Usa backend/exploracion.py (misma logica que la API). Ejecutar desde la raiz del proyecto."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend import exploracion  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
r = exploracion.resumen_cambios()
titulos = {
    "transiciones": "A. TRANSICIONES: primera jugada del cuarto nuevo contra la ultima del cuarto anterior",
    "dentro_cuarto": "B. DENTRO DEL CUARTO: jugadas consecutivas del mismo cuarto",
    "por_cuarto_jugada_nueva": "C. TODOS LOS PARES (A + B) agrupados por el cuarto de la jugada nueva",
}
for clave, titulo in titulos.items():
    print("=" * 80 + "\n" + titulo)
    t = pd.DataFrame(r[clave])
    t["moda"] = t.moda.map(lambda m: "/".join(map(str, m)))
    for unidad in ["Ofensiva", "Defensiva"]:
        p = t[t.unidad == unidad].pivot(index="grupo", columns="equipo", values=["n", "media", "mediana", "moda"])
        print(f"\n{unidad}\n{p.to_string()}")
print("\nPares excluidos de A:", r["excluidos"])
