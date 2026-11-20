"""Analisis de cuartos: por que el visitante rinde mas en el 3er cuarto. Solo lectura."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent
plays = pd.read_csv(DATA / "plays.csv", low_memory=False)
games = pd.read_csv(DATA / "games.csv")
pff = pd.read_csv(DATA / "pffScoutingData.csv", usecols=["gameId", "playId", "pff_role", "pff_positionLinedUp"])

m = plays.merge(games[["gameId", "homeTeamAbbr", "visitorTeamAbbr"]], on="gameId", how="left")
m["lado"] = (m.possessionTeam == m.homeTeamAbbr).map({True: "Home", False: "Visitor"})
# Visitante ataca = local defiende. Local ataca = visitante defiende.
vis_ataca = m[m.lado == "Visitor"]


def modas(s):
    """Todas las modas (hay empates), como texto."""
    mo = s.dropna().mode()
    return ", ".join(str(x) for x in mo.tolist())


print("=" * 80)
print("TAREA 1A: moda, media y mediana por cuarto y lado que ataca")
for col in ["playResult", "prePenaltyPlayResult", "yardsToGo", "defendersInBox"]:
    print(f"\n--- {col} ---")
    t = m.groupby(["quarter", "lado"])[col].agg(media="mean", mediana="median", moda=modas, n="count")
    t["media"] = t.media.round(3)
    print(t.to_string())

print("\n--- Todas las jugadas por cuarto (sin separar lado) ---")
for col in ["playResult", "yardsToGo", "defendersInBox"]:
    t = m.groupby("quarter")[col].agg(media="mean", mediana="median", moda=modas)
    t["media"] = t.media.round(3)
    print(f"\n{col}\n{t.to_string()}")

print("\n" + "=" * 80)
print("TAREA 1B: modas de la defensa del LOCAL (cuando el visitante ataca) y ataque del VISITANTE")
def_cols = ["personnelD", "pff_passCoverage", "pff_passCoverageType"]
off_cols = ["offenseFormation", "personnelO", "dropBackType", "pff_playAction"]
mod_def = vis_ataca.groupby("quarter")[def_cols + ["defendersInBox"]].agg(modas)
mod_off = vis_ataca.groupby("quarter")[off_cols].agg(modas)
print("\nDefensa del local por cuarto (moda):\n" + mod_def.to_string())
print("\nOfensiva del visitante por cuarto (moda):\n" + mod_off.to_string())

# Posiciones alineadas (pffScoutingData). El rol indica el lado: defensa = Coverage / Pass Rush.
base = vis_ataca[["gameId", "playId", "quarter"]]
pos = pff.merge(base, on=["gameId", "playId"], how="inner")
roles_def = ["Coverage", "Pass Rush"]
roles_off = ["Pass", "Pass Block", "Pass Route"]
for titulo, roles in [("DEFENSA del local (Coverage + Pass Rush)", roles_def),
                      ("OFENSIVA del visitante (Pass + Pass Block + Pass Route)", roles_off)]:
    sub = pos[pos.pff_role.isin(roles)]
    print(f"\nPosicion alineada mas frecuente, {titulo}")
    filas = []
    for q, g in sub.groupby("quarter"):
        vc = g.pff_positionLinedUp.value_counts()
        top3 = "; ".join(f"{k} ({v})" for k, v in vc.head(3).items())
        filas.append((q, len(g), top3))
    print(pd.DataFrame(filas, columns=["quarter", "registros", "top3_posiciones (conteo)"]).to_string(index=False))

print("\n" + "=" * 80)
print("TAREA 1C: el 3er cuarto contra el resto, cuando el visitante ataca")
variables = def_cols + ["defendersInBox"] + off_cols
cuartos = sorted(vis_ataca.quarter.unique())
for v in variables:
    print(f"\n[{v}]")
    dif = 0
    for q in cuartos:
        a = vis_ataca[vis_ataca.quarter == q][v].dropna()
        b = vis_ataca[vis_ataca.quarter != q][v].dropna()
        ma, mb = a.mode().tolist(), b.mode().tolist()
        distinto = ma != mb
        dif += distinto
        print(f"  Q{q}: moda={ma} | moda de los demas cuartos={mb} | {'DIFERENTE' if distinto else 'igual'}")
    print(f"  Cuartos con moda diferente a la de los demas: {dif} de {len(cuartos)}")

print("\nDiferencia de proporciones Q3 contra Q1+Q2+Q4 (puntos porcentuales), top 6 por variable:")
resto = vis_ataca[vis_ataca.quarter.isin([1, 2, 4])]
q3 = vis_ataca[vis_ataca.quarter == 3]
for v in ["personnelD", "pff_passCoverage", "pff_passCoverageType", "offenseFormation", "dropBackType", "pff_playAction"]:
    p3 = q3[v].value_counts(normalize=True) * 100
    pr = resto[v].value_counts(normalize=True) * 100
    d = (p3.sub(pr, fill_value=0)).round(2)
    d = d.reindex(d.abs().sort_values(ascending=False).index).head(6)
    print(f"\n[{v}] n_Q3={q3[v].notna().sum()} n_resto={resto[v].notna().sum()}")
    print(pd.DataFrame({"Q3_%": p3.reindex(d.index).round(2), "resto_%": pr.reindex(d.index).round(2),
                        "dif_pp": d}).to_string())

print("\nPor partido: el local cambia su cobertura mas frecuente en Q3 respecto a Q1+Q2+Q4 (visitante atacando)")
cont = {"cambia": 0, "igual": 0, "sin_datos_Q3": 0, "empate_en_moda": 0}
for gid, g in vis_ataca.groupby("gameId"):
    a = g[g.quarter == 3].pff_passCoverage.mode().tolist()
    b = g[g.quarter.isin([1, 2, 4])].pff_passCoverage.mode().tolist()
    if not a or not b:
        cont["sin_datos_Q3"] += 1
    elif len(a) > 1 or len(b) > 1:
        cont["empate_en_moda"] += 1
    elif a != b:
        cont["cambia"] += 1
    else:
        cont["igual"] += 1
print(cont, "| total partidos:", vis_ataca.gameId.nunique())

print("\nTambien al reves: el visitante cambia su formacion mas frecuente en Q3 (por partido)")
cont = {"cambia": 0, "igual": 0, "sin_datos_Q3": 0, "empate_en_moda": 0}
for gid, g in vis_ataca.groupby("gameId"):
    a = g[g.quarter == 3].offenseFormation.mode().tolist()
    b = g[g.quarter.isin([1, 2, 4])].offenseFormation.mode().tolist()
    if not a or not b:
        cont["sin_datos_Q3"] += 1
    elif len(a) > 1 or len(b) > 1:
        cont["empate_en_moda"] += 1
    elif a != b:
        cont["cambia"] += 1
    else:
        cont["igual"] += 1
print(cont)

print("\n" + "=" * 80)
print("EXTRA: el promedio del visitante en Q3 depende de jugadas largas?")
filas = []
for q, d in vis_ataca.groupby("quarter"):
    p95 = d.playResult.quantile(0.95)
    filas.append((q, len(d), round(d.playResult.mean(), 3), d.playResult.median(),
                  round((d.playResult >= 20).mean() * 100, 2), d.playResult.max(),
                  round(d.playResult.clip(upper=p95).mean(), 3)))
print(pd.DataFrame(filas, columns=["quarter", "jugadas", "media", "mediana", "%_jugadas_>=20yd",
                                   "max_yardas", "media_recortada_p95"]).to_string(index=False))
