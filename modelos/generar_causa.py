# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh>=4.4", "numpy>=1.26"]
# ///
"""Genera los modelos GLB de la causa limena, uno por paso de la receta.

Uso: uv run modelos/generar_causa.py
Salida: frontend/public/modelos/causa-limena/paso-N.glb
"""

from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import annulus, box, capsule, cylinder, icosphere
from trimesh.transformations import rotation_matrix, translation_matrix
from trimesh.visual.material import PBRMaterial

SALIDA = Path(__file__).resolve().parent.parent / "frontend/public/modelos/causa-limena"
rng = np.random.default_rng(7)

# colores rgb 0-1, rugosidad, metalico
LOZA = ((0.96, 0.95, 0.92), 0.35, 0.0)
MADERA = ((0.62, 0.43, 0.26), 0.8, 0.0)
PAPA = ((0.93, 0.80, 0.38), 0.75, 0.0)
MASA = ((0.99, 0.80, 0.22), 0.6, 0.0)
LIMON_CASCARA = ((0.42, 0.66, 0.18), 0.5, 0.0)
LIMON_PULPA = ((0.80, 0.90, 0.45), 0.4, 0.0)
AJI = ((0.98, 0.62, 0.10), 0.35, 0.0)
TALLO = ((0.30, 0.50, 0.15), 0.7, 0.0)
ACRILICO = ((0.92, 0.95, 0.97), 0.1, 0.0)
PALTA = ((0.56, 0.73, 0.26), 0.5, 0.0)
POLLO = ((0.96, 0.91, 0.76), 0.7, 0.0)
HEBRA = ((0.90, 0.80, 0.60), 0.8, 0.0)
CLARA = ((0.98, 0.98, 0.96), 0.4, 0.0)
YEMA = ((0.98, 0.72, 0.12), 0.5, 0.0)
ACEITUNA = ((0.22, 0.09, 0.16), 0.3, 0.0)
PEREJIL = ((0.20, 0.55, 0.18), 0.7, 0.0)

# el modelo se arma con z hacia arriba y se rota al final porque gltf usa y arriba
Z_A_Y = rotation_matrix(-np.pi / 2, [1, 0, 0])


def pintar(malla, material, opacidad=1.0):
    color, rugosidad, metalico = material
    malla.visual = trimesh.visual.TextureVisuals(
        material=PBRMaterial(
            baseColorFactor=[int(c * 255) for c in color] + [int(opacidad * 255)],
            roughnessFactor=rugosidad,
            metallicFactor=metalico,
            alphaMode="BLEND" if opacidad < 1 else "OPAQUE",
            doubleSided=opacidad < 1,
        )
    )
    return malla


def mover(malla, x=0.0, y=0.0, z=0.0):
    malla.apply_transform(translation_matrix([x, y, z]))
    return malla


def girar(malla, angulo, eje):
    malla.apply_transform(rotation_matrix(angulo, eje))
    return malla


def disco(radio, alto, z=0.0, secciones=64):
    # cilindro apoyado sobre z
    return mover(cylinder(radius=radio, height=alto, sections=secciones), z=z + alto / 2)


def plato():
    base = disco(0.10, 0.008)
    borde = mover(annulus(r_min=0.10, r_max=0.13, height=0.014, sections=64), z=0.007)
    return [pintar(base, LOZA), pintar(borde, LOZA)]


def tabla():
    return [pintar(mover(box([0.32, 0.22, 0.018]), z=0.009), MADERA)]


def papa(x, y, z, escala=1.0):
    malla = icosphere(subdivisions=3, radius=1.0)
    malla.apply_scale([0.034 * escala, 0.024 * escala, 0.021 * escala])
    girar(malla, rng.uniform(0, np.pi), [0, 0, 1])
    return pintar(mover(malla, x, y, z), PAPA)


def medio_limon(x, y, z):
    cascara = mover(disco(0.022, 0.012, z), x, y)
    pulpa = mover(disco(0.019, 0.0015, z + 0.012), x, y)
    return [pintar(cascara, LIMON_CASCARA), pintar(pulpa, LIMON_PULPA)]


def aji(x, y, z, angulo):
    cuerpo = capsule(height=0.075, radius=0.012, count=[24, 12])
    cuerpo.apply_scale([1.0, 0.85, 1.0])
    girar(cuerpo, np.pi / 2, [0, 1, 0])
    tallo = girar(cylinder(radius=0.003, height=0.014), np.pi / 2, [0, 1, 0])
    mover(tallo, x=0.05)
    partes = [pintar(cuerpo, AJI), pintar(tallo, TALLO)]
    for parte in partes:
        girar(parte, angulo, [0, 0, 1])
        mover(parte, x, y, z + 0.012)
    return partes


