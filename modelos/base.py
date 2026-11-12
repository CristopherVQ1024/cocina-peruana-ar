"""Piezas y utilidades comunes para los modelos de los platos.

Todo se arma en metros, con z hacia arriba y la base en z = 0.
"""

import io
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from trimesh.creation import icosphere, revolve
from trimesh.transformations import rotation_matrix, translation_matrix
from trimesh.visual.material import PBRMaterial

SALIDA = Path(__file__).resolve().parent.parent / "frontend/public/modelos"

# gltf usa y hacia arriba
Z_A_Y = rotation_matrix(-np.pi / 2, [1, 0, 0])

ALTURA_PLATO = 0.006
ALTURA_TABLA = 0.018
ALTURA_SARTEN = 0.004


@dataclass(frozen=True)
class Material:
    color: tuple[float, float, float]
    rugosidad: float = 0.6
    metalico: float = 0.0
    opacidad: float = 1.0


LOZA = Material((0.95, 0.94, 0.90), 0.22)
MADERA_CLARA = (0.78, 0.60, 0.40)
MADERA_OSCURA = (0.52, 0.35, 0.20)
MADERA = Material(MADERA_CLARA, 0.75)
ALUMINIO = Material((0.80, 0.81, 0.82), 0.32, 1.0)
HIERRO = Material((0.16, 0.16, 0.17), 0.45, 0.4)
MANGO = Material((0.09, 0.09, 0.09), 0.7)
AGUA = Material((0.74, 0.86, 0.92), 0.05, 0.0, 0.5)
CLARA = Material((0.97, 0.97, 0.94), 0.4)
YEMA = Material((0.96, 0.70, 0.12), 0.55)
ACEITUNA = Material((0.20, 0.09, 0.15), 0.22)
TALLO = Material((0.30, 0.45, 0.15), 0.7)


# color y materiales

def lineal(color):
    return np.clip(np.asarray(color, dtype=float), 0, 1) ** 2.2


def pintar(malla, material, colores=None, textura=None, uv=None):
    # colores es un arreglo rgb por vertice en srgb 0 a 1
    base = np.ones(3) if colores is not None or textura is not None else lineal(material.color)
    traslucido = material.opacidad < 1
    pbr = PBRMaterial(
        baseColorFactor=[int(round(c * 255)) for c in base] + [int(round(material.opacidad * 255))],
        baseColorTexture=textura,
        roughnessFactor=material.rugosidad,
        metallicFactor=material.metalico,
        alphaMode="BLEND" if traslucido else "OPAQUE",
        doubleSided=traslucido,
    )
    malla.visual = trimesh.visual.TextureVisuals(uv=uv, material=pbr)
    if colores is not None:
        rgba = np.column_stack([lineal(colores) * 255, np.full(len(colores), 255)])
        malla.visual.vertex_attributes["color"] = np.round(rgba).astype(np.uint8)
    return malla


def ruido(puntos, tamano, semilla=0, octavas=3):
    # ruido suave entre -1 y 1, tamano es el ancho de las manchas en metros
    rng = np.random.default_rng(semilla)
    total = np.zeros(len(puntos))
    peso, suma = 1.0, 0.0
    for octava in range(octavas):
        direcciones = rng.normal(size=(5, 3))
        direcciones /= np.linalg.norm(direcciones, axis=1, keepdims=True)
        fases = rng.uniform(0, 2 * np.pi, 5)
        frecuencia = 2 * np.pi / tamano * 2**octava
        total += peso * np.sin(puntos @ direcciones.T * frecuencia + fases).mean(axis=1)
        suma += peso
        peso *= 0.5
    return np.clip(total / suma * 2, -1, 1)


def escalon(valor, desde, hasta):
    t = np.clip((np.asarray(valor, dtype=float) - desde) / (hasta - desde), 0, 1)
    return t * t * (3 - 2 * t)


def mezcla(a, b, peso):
    peso = np.clip(np.asarray(peso, dtype=float), 0, 1)[:, None]
    return np.asarray(a, dtype=float) * (1 - peso) + np.asarray(b, dtype=float) * peso


def motas(malla, base, mota, tamano, umbral=0.45, semilla=0):
    valor = ruido(malla.vertices, tamano, semilla)
    return mezcla(base, mota, escalon(valor, umbral, umbral + 0.2))


def relieve(malla, amplitud, tamano, semilla=0):
    normales = malla.vertex_normals.copy()
    malla.vertices = malla.vertices + normales * (ruido(malla.vertices, tamano, semilla) * amplitud)[:, None]
    return malla


# transformaciones, aceptan una malla o una lista

