import asyncio
import logging
import time
from types import SimpleNamespace

import httpx2
import pytest
from google.genai import errors

from app.asistente import Asistente
from app.config import Settings
from app.esquemas import PreguntaAsistente
from app.platos import cargar_platos

PLATO = cargar_platos()["causa-limena"]
RESPUESTA = '{"respuesta": "ok", "fuera_de_ficha": false}'


def preparar(comportamiento, espera=0.2, traducir=0.2, total=2.0):
    ajustes = Settings(
        gemini_api_key="x",
        gemini_model="a",
        gemini_fallback_models=",".join(m for m in comportamiento if m != "a"),
        gemini_timeout_s=espera,
        gemini_timeout_traducir_s=traducir,
        gemini_timeout_total_s=total,
    )
    asistente = Asistente(ajustes)
    llamados = []

    async def generar(model, contents, config):
        llamados.append(model)
        paso = comportamiento[model]
        if isinstance(paso, tuple):
            await asyncio.sleep(paso[0])
            paso = paso[1]
        if paso == "colgar":
            await asyncio.sleep(10)
        if paso == "sin red":
            raise httpx2.ConnectError("x")
        if isinstance(paso, int):
            raise errors.APIError(paso, {"error": {"message": "x"}})
        return SimpleNamespace(text=paso)

    asistente._cliente = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generar)))
    return asistente, llamados


def responder(asistente):
    pregunta = PreguntaAsistente(plato_id=PLATO.id, pregunta="¿Pica?")
    return asyncio.run(asistente.responder(PLATO, pregunta))


@pytest.mark.parametrize("fallo", [404, 429, 500, 503, "colgar", "sin red", "{no es json", "", None])
def test_usa_el_respaldo(fallo):
    asistente, llamados = preparar({"a": fallo, "b": RESPUESTA})
    assert responder(asistente).respuesta == "ok"
    assert llamados == ["a", "b"]


@pytest.mark.parametrize("codigo", [400, 401, 403])
def test_clave_mala_no_usa_respaldo(codigo):
    asistente, llamados = preparar({"a": codigo, "b": RESPUESTA})
    with pytest.raises(errors.APIError):
        responder(asistente)
    assert llamados == ["a"]


def test_fallan_todos_devuelve_el_ultimo_error():
    asistente, llamados = preparar({"a": 503, "b": 429, "c": "colgar"}, total=0.6)
    with pytest.raises(TimeoutError):
        responder(asistente)
    assert llamados == ["a", "b", "c"]


def test_registra_el_modelo_que_fallo(caplog):
    asistente, _ = preparar({"a": 503, "b": RESPUESTA})
    with caplog.at_level(logging.WARNING, logger="uvicorn.error"):
        responder(asistente)
    assert "Gemini a falló (503)" in caplog.text


def test_el_ultimo_modelo_usa_el_tiempo_restante():
    asistente, llamados = preparar({"a": "colgar", "b": (0.5, RESPUESTA)}, espera=0.1, total=1.0)
    assert responder(asistente).respuesta == "ok"
    assert llamados == ["a", "b"]


def test_no_pasa_del_tope_total():
    asistente, llamados = preparar({"a": "colgar", "b": "colgar", "c": "colgar"}, espera=0.3, total=0.5)
    inicio = time.monotonic()
    with pytest.raises(TimeoutError):
        responder(asistente)
    assert time.monotonic() - inicio < 0.7
    assert llamados == ["a", "b"]


def test_traducir_espera_mas_que_responder():
    comportamiento = {"a": (0.3, PLATO.model_dump_json()), "b": RESPUESTA}
    asistente, llamados = preparar(comportamiento, espera=0.1, traducir=0.6)
    traducido = asyncio.run(asistente.traducir(PLATO, "en"))
    assert traducido.id == PLATO.id and llamados == ["a"]


def test_traduccion_invalida_usa_el_respaldo():
    asistente, llamados = preparar({"a": RESPUESTA, "b": PLATO.model_dump_json()})
    traducido = asyncio.run(asistente.traducir(PLATO, "fr"))
    assert [p.modelo for p in traducido.pasos] == [p.modelo for p in PLATO.pasos]
    assert llamados == ["a", "b"]
