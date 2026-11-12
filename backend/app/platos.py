import json
from functools import lru_cache
from pathlib import Path

from .config import get_settings
from .esquemas import Plato, PlatoResumen


ORDEN = ["causa-limena", "tacacho-con-cecina", "rocoto-relleno"]


def posicion(plato_id: str) -> tuple[int, str]:
    return (ORDEN.index(plato_id) if plato_id in ORDEN else len(ORDEN), plato_id)


@lru_cache
def cargar_platos() -> dict[str, Plato]:
    carpeta: Path = get_settings().datos_dir
    platos = {}
    for archivo in carpeta.glob("*.json"):
        plato = Plato.model_validate(json.loads(archivo.read_text(encoding="utf-8")))
        platos[plato.id] = plato
    return {plato_id: platos[plato_id] for plato_id in sorted(platos, key=posicion)}


def resumen(plato: Plato) -> PlatoResumen:
    return PlatoResumen(
        id=plato.id,
        nombre=plato.nombre,
        region=plato.region,
        resumen=plato.resumen,
        modelo=plato.pasos[-1].modelo,
    )