def bol():
    pared = mover(annulus(r_min=0.072, r_max=0.078, height=0.05, sections=64), z=0.025 + 0.018)
    fondo = disco(0.078, 0.006, 0.018)
    return [pintar(pared, LOZA), pintar(fondo, LOZA)]


def aro(alto):
    return pintar(mover(annulus(r_min=0.040, r_max=0.042, height=alto, sections=64), z=0.008 + alto / 2), ACRILICO, 0.28)


def capa(z, alto, material, radio=0.0395):
    return pintar(disco(radio, alto, z), material)


def hebras_pollo(z, cantidad=40):
    hebras = []
    for _ in range(cantidad):
        r = 0.034 * np.sqrt(rng.uniform())
        t = rng.uniform(0, 2 * np.pi)
        hebra = box([rng.uniform(0.008, 0.014), 0.003, 0.003])
        girar(hebra, rng.uniform(0, np.pi), [0, 0, 1])
        hebras.append(pintar(mover(hebra, r * np.cos(t), r * np.sin(t), z + 0.0015), HEBRA))
    return hebras


def huevo(x, y, z, angulo):
    clara = girar(disco(0.013, 0.004, 0.0), np.pi / 2.6, [1, 0, 0])
    yema = girar(disco(0.007, 0.0045, 0.0), np.pi / 2.6, [1, 0, 0])
    partes = [pintar(clara, CLARA), pintar(yema, YEMA)]
    for parte in partes:
        girar(parte, angulo, [0, 0, 1])
        mover(parte, x, y, z + 0.008)
    return partes


def aceituna(x, y, z):
    malla = icosphere(subdivisions=3, radius=1.0)
    malla.apply_scale([0.011, 0.008, 0.008])
    return pintar(mover(malla, x, y, z + 0.007), ACEITUNA)


def perejil(x, y, z):
    hojas = []
    for _ in range(5):
        hoja = icosphere(subdivisions=1, radius=0.0035)
        hojas.append(pintar(mover(hoja, x + rng.uniform(-0.005, 0.005), y + rng.uniform(-0.005, 0.005), z + 0.003), PEREJIL))
    return hojas


def paso_1():
    partes = tabla()
    for x, y in [(-0.07, -0.03), (-0.02, 0.04), (0.03, -0.02), (0.08, 0.04), (0.09, -0.05)]:
        partes.append(papa(x, y, 0.018 + 0.021, rng.uniform(0.85, 1.1)))
    return partes


def paso_2():
    partes = tabla() + bol()
    masa = icosphere(subdivisions=4, radius=1.0)
    masa.apply_scale([0.070, 0.070, 0.030])
    partes.append(pintar(mover(masa, z=0.032), MASA))
    partes += medio_limon(0.115, -0.06, 0.018)
    partes += medio_limon(0.12, 0.0, 0.018)
    partes += aji(0.11, 0.07, 0.018, 0.3)
    return partes


def paso_3():
    partes = plato()
    partes.append(capa(0.008, 0.022, MASA))
    partes.append(aro(0.075))
    return partes


def paso_4():
    partes = plato()
    partes.append(capa(0.008, 0.022, MASA))
    partes.append(capa(0.030, 0.010, PALTA))
    partes.append(capa(0.040, 0.015, POLLO))
    partes += hebras_pollo(0.055)
    partes.append(aro(0.075))
    return partes


def paso_5():
    partes = plato()
    partes.append(capa(0.008, 0.022, MASA))
    partes.append(capa(0.030, 0.010, PALTA))
    partes.append(capa(0.040, 0.015, POLLO))
    partes.append(capa(0.055, 0.022, MASA))
    tope = 0.077
    partes += huevo(-0.012, 0.004, tope, 0.4)
    partes += huevo(0.012, -0.006, tope, -0.5)
    partes.append(aceituna(0.004, 0.018, tope))
    partes += perejil(-0.015, -0.018, tope)
    return partes


def exportar(nombre, partes):
    escena = trimesh.Scene()
    for i, parte in enumerate(partes):
        parte.apply_transform(Z_A_Y)
        escena.add_geometry(parte, node_name=f"{nombre}-{i}")
    destino = SALIDA / f"{nombre}.glb"
    escena.export(destino)
    print(f"{destino.name}: {destino.stat().st_size / 1024:.0f} KB, {len(partes)} piezas")


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for numero, paso in enumerate([paso_1, paso_2, paso_3, paso_4, paso_5], start=1):
        exportar(f"paso-{numero}", paso())


if __name__ == "__main__":
    main()
