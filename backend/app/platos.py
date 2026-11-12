import json
from functools import lru_cache
from pathlib import Path

from .config import get_settings
from .esquemas import Plato, PlatoResumen


@lru_cache
def cargar_platos() -> dict[str, Plato]:
    carpeta: Path = get_settings().datos_dir
    platos = {}
    for archivo in sorted(carpeta.glob("*.json")):
        plato = Plato.model_validate(json.loads(archivo.read_text(encoding="utf-8")))
        platos[plato.id] = plato
    return platos


def resumen(plato: Plato) -> PlatoResumen:
    return PlatoResumen(
        id=plato.id,
        nombre=plato.nombre,
        region=plato.region,
        resumen=plato.resumen,
        modelo=plato.pasos[-1].modelo,
    )