def mover(piezas, x=0.0, y=0.0, z=0.0):
    for pieza in piezas if isinstance(piezas, list) else [piezas]:
        pieza.apply_transform(translation_matrix([x, y, z]))
    return piezas


def girar(piezas, angulo, eje=(0, 0, 1), centro=(0, 0, 0)):
    for pieza in piezas if isinstance(piezas, list) else [piezas]:
        pieza.apply_transform(rotation_matrix(angulo, eje, centro))
    return piezas


# geometria

def curva(control, n=24):
    # curva suave que pasa por los puntos de control
    p = np.asarray(control, dtype=float)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    tramos = len(p) - 3
    puntos = []
    for u in np.linspace(0, tramos, n):
        i = min(int(u), tramos - 1)
        t = u - i
        a, b, c, d = p[i : i + 4]
        puntos.append(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t**2 + (3 * b - a - 3 * c + d) * t**3))
    return np.array(puntos)


def redondear(perfil, radio, pasos=4):
    p = np.asarray(perfil, dtype=float)
    salida = [p[0]]
    for a, b, c in zip(p[:-2], p[1:-1], p[2:]):
        u, w = a - b, c - b
        lu, lw = np.linalg.norm(u), np.linalg.norm(w)
        if lu < 1e-9 or lw < 1e-9 or np.dot(u, w) / (lu * lw) < -0.94:
            salida.append(b)
            continue
        inicio = b + u / lu * min(radio, lu / 2)
        fin = b + w / lw * min(radio, lw / 2)
        for t in np.linspace(0, 1, pasos + 1):
            salida.append((1 - t) ** 2 * inicio + 2 * t * (1 - t) * b + t**2 * fin)
    salida.append(p[-1])
    return np.array(salida)


def densificar(perfil, paso):
    p = np.asarray(perfil, dtype=float)
    salida = [p[0]]
    for a, b in zip(p[:-1], p[1:]):
        partes = max(1, int(np.ceil(np.linalg.norm(b - a) / paso)))
        salida += [a + (b - a) * k / partes for k in range(1, partes + 1)]
    return np.array(salida)


def torno(perfil, secciones=64, paso=None):
    # solido de revolucion, el perfil es una lista de radio y altura
    perfil = np.asarray(perfil, dtype=float)
    if paso:
        perfil = densificar(perfil, paso)
    perfil[1:-1, 0] = np.maximum(perfil[1:-1, 0], 1e-4)
    malla = revolve(perfil, sections=secciones)
    malla.merge_vertices()
    malla.update_faces(malla.nondegenerate_faces())
    malla.remove_unreferenced_vertices()
    if malla.volume < 0:
        malla.invert()
    return malla


def disco(radio, alto, z=0.0, bisel=0.0015, paso=None, secciones=64):
    bisel = min(bisel, alto / 2)
    perfil = redondear([(0, 0), (radio, 0), (radio, alto), (0, alto)], bisel)
    return mover(torno(perfil, secciones, paso), z=z)


def anillo(radio_interior, radio_exterior, alto, z=0.0, secciones=64):
    perfil = [
        (radio_interior, 0),
        (radio_exterior, 0),
        (radio_exterior, alto),
        (radio_interior, alto),
        (radio_interior, 0),
    ]
    return mover(torno(perfil, secciones), z=z)


def organico(radios, bulto=0.0, tamano=0.02, semilla=0, subdivisiones=3):
    malla = icosphere(subdivisions=subdivisiones, radius=1.0)
    direcciones = malla.vertices.copy()
    vertices = direcciones * np.asarray(radios, dtype=float)
    if bulto:
        vertices += direcciones * (ruido(vertices, tamano, semilla) * bulto)[:, None]
    malla.vertices = vertices
    return malla


def husillo(n, radio, punta_inicio=0.15, punta_fin=0.15):
    # radios de un tubo con las puntas redondeadas
    t = np.linspace(0, 1, n)
    factor = np.ones(n)
    if punta_inicio:
        factor = np.where(t < punta_inicio, np.sqrt(np.clip(1 - (1 - t / punta_inicio) ** 2, 0, 1)), factor)
    if punta_fin:
        factor = np.where(t > 1 - punta_fin, np.sqrt(np.clip(1 - (1 - (1 - t) / punta_fin) ** 2, 0, 1)), factor)
    return radio * np.maximum(factor, 0.03)


