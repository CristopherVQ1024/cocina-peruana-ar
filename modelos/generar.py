# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh>=4.4", "numpy>=1.26", "pillow>=10", "scipy>=1.11"]
# ///
"""Genera los modelos GLB de los platos, uno por paso de la receta.

Uso: uv run modelos/generar.py            todos los platos
     uv run modelos/generar.py rocoto     solo los que contengan ese texto
Salida: frontend/public/modelos/<plato>/paso-N.glb
"""

import sys

import causa
import rocoto
import tacacho
from base import exportar

PLATOS = [causa, tacacho, rocoto]


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    for plato in PLATOS:
        if filtro not in plato.ID:
            continue
        for numero, paso in enumerate(plato.PASOS, start=1):
            exportar(plato.ID, numero, paso())


if __name__ == "__main__":
    main()
