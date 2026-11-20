"""Metricas del dashboard: dominio ofensivo del VISITANTE en el 3er cuarto y cambios en la defensa LOCAL.

Definiciones (tomadas de data/EXPLORACION/ y del README):
- Yardas = `playResult` de plays.csv en jugadas del Q3 donde `possessionTeam` es el visitante de games.csv.
- Cambios = jugadores que entran a la defensa local respecto a la jugada anterior de esa misma unidad
  (backend/exploracion.py, roles Coverage y Pass Rush de pffScoutingData.csv), en las jugadas del Q3.
  La defensa siempre tiene 11 jugadores, asi que entran = salen.
- Moda: valores enteros; si hay varias se reporta la menor y se listan todas en `modas`.
- Por temporada: se agrupan todas las jugadas de la temporada (no es promedio de promedios).
  `equipo` = "TODOS" o el visitante (solo sus partidos como visitante).
Solo lectura de data/*.csv; todo se calcula en memoria.
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

from backend import exploracion

DATA = Path(__file__).resolve().parent.parent / "data"


def _estadisticos(s: pd.Series) -> dict:
    v = s.dropna()
    modas = sorted(int(x) for x in v.round().astype(int).mode())
    return {"n": int(len(v)), "media": round(float(v.mean()), 2), "mediana": float(v.median()),
            "moda": modas[0], "modas": modas}


def _por_partido(df: pd.DataFrame, col: str) -> list[dict]:
    filas = []
    for gid, g in df.groupby("gameId"):
        r = g.iloc[0]
        filas.append({"gameId": int(gid), "season": int(r.season), "week": int(r.week), "fecha": r.gameDate,
                      "visitante": r.visitorTeamAbbr, "local": r.homeTeamAbbr, **_estadisticos(g[col])})
    return sorted(filas, key=lambda f: (f["season"], f["gameId"]))


def _por_temporada(df: pd.DataFrame, col: str) -> list[dict]:
    filas = []
    for season, g in df.groupby("season"):
        filas.append({"season": int(season), "equipo": "TODOS", **_estadisticos(g[col])})
        for eq, ge in g.groupby("visitorTeamAbbr"):
            filas.append({"season": int(season), "equipo": eq, **_estadisticos(ge[col])})
    return filas


@lru_cache(maxsize=1)
def todo() -> dict:
    games = pd.read_csv(DATA / "games.csv")
    plays = pd.read_csv(DATA / "plays.csv", usecols=["gameId", "playId", "quarter", "possessionTeam", "playResult"])

    # 1) Yardas del visitante atacando en el Q3
    y = plays[plays.quarter == 3].merge(games, on="gameId")
    y = y[y.possessionTeam == y.visitorTeamAbbr]

    # 2) Cambios en la defensa local en el Q3 (la defensa local actua cuando ataca el visitante)
    p = exploracion.pares()
    c = p[(p.unidad == "Defensiva") & (p.equipo == "Local") & (p.q == 3)].merge(games, on="gameId")

    partidos = [{"gameId": int(r.gameId), "season": int(r.season), "week": int(r.week), "fecha": r.gameDate,
                 "visitante": r.visitorTeamAbbr, "local": r.homeTeamAbbr}
                for r in games.sort_values(["season", "gameId"]).itertuples()]
    meta = {
        "temporadas": sorted(int(s) for s in games.season.unique()),
        "equipos_visitantes": sorted(games.visitorTeamAbbr.unique().tolist()),
        "partidos": partidos,
        "jugadas_yardas": int(len(y)),
        "jugadas_cambios": int(len(c)),
        "notas": [
            "Yardas = playResult de jugadas de pase del visitante en el 3er cuarto (plays.csv solo trae pases).",
            "Cambios = jugadores que entran a la defensa local respecto a la jugada anterior de esa unidad en el Q3.",
            "Moda redondeada a yardas enteras; si hay varias se muestra la menor.",
            "Por temporada se agrupan todas las jugadas; el filtro de equipo usa solo partidos del equipo como visitante.",
        ],
    }
    return {
        "meta": meta,
        "yardas_por_partido": _por_partido(y, "playResult"),
        "yardas_por_temporada": _por_temporada(y, "playResult"),
        "cambios_por_partido": _por_partido(c, "entran"),
        "cambios_por_temporada": _por_temporada(c, "entran"),
    }