def tubo(puntos, radios, lados=16, ancho=1.0, seccion=None):
    # barre una seccion a lo largo de una curva, ancho aplasta la seccion
    puntos = np.asarray(puntos, dtype=float)
    n = len(puntos)
    radios = np.broadcast_to(np.asarray(radios, dtype=float), (n,))
    tangentes = np.gradient(puntos, axis=0)
    tangentes /= np.linalg.norm(tangentes, axis=1, keepdims=True)
    lado = np.cross([0, 0, 1], tangentes[0])
    if np.linalg.norm(lado) < 1e-6:
        lado = np.array([1.0, 0.0, 0.0])
    angulos = np.linspace(0, 2 * np.pi, lados, endpoint=False)
    factor = seccion(angulos) if seccion else np.ones(lados)
    anillos = []
    for punto, tangente, radio in zip(puntos, tangentes, radios):
        lado = lado - np.dot(lado, tangente) * tangente
        lado /= np.linalg.norm(lado)
        arriba = np.cross(tangente, lado)
        contorno = np.outer(np.cos(angulos) * factor * ancho, lado) + np.outer(np.sin(angulos) * factor, arriba)
        anillos.append(punto + contorno * radio)
    vertices = np.vstack(anillos + [puntos[:1], puntos[-1:]])
    caras = []
    for i in range(n - 1):
        for j in range(lados):
            a, b = i * lados + j, i * lados + (j + 1) % lados
            c, d = a + lados, b + lados
            caras += [[a, b, c], [b, d, c]]
    inicio, fin, ultimo = n * lados, n * lados + 1, (n - 1) * lados
    for j in range(lados):
        k = (j + 1) % lados
        caras += [[inicio, k, j], [fin, ultimo + j, ultimo + k]]
    malla = trimesh.Trimesh(vertices, caras, process=False)
    if malla.volume < 0:
        malla.invert()
    # posicion de cada vertice a lo largo del tubo, de 0 a 1
    malla.metadata["t"] = np.concatenate([np.repeat(np.linspace(0, 1, n), lados), [0.0, 1.0]])
    return malla


def rectangulo(ancho, fondo, radio, n=8):
    contorno = []
    esquinas = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for k, (sx, sy) in enumerate(esquinas):
        centro = np.array([sx * (ancho / 2 - radio), sy * (fondo / 2 - radio)])
        for angulo in np.linspace(k * np.pi / 2, (k + 1) * np.pi / 2, n):
            contorno.append(centro + radio * np.array([np.cos(angulo), np.sin(angulo)]))
    return np.array(contorno)


