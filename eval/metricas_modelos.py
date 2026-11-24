# /// script
# requires-python = ">=3.11"
# ///
"""Tamaño, triángulos, vértices y materiales de cada GLB generado."""

import json
import struct
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "frontend" / "public" / "modelos"


def leer_glb(ruta: Path) -> dict:
    datos = ruta.read_bytes()
    largo = struct.unpack_from("<I", datos, 12)[0]
    return json.loads(datos[20:20 + largo])


def medir(ruta: Path) -> dict:
    g = leer_glb(ruta)
    acc = g.get("accessors", [])
    tri = vert = prim = 0
    for malla in g.get("meshes", []):
        for p in malla["primitives"]:
            prim += 1
            vert += acc[p["attributes"]["POSITION"]]["count"]
            tri += acc[p["indices"]]["count"] // 3 if "indices" in p else acc[p["attributes"]["POSITION"]]["count"] // 3
    mats = g.get("materials", [])
    return {
        "archivo": f"{ruta.parent.name}/{ruta.name}",
        "kb": round(ruta.stat().st_size / 1024, 1),
        "triangulos": tri,
        "vertices": vert,
        "primitivas": prim,
        "materiales": len(mats),
        "translucidos": sum(1 for m in mats if m.get("alphaMode") == "BLEND"),
        "texturas": len(g.get("textures", [])),
        "normales": all("NORMAL" in p["attributes"] for m in g.get("meshes", []) for p in m["primitives"]),
        "color_vertice": sum(1 for m in g.get("meshes", []) for p in m["primitives"] if "COLOR_0" in p["attributes"]),
    }


def main():
    filas = [medir(r) for r in sorted(RAIZ.glob("*/paso-*.glb"))]
    json.dump(filas, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
