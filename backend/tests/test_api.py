import pytest
from fastapi.testclient import TestClient

from app.asistente import get_asistente
from app.esquemas import RespuestaAsistente
from app.main import app


class AsistenteFalso:
    def __init__(self):
        self.ultima_pregunta = None

    async def responder(self, plato, pregunta):
        self.ultima_pregunta = pregunta
        return RespuestaAsistente(respuesta=f"Sobre {plato.nombre}", fuera_de_ficha=False)

    async def traducir(self, plato, idioma):
        return plato.model_copy(update={"nombre": f"{plato.nombre} ({idioma})"})


@pytest.fixture
def cliente():
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def falso():
    asistente = AsistenteFalso()
    app.dependency_overrides[get_asistente] = lambda: asistente
    return asistente


def test_lista_platos(cliente):
    r = cliente.get("/api/platos")
    assert r.status_code == 200
    causa = next(p for p in r.json() if p["id"] == "causa-limena")
    assert causa["modelo"].endswith("paso-5.glb")


def test_detalle_con_pasos_y_modelos(cliente):
    plato = cliente.get("/api/platos/causa-limena").json()
    assert [p["numero"] for p in plato["pasos"]] == [1, 2, 3, 4, 5]
    assert all(p["modelo"].startswith("/modelos/causa-limena/") for p in plato["pasos"])


def test_plato_inexistente(cliente):
    assert cliente.get("/api/platos/ceviche-marciano").status_code == 404


def test_sin_clave_el_asistente_avisa(cliente):
    app.dependency_overrides[get_asistente] = lambda: None
    r = cliente.post("/api/asistente", json={"plato_id": "causa-limena", "pregunta": "¿Pica?"})
    assert r.status_code == 503


def test_asistente_responde(cliente, falso):
    r = cliente.post(
        "/api/asistente",
        json={"plato_id": "causa-limena", "pregunta": "¿Pica?", "idioma": "en", "paso": 2},
    )
    assert r.status_code == 200
    assert r.json()["respuesta"] == "Sobre Causa limeña"
    assert falso.ultima_pregunta.paso == 2


def test_pregunta_vacia_rechazada(cliente, falso):
    r = cliente.post("/api/asistente", json={"plato_id": "causa-limena", "pregunta": ""})
    assert r.status_code == 422


def test_traduccion(cliente, falso):
    r = cliente.get("/api/platos/causa-limena", params={"idioma": "en"})
    assert r.json()["nombre"] == "Causa limeña (en)"


def test_idioma_no_soportado(cliente, falso):
    assert cliente.get("/api/platos/causa-limena", params={"idioma": "de"}).status_code == 422
