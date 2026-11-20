"""Analisis de plays.csv. Solo lectura: no modifica ningun archivo de data/."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent
plays = pd.read_csv(DATA / "plays.csv", low_memory=False)
games = pd.read_csv(DATA / "games.csv")

print("=" * 80)
print("SUBTAREA 1: tipo, nulos y unicos por columna de plays.csv")
numericas = plays.select_dtypes(include="number").columns
tabla = pd.DataFrame({
    "tipo": ["numerica" if c in numericas else "no numerica" for c in plays.columns],
    "dtype": plays.dtypes.astype(str).values,
    "nulos": plays.isna().sum().values,
    "pct_nulos": (plays.isna().mean() * 100).round(2).values,
    "unicos": plays.nunique().values,
}, index=plays.columns)
print(tabla.to_string())
print(f"\nNumericas: {len(numericas)} | No numericas: {plays.shape[1] - len(numericas)}")
print("Numericas que son identificadores/codigos:", ["gameId", "playId", "foulNFLId1", "foulNFLId2", "foulNFLId3"])

print("\n" + "=" * 80)
print("PREGUNTA 1: filas por gameId y repeticion de playId")
filas = plays.groupby("gameId").size()
print(filas.describe().round(2).to_string())
print("\nCantidades distintas de filas por gameId:", filas.nunique())
print("Min:", filas.min(), "(gameId", filas.idxmin(), ") Max:", filas.max(), "(gameId", filas.idxmax(), ")")
print("Partidos en games.csv:", games.gameId.nunique(), "| con jugadas en plays:", filas.shape[0])

print("\nplayId unicos:", plays.playId.nunique(), "de", len(plays), "filas")
print("playId repetidos entre filas (global):", int(plays.playId.duplicated(keep=False).sum()), "filas afectadas")
print("Pares (gameId, playId) duplicados:", int(plays.duplicated(["gameId", "playId"]).sum()))
rep = plays.groupby("playId")["gameId"].nunique()
print("playId que aparece en mas de un partido:", int((rep > 1).sum()), "| max partidos por un mismo playId:", int(rep.max()))
dentro = plays.groupby("gameId")["playId"].apply(lambda s: s.duplicated().sum())
print("playId repetidos dentro de un mismo partido:", int(dentro.sum()))

print("\n" + "=" * 80)
print("PREGUNTA 2: jugadas y yardas por quarter, y local/visitante")
m = plays.merge(games[["gameId", "homeTeamAbbr", "visitorTeamAbbr"]], on="gameId", how="left")
print("Jugadas sin partido en games:", int(m.homeTeamAbbr.isna().sum()))
m["lado"] = (m.possessionTeam == m.homeTeamAbbr).map({True: "Home", False: "Visitor"})
print("Jugadas donde la posesion no es ni local ni visitante:",
      int((~m.possessionTeam.isin([]) & (m.possessionTeam != m.homeTeamAbbr) & (m.possessionTeam != m.visitorTeamAbbr)).sum()))

q = m.groupby("quarter").agg(jugadas=("playId", "size"), yardas_playResult=("playResult", "sum"),
                             prom_yardas=("playResult", "mean"), mediana_yardas=("playResult", "median"))
q["prom_yardas"] = q.prom_yardas.round(3)
print(q.to_string())
print("Quarter con mas jugadas:", q.jugadas.idxmax(), "| con mas yardas totales:", q.yardas_playResult.idxmax(),
      "| con mayor promedio por jugada:", q.prom_yardas.idxmax())

h = m.pivot_table(index="quarter", columns="lado", values="playResult", aggfunc=["size", "sum", "mean"]).round(3)
print("\nPor quarter y lado (size=jugadas, sum=yardas, mean=yardas/jugada):")
print(h.to_string())
print("\nLado con mas yardas totales por quarter:")
print(h["sum"].idxmax(axis=1).to_string())
print("\nLado con mejor promedio por jugada por quarter:")
print(h["mean"].idxmax(axis=1).to_string())
print("\nTotal por lado:")
print(m.groupby("lado").playResult.agg(["size", "sum", "mean"]).round(3).to_string())
