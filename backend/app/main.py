import logging

from fastapi import Depends, FastAPI, HTTPException

from .asistente import Asistente, get_asistente
from .esquemas import Idioma, Plato, PlatoResumen, PreguntaAsistente, RespuestaAsistente
from .platos import cargar_platos, resumen

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="Cocina peruana AR")


def buscar_plato(plato_id: str) -> Plato:
    plato = cargar_platos().get(plato_id)
    if plato is None:
        raise HTTPException(404, "Plato no encontrado")
    return plato


def asistente_requerido(asistente: Asistente | None = Depends(get_asistente)) -> Asistente:
    if asistente is None:
        raise HTTPException(503, "El asistente no está configurado, falta GEMINI_API_KEY")
    return asistente


@app.get("/api/salud")
def salud():
    return {"ok": True, "platos": len(cargar_platos())}


@app.get("/api/platos", response_model=list[PlatoResumen])
def listar_platos():
    return [resumen(plato) for plato in cargar_platos().values()]


@app.get("/api/platos/{plato_id}", response_model=Plato)
async def obtener_plato(
    plato_id: str,
    idioma: Idioma = "es",
    asistente: Asistente | None = Depends(get_asistente),
):
    plato = buscar_plato(plato_id)
    if idioma == "es":
        return plato
    if asistente is None:
        raise HTTPException(503, "La traducción no está disponible, falta GEMINI_API_KEY")
    try:
        return await asistente.traducir(plato, idioma)
    except Exception:
        log.exception("Error al traducir %s a %s", plato_id, idioma)
        raise HTTPException(502, "No se pudo traducir la ficha, intenta de nuevo")


@app.post("/api/asistente", response_model=RespuestaAsistente)
async def preguntar(pregunta: PreguntaAsistente, asistente: Asistente = Depends(asistente_requerido)):
    plato = buscar_plato(pregunta.plato_id)
    try:
        return await asistente.responder(plato, pregunta)
    except Exception:
        log.exception("Error del asistente con %s", pregunta.plato_id)
        raise HTTPException(502, "El asistente no respondió, intenta de nuevo")
