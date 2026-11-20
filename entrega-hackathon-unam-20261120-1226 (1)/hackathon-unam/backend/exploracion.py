"""Exploración: jugadores que entran entre jugadas consecutivas de una misma unidad.

Solo lectura de data/*.csv. Se calcula en memoria; no escribe archivos.
Limite: plays.csv solo trae jugadas de pase, asi que "jugada anterior" es el pase anterior de la unidad.
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
ROLES_OFENSIVA = ["Pass", "Pass Block", "Pass Route"]
ROLES_DEFENSIVA = ["Coverage", "Pass Rush"]


@lru_cache(maxsize=1)
def pares() -> pd.DataFrame:
    """Un renglon por par de jugadas consecutivas de una misma unidad (ofensiva o defensiva)."""
    plays = pd.read_csv(DATA / "plays.csv", usecols=["gameId", "playId", "quarter", "gameClock",
                                                      "possessionTeam", "defensiveTeam"])
    games = pd.read_csv(DATA / "games.csv", usecols=["gameId", "homeTeamAbbr"])
    pff = pd.read_csv(DATA / "pffScoutingData.csv", usecols=["gameId", "playId", "nflId", "pff_role"])

    pff["unidad"] = pff.pff_role.map(lambda r: "Ofensiva" if r in ROLES_OFENSIVA else "Defensiva")
    sets = pff.groupby(["gameId", "playId", "unidad"]).nflId.agg(frozenset).rename("ids").reset_index()
    plays["seg"] = plays.gameClock.str.split(":").map(lambda x: int(x[0]) * 60 + int(x[1]))
    base = plays.merge(games, on="gameId").merge(sets, on=["gameId", "playId"])
    equipo = base.possessionTeam.where(base.unidad == "Ofensiva", base.defensiveTeam)
    base["equipo"] = (equipo == base.homeTeamAbbr).map({True: "Local", False: "Visitante"})

    filas = []
    for (gid, unidad, eq), g in base.groupby(["gameId", "unidad", "equipo"], sort=False):
        g = g.sort_values(["quarter", "seg", "playId"], ascending=[True, False, True])
        q, ids, pid = g.quarter.tolist(), g.ids.tolist(), g.playId.tolist()
        for i in range(1, len(g)):
            nuevos, salen = ids[i] - ids[i - 1], ids[i - 1] - ids[i]
            filas.append((gid, pid[i], unidad, eq, q[i - 1], q[i], len(nuevos), nuevos, salen))
    return pd.DataFrame(filas, columns=["gameId", "playId", "unidad", "equipo", "q_prev", "q", "entran",
                                        "ids_entran", "ids_salen"])


def posiciones_cambio(q_prev: int, q: int) -> pd.DataFrame:
    """Jugadores que entran y salen, por posicion oficial (players.csv), unidad y equipo.

    q_prev == q: jugadas consecutivas dentro de ese cuarto. q_prev != q: transicion entre cuartos.
    """
    p = pares()
    p = p[(p.q_prev == q_prev) & (p.q == q)]
    pos = pd.read_csv(DATA / "players.csv", usecols=["nflId", "officialPosition"]).set_index("nflId").officialPosition
    filas = []
    for _, r in p.iterrows():
        for ids, sentido in [(r.ids_entran, "entran"), (r.ids_salen, "salen")]:
            for i in ids:
                filas.append((r.unidad, r.equipo, sentido, pos.get(i, "SIN DATO")))
    d = pd.DataFrame(filas, columns=["unidad", "equipo", "sentido", "posicion"])
    pares_n = p.groupby(["unidad", "equipo"]).size().rename("pares").reset_index()
    t = d.groupby(["unidad", "equipo", "sentido", "posicion"]).size().rename("jugadores").reset_index()
    t = t.merge(pares_n, on=["unidad", "equipo"])
    t["por_cada_100_pares"] = (t.jugadores / t.pares * 100).round(1)
    return t


def _stats(s: pd.Series) -> dict:
    return {"n": int(len(s)), "media": round(float(s.mean()), 3), "mediana": float(s.median()),
            "moda": [int(x) for x in s.mode().tolist()]}


def _tabla(df: pd.DataFrame, clave: str, etiqueta) -> list[dict]:
    out = []
    for (unidad, k, eq), g in df.groupby(["unidad", clave, "equipo"]):
        out.append({"unidad": unidad, "grupo": etiqueta(k), "equipo": eq, **_stats(g.entran)})
    return out


def resumen_cambios() -> dict:
    p = pares()
    p = p.assign(transicion=p.q_prev != p.q)
    estandar = p.transicion & (p.q - p.q_prev == 1)  # excluye el unico par Q1->Q3 (falta Q2)
    t = p[estandar].assign(clave=lambda d: "Q" + d.q_prev.astype(str) + "→Q" + d.q.astype(str))
    d = p[~p.transicion].assign(clave=lambda d: "Q" + d.q.astype(str))
    c = p.assign(clave=lambda d: "Q" + d.q.astype(str))
    return {
        "transiciones": _tabla(t, "clave", str),
        "dentro_cuarto": _tabla(d, "clave", str),
        "por_cuarto_jugada_nueva": _tabla(c, "clave", str),
        "excluidos": {"pares_Q1_a_Q3": int((p.transicion & (p.q - p.q_prev != 1)).sum())},
    }


def posiciones_q3() -> list[dict]:
    """Posiciones alineadas en el 3er cuarto por unidad y equipo; la moda es la de mayor conteo."""
    plays = pd.read_csv(DATA / "plays.csv", usecols=["gameId", "playId", "quarter", "possessionTeam"])
    games = pd.read_csv(DATA / "games.csv", usecols=["gameId", "homeTeamAbbr"])
    pff = pd.read_csv(DATA / "pffScoutingData.csv", usecols=["gameId", "playId", "pff_role", "pff_positionLinedUp"])
    q3 = plays[plays.quarter == 3].merge(games, on="gameId")
    q3["ataca_local"] = q3.possessionTeam == q3.homeTeamAbbr
    x = pff.merge(q3[["gameId", "playId", "ataca_local"]], on=["gameId", "playId"])
    x["ofensiva"] = x.pff_role.isin(ROLES_OFENSIVA)
    x["local"] = x.ataca_local == x.ofensiva  # local ataca y es ofensiva, o visitante ataca y es defensiva
    paneles = []
    for unidad, es_of in [("Ofensiva", True), ("Defensiva", False)]:
        for eq, es_local in [("Local", True), ("Visitante", False)]:
            g = x[(x.ofensiva == es_of) & (x.local == es_local)]
            vc = g.pff_positionLinedUp.value_counts()
            paneles.append({"unidad": unidad, "equipo": eq,
                            "jugadas": int(g.groupby(["gameId", "playId"]).ngroups),
                            "moda": vc[vc == vc.max()].index.tolist(),
                            "top": [{"posicion": k, "registros": int(v)} for k, v in vc.head(10).items()]})
    return paneles
