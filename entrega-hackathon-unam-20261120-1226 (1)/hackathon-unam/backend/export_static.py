"""Escribe las mismas metricas del API en dashboard/public/data/*.json.

Ejecutar desde la raiz del proyecto:  .venv/Scripts/python -m backend.export_static
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from backend import q3  # noqa: E402

SALIDA = RAIZ / "dashboard" / "public" / "data"


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, contenido in q3.todo().items():
        ruta = SALIDA / f"{nombre}.json"
        ruta.write_text(json.dumps(contenido, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{ruta.relative_to(RAIZ)}  {ruta.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
