"""Cambios de plantilla (indirecto): jugadores que entran/salen entre jugadas consecutivas.
Solo lectura. Limite: plays.csv solo trae jugadas de pase (dropbacks), asi que "jugada anterior"
es el pase anterior de esa unidad, no necesariamente el snap anterior."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent
plays = pd.read_csv(DATA / "plays.csv", low_memory=False,
                    usecols=["gameId", "playId", "quarter", "gameClock", "possessionTeam", "defensiveTeam"])
games = pd.read_csv(DATA / "games.csv")
pff = pd.read_csv(DATA / "pffScoutingData.csv", usecols=["gameId", "playId", "nflId", "pff_role"])
players = pd.read_csv(DATA / "players.csv", usecols=["nflId", "officialPosition"])

print("=" * 80)
print("0. Validacion de la inferencia")
OFF = ["Pass", "Pass Block", "Pass Route"]
DEF = ["Coverage", "Pass Rush"]
cnt = pff.assign(lado=pff.pff_role.map(lambda r: "OFF" if r in OFF else "DEF")).groupby(["gameId", "playId", "lado"]).nflId.nunique().unstack()
print("Jugadores por jugada (ofensiva):", cnt.OFF.value_counts().sort_index().to_dict())
print("Jugadores por jugada (defensiva):", cnt.DEF.value_counts().sort_index().to_dict())
print("Filas duplicadas (gameId, playId, nflId):", int(pff.duplicated(["gameId", "playId", "nflId"]).sum()))

# Orden cronologico: cuarto ascendente, reloj descendente (mm:ss)
plays["seg"] = plays.gameClock.str.split(":").map(lambda x: int(x[0]) * 60 + int(x[1]))
plays = plays.sort_values(["gameId", "quarter", "seg", "playId"], ascending=[True, True, False, True])
ok = plays.groupby("gameId").playId.apply(lambda s: s.is_monotonic_increasing).mean() * 100
print(f"Partidos donde playId crece junto con el orden cronologico por cuarto y reloj: {ok:.1f}%")
print("Jugadores en pffScoutingData sin registro en players.csv:", int((~pff.nflId.isin(players.nflId)).sum()), "filas")

# Conjuntos por jugada
pff["lado"] = pff.pff_role.map(lambda r: "OFF" if r in OFF else "DEF")
sets = pff.groupby(["gameId", "playId", "lado"]).nflId.agg(frozenset)
sets = sets.rename("ids").reset_index()
base = plays.merge(sets, on=["gameId", "playId"])
# Equipo dueño de la unidad
base["equipo"] = base.apply(lambda r: r.possessionTeam if r.lado == "OFF" else r.defensiveTeam, axis=1)
base = base.merge(games[["gameId", "homeTeamAbbr"]], on="gameId")
base["es_local"] = base.equipo == base.homeTeamAbbr
base["lado_eq"] = base.es_local.map({True: "Local", False: "Visitante"})

filas = []
for (gid, eq, lado), g in base.groupby(["gameId", "equipo", "lado"], sort=False):
    g = g.sort_values(["quarter", "seg", "playId"], ascending=[True, False, True]).reset_index(drop=True)
    for i in range(1, len(g)):
        a, b = g.ids[i - 1], g.ids[i]
        filas.append((gid, eq, lado, g.lado_eq[i], g.quarter[i - 1], g.quarter[i], len(b - a), len(a - b), len(a & b),
                      b - a, a - b))
cam = pd.DataFrame(filas, columns=["gameId", "equipo", "lado", "lado_eq", "q_prev", "q", "entran", "salen", "comunes", "ids_entran", "ids_salen"])
cam["cambio"] = cam.entran > 0
cam["transicion"] = cam.q_prev != cam.q
print(f"\nPares de jugadas consecutivas de una misma unidad: {len(cam)}")

print("\n" + "=" * 80)
print("1. Cambios promedio entre jugadas consecutivas de la misma unidad, por cuarto de la jugada nueva")
for lado, nombre in [("OFF", "OFENSIVA"), ("DEF", "DEFENSIVA")]:
    t = cam[cam.lado == lado].groupby(["q", "lado_eq"]).agg(pares=("entran", "size"), entran_prom=("entran", "mean"),
                                                            pct_con_cambio=("cambio", "mean"))
    t["entran_prom"] = t.entran_prom.round(3)
    t["pct_con_cambio"] = (t.pct_con_cambio * 100).round(1)
    print(f"\n{nombre}\n{t.to_string()}")

print("\n" + "=" * 80)
print("2. Primera jugada de un cuarto contra la ultima del cuarto anterior (transiciones), y contra el resto")
cam["tipo"] = cam.apply(lambda r: f"Q{r.q_prev}->Q{r.q}" if r.transicion else "dentro del cuarto", axis=1)
for lado, nombre in [("OFF", "OFENSIVA"), ("DEF", "DEFENSIVA")]:
    t = cam[cam.lado == lado].groupby(["lado_eq", "tipo"]).agg(pares=("entran", "size"), entran_prom=("entran", "mean"),
                                                               pct_con_cambio=("cambio", "mean"))
    t["entran_prom"] = t.entran_prom.round(3)
    t["pct_con_cambio"] = (t.pct_con_cambio * 100).round(1)
    print(f"\n{nombre}\n{t.to_string()}")

print("\n" + "=" * 80)
print("3. Q2->Q3 (medio tiempo): visitante ofensiva y local defensiva")
for lado, eq, nombre in [("OFF", "Visitante", "Ofensiva del visitante"), ("DEF", "Local", "Defensiva del local")]:
    s = cam[(cam.lado == lado) & (cam.lado_eq == eq) & (cam.q_prev == 2) & (cam.q == 3)]
    print(f"\n{nombre}: {len(s)} partidos con transicion Q2->Q3")
    print(s[["entran", "salen"]].describe().round(2).to_string())
    print("Partidos con al menos un jugador nuevo:", int(s.cambio.sum()), "de", len(s))
    ent = pd.Series([x for ids in s.ids_entran for x in ids]).to_frame("nflId").merge(players, on="nflId", how="left")
    print("Posicion oficial de jugadores que entran (top 8):")
    print(ent.officialPosition.value_counts().head(8).to_string())

print("\n" + "=" * 80)
print("4. Plantilla total usada por unidad, por cuarto (jugadores distintos por equipo-partido)")
usados = base.groupby(["gameId", "equipo", "lado", "lado_eq", "quarter"]).ids.apply(lambda s: len(frozenset().union(*s))).reset_index(name="distintos")
for lado, nombre in [("OFF", "OFENSIVA"), ("DEF", "DEFENSIVA")]:
    t = usados[usados.lado == lado].groupby(["quarter", "lado_eq"]).distintos.agg(["count", "mean", "median"]).round(2)
    print(f"\n{nombre} (jugadores distintos por equipo en cada cuarto)\n{t.to_string()}")

print("\n" + "=" * 80)
print("5. Q2->Q3 contra otras transiciones: diferencia media por partido (pareada) y error estandar")
import numpy as np
for lado, eq in [("OFF", "Visitante"), ("DEF", "Local")]:
    def serie(a, b):
        return cam[(cam.lado == lado) & (cam.lado_eq == eq) & (cam.q_prev == a) & (cam.q == b)].set_index("gameId").entran
    for otro in [(1, 2), (3, 4)]:
        d = (serie(2, 3) - serie(*otro)).dropna()
        print(f"{lado} {eq}: Q2->Q3 menos Q{otro[0]}->Q{otro[1]}: dif={d.mean():.3f}, EE={d.std() / np.sqrt(len(d)):.3f}, n={len(d)}")