def extruir(contorno, alto, bisel=0.002, niveles=1, anillos=1):
    # levanta un contorno plano con los bordes biselados
    contorno = np.asarray(contorno, dtype=float)
    n = len(contorno)
    centro = contorno.mean(axis=0)
    direccion = contorno - centro
    interior = contorno - direccion / np.linalg.norm(direccion, axis=1, keepdims=True) * bisel
    escalas = np.linspace(0, 1, anillos + 1)[1:]
    capas = [(centro + (interior - centro) * e, 0.0) for e in escalas]
    capas += [(contorno, z) for z in np.linspace(bisel, alto - bisel, niveles + 1)]
    capas += [(centro + (interior - centro) * e, alto) for e in escalas[::-1]]
    vertices = [np.column_stack([xy, np.full(n, z)]) for xy, z in capas]
    vertices += [[[*centro, 0.0]], [[*centro, alto]]]
    caras = []
    for i in range(len(capas) - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = a + n, b + n
            caras += [[a, b, c], [b, d, c]]
    base, tope, ultimo = len(capas) * n, len(capas) * n + 1, (len(capas) - 1) * n
    for j in range(n):
        k = (j + 1) % n
        caras += [[base, k, j], [tope, ultimo + j, ultimo + k]]
    malla = trimesh.Trimesh(np.vstack(vertices), caras, process=False)
    if malla.volume < 0:
        malla.invert()
    return malla


# menaje

@lru_cache
def textura_madera():
    alto, ancho = 256, 512
    y, x = np.mgrid[0:alto, 0:ancho] / 256
    plano = np.column_stack([x.ravel() * 0.12, y.ravel(), np.zeros(x.size)])
    onda = ruido(plano, 0.5, 3)
    fino = ruido(plano * [0.4, 6, 1], 0.2, 5)
    veta = (np.sin((plano[:, 1] * 11 + onda * 1.6) * 2 * np.pi) * 0.5 + 0.5) ** 2
    color = mezcla(MADERA_CLARA, MADERA_OSCURA, veta * 0.55 + fino * 0.15 + 0.1)
    imagen = Image.fromarray((color.reshape(alto, ancho, 3) * 255).astype(np.uint8))
    memoria = io.BytesIO()
    imagen.save(memoria, format="JPEG", quality=82)
    memoria.seek(0)
    return Image.open(memoria)


def tabla(ancho=0.34, fondo=0.24):
    malla = extruir(rectangulo(ancho, fondo, 0.02), ALTURA_TABLA, bisel=0.003, anillos=2)
    uv = np.column_stack([malla.vertices[:, 0] / ancho + 0.5, malla.vertices[:, 1] / (ancho / 2) + 0.5])
    return [pintar(malla, MADERA, textura=textura_madera(), uv=uv)]


def plato(radio=0.13):
    perfil = [
        (0, 0),
        (0.55 * radio, 0),
        (radio, 0.016),
        (radio, 0.019),
        (0.70 * radio, 0.0085),
        (0.62 * radio, ALTURA_PLATO),
        (0, ALTURA_PLATO),
    ]
    return [pintar(torno(redondear(perfil, 0.003), 96), LOZA)]


def bol(radio=0.08, alto=0.055, grosor=0.004, material=LOZA):
    # el fondo interior queda a grosor por 1.5
    tramos = np.linspace(0, 1, 10)
    pared = [(radio * (0.5 + 0.5 * np.sqrt(1 - (1 - s) ** 2)), alto * s) for s in tramos]
    piso = grosor * 1.5
    interior = [(r - grosor, z) for r, z in reversed(pared) if z > piso + 0.004]
    perfil = [(0, 0)] + pared + interior + [(interior[-1][0] - 0.004, piso), (0, piso)]
    return [pintar(torno(redondear(perfil, 0.002), 64), material)]


def olla(radio=0.085, alto=0.09):
    grosor = 0.003
    perfil = [
        (0, 0),
        (radio, 0),
        (radio, alto),
        (radio + 0.004, alto + 0.002),
        (radio - grosor, alto),
        (radio - grosor, grosor),
        (0, grosor),
    ]
    piezas = [torno(redondear(perfil, 0.006), 64)]
    for lado in (1, -1):
        asa = curva(
            [
                (-0.026, lado * (radio - 0.003), alto * 0.78),
                (-0.02, lado * (radio + 0.022), alto * 0.8),
                (0.02, lado * (radio + 0.022), alto * 0.8),
                (0.026, lado * (radio - 0.003), alto * 0.78),
            ],
            16,
        )
        piezas.append(tubo(asa, 0.004, lados=10))
    return [pintar(pieza, ALUMINIO) for pieza in piezas]


def agua(radio, z):
    return [pintar(disco(radio, 0.002, z, bisel=0.0005), AGUA)]


def sarten(radio=0.12):
    perfil = [
        (0, 0),
        (0.84 * radio, 0),
        (radio, 0.034),
        (radio + 0.003, 0.036),
        (radio - 0.004, 0.035),
        (0.84 * radio - 0.003, ALTURA_SARTEN),
        (0, ALTURA_SARTEN),
    ]
    cuerpo = pintar(torno(redondear(perfil, 0.004), 96), HIERRO)
    recorrido = curva([(radio - 0.004, 0, 0.03), (radio + 0.05, 0, 0.04), (radio + 0.17, 0, 0.046)], 16)
    mango = pintar(tubo(recorrido, husillo(16, 0.009, 0.0, 0.05), lados=14, ancho=1.4), MANGO)
    return [cuerpo, mango]


def rodaja_huevo(x=0.0, y=0.0, z=0.0, angulo=0.0, inclinacion=0.0):
    clara = disco(0.015, 0.004, bisel=0.0012, secciones=40)
    clara.apply_scale([1.15, 1.0, 1.0])
    yema = disco(0.0078, 0.0046, bisel=0.001, secciones=32)
    piezas = [pintar(clara, CLARA), pintar(yema, YEMA)]
    girar(piezas, inclinacion, (0, 1, 0))
    girar(piezas, angulo)
    return mover(piezas, x, y, z)


def aceituna(x=0.0, y=0.0, z=0.0, angulo=0.0):
    malla = organico((0.012, 0.009, 0.009), 0.0004, 0.01, 2)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.009), ACEITUNA)]


# salida

def aplanar(piezas):
    for pieza in piezas:
        if isinstance(pieza, list):
            yield from aplanar(pieza)
        else:
            yield pieza


def exportar(plato_id, numero, piezas):
    carpeta = SALIDA / plato_id
    carpeta.mkdir(parents=True, exist_ok=True)
    escena = trimesh.Scene()
    piezas = list(aplanar(piezas))
    for i, pieza in enumerate(piezas):
        pieza.apply_transform(Z_A_Y)
        escena.add_geometry(pieza, node_name=f"paso-{numero}-{i}", geom_name=f"pieza-{i}")
    destino = carpeta / f"paso-{numero}.glb"
    escena.export(destino, include_normals=True)
    triangulos = sum(len(pieza.faces) for pieza in piezas)
    print(f"{plato_id}/{destino.name}: {destino.stat().st_size / 1024:.0f} KB, {len(piezas)} piezas, {triangulos} triangulos")
