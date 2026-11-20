"""Tipo de jugador (posicion oficial de players.csv) que entra y sale del Q2 al Q3 y durante el Q3.
Solo lectura. Usa backend/exploracion.py. Genera tablas y graficas SVG (biblioteca estandar)."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
sys.stdout.reconfigure(encoding="utf-8")
from backend import exploracion  # noqa: E402

OUT = AQUI / "graficas"
OUT.mkdir(exist_ok=True)
COL = {"Local": "#1f6feb", "Visitante": "#e5534b"}
PERIODOS = {"q2_a_q3": ("Del Q2 al Q3 (primera jugada del Q3 contra la ultima del Q2)", 2, 3),
            "dentro_q3": ("Durante el Q3 (jugadas consecutivas)", 3, 3)}


def grafica(t, titulo, archivo):
    pos = (t.groupby("posicion").por_cada_100_pares.sum().sort_values(ascending=False).index.tolist())
    w, ml, mt, fila = 760, 70, 70, 56
    h = mt + len(pos) * fila + 40
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="Arial, sans-serif">',
         f'<rect width="{w}" height="{h}" fill="white"/>',
         f'<text x="{w / 2}" y="22" text-anchor="middle" font-size="14" font-weight="bold">{escape(titulo)}</text>']
    leyenda = [("Local entra", COL["Local"], 1), ("Local sale", COL["Local"], 0.35),
               ("Visitante entra", COL["Visitante"], 1), ("Visitante sale", COL["Visitante"], 0.35)]
    for i, (txt, c, op) in enumerate(leyenda):
        s.append(f'<rect x="{80 + i * 160}" y="36" width="12" height="12" fill="{c}" opacity="{op}"/>'
                 f'<text x="{97 + i * 160}" y="47" font-size="11">{txt}</text>')
    mx = max(t.por_cada_100_pares.max(), 1)
    ancho = w - ml - 80
    for k, p in enumerate(pos):
        y0 = mt + k * fila
        s.append(f'<text x="{ml - 8}" y="{y0 + 26}" text-anchor="end" font-size="12" font-weight="bold">{escape(p)}</text>')
        for j, (eq, sen) in enumerate([("Local", "entran"), ("Local", "salen"), ("Visitante", "entran"), ("Visitante", "salen")]):
            r = t[(t.posicion == p) & (t.equipo == eq) & (t.sentido == sen)]
            v = float(r.por_cada_100_pares.iloc[0]) if len(r) else 0.0
            n = int(r.jugadores.iloc[0]) if len(r) else 0
            bw = ancho * v / mx
            yy = y0 + j * 12
            s.append(f'<rect x="{ml}" y="{yy}" width="{bw}" height="10" fill="{COL[eq]}" opacity="{1 if sen == "entran" else 0.35}"/>')
            s.append(f'<text x="{ml + bw + 4}" y="{yy + 9}" font-size="9">{v:.0f} ({n})</text>')
    s.append(f'<text x="{w / 2}" y="{h - 10}" text-anchor="middle" font-size="10">'
             'Jugadores por cada 100 cambios de jugada; entre parentesis, el conteo bruto.</text>')
    s.append("</svg>")
    (OUT / archivo).write_text("\n".join(s), encoding="utf-8")


for clave, (nombre, a, b) in PERIODOS.items():
    t = exploracion.posiciones_cambio(a, b)
    print("=" * 80 + f"\n{nombre}")
    for unidad in ["Ofensiva", "Defensiva"]:
        u = t[t.unidad == unidad]
        pares = u.drop_duplicates("equipo").set_index("equipo").pares.to_dict()
        piv = u.pivot_table(index="posicion", columns=["equipo", "sentido"], values="jugadores", fill_value=0).astype(int)
        piv["total"] = piv.sum(axis=1)
        print(f"\n{unidad} (pares de jugadas: {pares})\n{piv.sort_values('total', ascending=False).drop(columns='total').to_string()}")
        u.to_csv(OUT / f"{clave}_{unidad.lower()}.csv", index=False)
        grafica(u, f"{nombre.split(' (')[0]}: {unidad.lower()}", f"{clave}_{unidad.lower()}.svg")
