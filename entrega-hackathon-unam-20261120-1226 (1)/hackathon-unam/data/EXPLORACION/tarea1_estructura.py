"""TAREA 1: estructura de los 4 CSV de data/. Solo lectura, no modifica nada."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent.parent
ARCHIVOS = ["games.csv", "plays.csv", "players.csv", "pffScoutingData.csv"]

for nombre in ARCHIVOS:
    df = pd.read_csv(DATA / nombre, low_memory=False)
    print("=" * 80)
    print(f"{nombre}: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(pd.DataFrame({"dtype": df.dtypes.astype(str), "no_nulos": df.notna().sum(),
                        "nulos": df.isna().sum(), "unicos": df.nunique()}).to_string())
    print("\nPrimeras 3 filas:")
    print(df.head(3).T.to_string())
    for col in ("season", "week", "gameDate", "quarter", "down"):
        if col in df.columns:
            vals = sorted(df[col].dropna().unique().tolist())
            print(f"\n{col}: {len(vals)} valores, min={vals[0]}, max={vals[-1]}")
            if len(vals) <= 25:
                print("  ", vals)
