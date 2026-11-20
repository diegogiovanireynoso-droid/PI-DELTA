"""Graficas de respuesta: (1) yardas promedio por cuarto y (2) moda de posiciones que entran/salen en el Q3.
Solo lectura de data/*.csv. Salida: SVG (biblioteca estandar) en data/EXPLORACION/graficas/."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
sys.stdout.reconfigure(encoding="utf-8")
from backend import exploracion  # noqa: E402

DATA = AQUI.parent
OUT = AQUI / "graficas"
OUT.mkdir(exist_ok=True)
COL = {"Local": "#1f6feb", "Visitante": "#e5534b"}


def cabecera(w, h, titulo):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="Arial, sans-serif">',
            f'<rect width="{w}" height="{h}" fill="white"/>',
            f'<text x="{w / 2}" y="24" text-anchor="middle" font-size="15" font-weight="bold">{escape(titulo)}</text>']


# ---------------------------------------------------------------- 1. yardas promedio por cuarto
plays = pd.read_csv(DATA / "plays.csv", usecols=["gameId", "quarter", "possessionTeam", "playResult"])
games = pd.read_csv(DATA / "games.csv", usecols=["gameId", "homeTeamAbbr"])
m = plays.merge(games, on="gameId")
m["equipo"] = (m.possessionTeam == m.homeTeamAbbr).map({True: "Local", False: "Visitante"})
y = m.groupby(["quarter", "equipo"]).playResult.agg(["mean", "median", "size"]).round(3)
print("Yardas por jugada (playResult) segun el equipo que ataca\n", y.to_string())
mejor = y.xs("Visitante", level="equipo")["mean"].idxmax()
print(f"\nCuarto con mayor promedio del visitante: Q{mejor}")

w, h, ml, mt, mb = 760, 420, 60, 60, 70
pw, ph = w - ml - 30, h - mt - mb
ymax = 8.5


def yy(v):
    return mt + ph - v / ymax * ph


s = cabecera(w, h, "Yardas promedio por jugada del equipo que ataca, por cuarto")
for k in range(0, 9):
    s.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{yy(k)}" y2="{yy(k)}" stroke="#ddd"/>'
             f'<text x="{ml - 8}" y="{yy(k) + 4}" text-anchor="end" font-size="11">{k}</text>')
gw = pw / 5
for i, q in enumerate(range(1, 6)):
    x0 = ml + i * gw + gw * 0.12
    bw = gw * 0.36
    if q == mejor:
        s.append(f'<rect x="{ml + i * gw + 2}" y="{mt}" width="{gw - 4}" height="{ph}" fill="#fff4d6"/>')
    for j, eq in enumerate(["Visitante", "Local"]):
        r = y.loc[(q, eq)]
        x = x0 + j * (bw + 4)
        s.append(f'<rect x="{x}" y="{yy(r["mean"])}" width="{bw}" height="{mt + ph - yy(r["mean"])}" fill="{COL[eq]}"'
                 f' opacity="{1 if eq == "Visitante" else 0.45}"/>')
        s.append(f'<text x="{x + bw / 2}" y="{yy(r["mean"]) - 5}" text-anchor="middle" font-size="11" font-weight="bold">{r["mean"]:.2f}</text>')
        s.append(f'<text x="{x + bw / 2}" y="{mt + ph + 14}" text-anchor="middle" font-size="9">n={int(r["size"])}</text>')
    s.append(f'<text x="{ml + i * gw + gw / 2}" y="{mt + ph + 32}" text-anchor="middle" font-size="12">'
             f'{"Q" + str(q) if q < 5 else "Tiempo extra"}</text>')
s.append(f'<line x1="{ml}" x2="{ml}" y1="{mt}" y2="{mt + ph}" stroke="black"/><line x1="{ml}" x2="{ml + pw}" y1="{mt + ph}" y2="{mt + ph}" stroke="black"/>')
s.append(f'<rect x="{ml}" y="{h - 22}" width="12" height="12" fill="{COL["Visitante"]}"/><text x="{ml + 17}" y="{h - 12}" font-size="11">Visitante ataca</text>')
s.append(f'<rect x="{ml + 130}" y="{h - 22}" width="12" height="12" fill="{COL["Local"]}" opacity="0.45"/><text x="{ml + 147}" y="{h - 12}" font-size="11">Local ataca</text>')
s.append(f'<text x="{ml + 250}" y="{h - 12}" font-size="11">Resaltado: Q{mejor}, el mejor promedio del visitante</text>')
s.append("</svg>")
(OUT / "respuesta1_yardas_por_cuarto.svg").write_text("\n".join(s), encoding="utf-8")

# ---------------------------------------------------------------- 2. moda de posiciones que entran y salen en Q3
t = exploracion.posiciones_cambio(3, 3)  # jugadas consecutivas dentro del Q3
print("\nModa de la posicion que ENTRA / SALE durante el Q3 (conteo de jugadores)")
moda = {}
for (unidad, eq, sen), g in t.groupby(["unidad", "equipo", "sentido"]):
    top = g.sort_values("jugadores", ascending=False).iloc[0]
    moda[(unidad, eq, sen)] = (top.posicion, int(top.jugadores))
    print(f"  {unidad:9s} {eq:9s} {sen:6s}: {top.posicion} ({int(top.jugadores)} de {int(g.jugadores.sum())} jugadores, {int(top.pares)} cambios de jugada)")

w, h = 760, 880
s = cabecera(w, h, "3er cuarto: posiciones que entran y salen, por equipo")
ml, bh = 70, 12
oy = 40
for unidad in ["Ofensiva", "Defensiva"]:
    u = t[t.unidad == unidad]
    orden = u.groupby("posicion").jugadores.sum().sort_values(ascending=False).head(5).index.tolist()
    mx = u[u.posicion.isin(orden)].jugadores.max()
    s.append(f'<text x="{ml}" y="{oy + 18}" font-size="14" font-weight="bold">{unidad}</text>')
    for j, (txt, eq, op) in enumerate([("Local entra", "Local", 1), ("Local sale", "Local", 0.35),
                                       ("Visitante entra", "Visitante", 1), ("Visitante sale", "Visitante", 0.35)]):
        s.append(f'<rect x="{200 + j * 140}" y="{oy + 7}" width="12" height="12" fill="{COL[eq]}" opacity="{op}"/>'
                 f'<text x="{217 + j * 140}" y="{oy + 17}" font-size="11">{txt}</text>')
    for k, p in enumerate(orden):
        y0 = oy + 34 + k * 72
        s.append(f'<text x="{ml - 8}" y="{y0 + 30}" text-anchor="end" font-size="13" font-weight="bold">{p}</text>')
        for j, (eq, sen) in enumerate([("Local", "entran"), ("Local", "salen"), ("Visitante", "entran"), ("Visitante", "salen")]):
            r = u[(u.posicion == p) & (u.equipo == eq) & (u.sentido == sen)]
            v = int(r.jugadores.iloc[0]) if len(r) else 0
            bw = (w - ml - 90) * v / mx
            by = y0 + j * (bh + 3)
            es_moda = moda[(unidad, eq, sen)][0] == p
            s.append(f'<rect x="{ml}" y="{by}" width="{bw}" height="{bh}" fill="{COL[eq]}" opacity="{1 if sen == "entran" else 0.35}"'
                     f'{" stroke=\"black\" stroke-width=\"2\"" if es_moda else ""}/>')
            s.append(f'<text x="{ml + bw + 4}" y="{by + 10}" font-size="10">{v}{" (moda)" if es_moda else ""}</text>')
    oy += 34 + 5 * 72 + 20
s.append(f'<text x="{w / 2}" y="{h - 10}" text-anchor="middle" font-size="10">'
         'Jugadas consecutivas dentro del Q3 (unos 800 cambios de jugada por equipo). Contorno negro = moda.</text>')
s.append("</svg>")
(OUT / "respuesta2_moda_posiciones_q3.svg").write_text("\n".join(s), encoding="utf-8")
print("\nGraficas guardadas en", OUT)
