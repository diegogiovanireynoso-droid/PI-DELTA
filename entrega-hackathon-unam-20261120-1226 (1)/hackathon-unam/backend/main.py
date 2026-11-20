"""API de la app. Ejecuta: .venv/bin/uvicorn backend.main:app --reload"""
from fastapi import FastAPI, HTTPException

from backend import exploracion, q3

app = FastAPI(title="Hackathon NFL UNAM")

# Nombre del recurso -> ruta del API. El dashboard usa los mismos nombres para los JSON estaticos.
RUTAS = {
    "meta": "/api/q3/meta",
    "yardas_por_partido": "/api/q3/yardas/partido",
    "yardas_por_temporada": "/api/q3/yardas/temporada",
    "cambios_por_partido": "/api/q3/cambios/partido",
    "cambios_por_temporada": "/api/q3/cambios/temporada",
}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _registrar(nombre: str, ruta: str) -> None:
    def endpoint():
        datos = q3.todo().get(nombre)
        if datos is None:
            raise HTTPException(status_code=404, detail="recurso no encontrado")
        return datos
    app.add_api_route(ruta, endpoint, methods=["GET"], name=nombre)


for _nombre, _ruta in RUTAS.items():
    _registrar(_nombre, _ruta)


@app.get("/api/exploracion/cambios")
def cambios_exploracion() -> dict:
    """Resultado de la exploracion: jugadores que entran por cuarto y posiciones del Q3."""
    return {**exploracion.resumen_cambios(), "posiciones_q3": exploracion.posiciones_q3()}
