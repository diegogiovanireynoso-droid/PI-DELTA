"""Yardas del visitante en el Q3 segun los jugadores que ENTRAN (visitante en ofensiva, local en defensa).
Solo lectura. La unidad ofensiva del visitante y la defensiva del local comparten la misma jugada
(el visitante tiene la posesion), asi que se unen por (gameId, playId)."""
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
sys.stdout.reconfigure(encoding="utf-8")
from backend import exploracion  # noqa: E402

DATA = AQUI.parent
pos = pd.read_csv(DATA / "players.csv", usecols=["nflId", "officialPosition"]).set_index("nflId").officialPosition
plays = pd.read_csv(DATA / "plays.csv", usecols=["gameId", "playId", "quarter", "possessionTeam", "playResult"])
games = pd.read_csv(DATA / "games.csv", usecols=["gameId", "visitorTeamAbbr"])
v = plays.merge(games, on="gameId")
v = v[(v.quarter == 3) & (v.possessionTeam == v.visitorTeamAbbr)][["gameId", "playId", "playResult"]]

p = exploracion.pares()
p = p[p.q == 3]
ofv = p[(p.unidad == "Ofensiva") & (p.equipo == "Visitante")].set_index(["gameId", "playId"])
dfl = p[(p.unidad == "Defensiva") & (p.equipo == "Local")].set_index(["gameId", "playId"])
d = v.set_index(["gameId", "playId"]).join(ofv[["q_prev", "entran", "ids_entran"]].add_prefix("of_"), how="inner") \
     .join(dfl[["entran", "ids_entran"]].add_prefix("df_"), how="inner")
d["primera_q3"] = d.of_q_prev != 3
print(f"Jugadas del visitante en Q3: {len(v)} | con cambios calculables en ambas unidades: {len(d)}")
print(f"Yardas (playResult) base: media {d.playResult.mean():.2f}, mediana {d.playResult.median():.1f}\n")


def por_posicion(col, nombre):
    posiciones = sorted({pos.get(i, "SIN DATO") for s in d[col] for i in s})
    filas = []
    for ps in posiciones:
        mask = d[col].map(lambda s: any(pos.get(i, "SIN DATO") == ps for i in s))
        a, b = d[mask].playResult, d[~mask].playResult
        filas.append((ps, int(mask.sum()), round(a.mean(), 2), a.median(), round(b.mean(), 2), round(a.mean() - b.mean(), 2)))
    t = pd.DataFrame(filas, columns=["posicion_que_entra", "jugadas_con", "media_con", "mediana_con", "media_sin", "dif_media"])
    print(f"{nombre}\n{t.sort_values('media_con', ascending=False).to_string(index=False)}\n")
    return t


tof = por_posicion("of_ids_entran", "A. CAMBIO DEL VISITANTE (ofensiva): yardas de la jugada si entra al menos un jugador de esa posicion")
tdf = por_posicion("df_ids_entran", "B. CAMBIO DEL LOCAL (defensa): yardas del visitante si entra al menos un jugador de esa posicion")

print("C. Por cantidad de jugadores que entran (media de yardas)")
for col, nombre in [("of_entran", "visitante ofensiva"), ("df_entran", "local defensiva")]:
    g = d.groupby(d[col].clip(upper=3)).playResult.agg(["size", "mean", "median"]).round(2)
    g.index = [f"{i}" if i < 3 else "3 o mas" for i in g.index]
    print(f"{nombre}\n{g.to_string()}\n")

print("D. Primera jugada del Q3 (cambio del medio tiempo) contra el resto del Q3")
print(d.groupby("primera_q3").playResult.agg(["size", "mean", "median"]).round(2).to_string(), "\n")

mejor_of = tof[tof.jugadas_con >= 30].sort_values("media_con", ascending=False).iloc[0]
mejor_df = tdf[tdf.jugadas_con >= 30].sort_values("media_con", ascending=False).iloc[0]
print("E. Mejor posicion con al menos 30 jugadas:")
print(" visitante ofensiva:", mejor_of.posicion_que_entra, "media", mejor_of.media_con)
print(" local defensa:", mejor_df.posicion_que_entra, "media", mejor_df.media_con)
ma = d.of_ids_entran.map(lambda s: any(pos.get(i) == mejor_of.posicion_que_entra for i in s))
mb = d.df_ids_entran.map(lambda s: any(pos.get(i) == mejor_df.posicion_que_entra for i in s))
cruce = d.assign(of=ma, df=mb).groupby(["of", "df"]).playResult.agg(["size", "mean", "median"]).round(2)
print("\nCruce (of = entra", mejor_of.posicion_que_entra, "al visitante; df = entra", mejor_df.posicion_que_entra, "al local):")
print(cruce.to_string())
print(f"\nJugadas donde ocurren ambos cambios: {int((ma & mb).sum())} de {len(d)}")
