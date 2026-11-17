"""Ceviche de pescado, un modelo por paso."""

import numpy as np

from base import (
    ALTURA_PLATO,
    ALTURA_TABLA,
    CAMOTE,
    CAMOTE_PIEL,
    LIMON,
    Material,
    aji,
    anillo,
    bol,
    cuchillo,
    disco,
    escalon,
    extruir,
    girar,
    hoja_lechuga,
    hojas_picadas,
    husillo,
    medio_limon,
    mezcla,
    motas,
    mover,
    organico,
    pintar,
    plato,
    radio_bol,
    rectangulo,
    ruido,
    tabla,
    trozo_choclo,
    tubo,
)

ID = "ceviche"
rng = np.random.default_rng(31)

PESCADO = Material((0.95, 0.80, 0.76), 0.4)
PESCADO_VETA = (0.98, 0.93, 0.90)
CURADO = Material((0.97, 0.94, 0.89), 0.5)
CURADO_VETA = (0.90, 0.84, 0.78)
CEBOLLA = Material((0.58, 0.16, 0.38), 0.35)
CEBOLLA_CLARA = (0.96, 0.86, 0.90)
AJI_LIMO = Material((0.86, 0.10, 0.07), 0.25)
CULANTRO = Material((0.18, 0.48, 0.16), 0.7)
JUGO = Material((0.88, 0.92, 0.62), 0.08, 0.0, 0.6)
LECHE_TIGRE = Material((0.95, 0.94, 0.84), 0.12, 0.0, 0.7)
CANCHA = Material((0.82, 0.56, 0.22), 0.6)
CANCHA_TOSTADA = (0.50, 0.28, 0.10)
CUENCO = Material((0.25, 0.42, 0.55), 0.3)


def filete(x, y, z, angulo=0.0, largo=0.085):
    malla = organico((largo, 0.036, 0.009), 0.0015, 0.03, 3, 4)
    v = np.array(malla.vertices)
    v[:, 1] *= 1 - 0.55 * escalon(v[:, 0], -0.01, largo)
    malla.vertices = v
    espina = np.abs(np.sin((v[:, 0] + np.abs(v[:, 1]) * 0.9) / 0.011 * np.pi)) ** 8
    colores = mezcla(PESCADO.color, PESCADO_VETA, espina * 0.8)
    colores = mezcla(colores, PESCADO_VETA, (1 - escalon(np.abs(v[:, 1]), 0.0, 0.003)) * 0.7)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.009), PESCADO, colores)]


def cubo_pescado(x, y, z, curado=False, inclinacion=0.3):
    semilla = int(rng.integers(1000))
    lado = rng.uniform(0.015, 0.019)
    contorno = rectangulo(lado, lado * rng.uniform(0.8, 1.0), 0.0035, 4)
    malla = extruir(contorno, lado * rng.uniform(0.7, 0.9), bisel=0.0025, niveles=2, anillos=2)
    material, veta = (CURADO, CURADO_VETA) if curado else (PESCADO, PESCADO_VETA)
    lineas = escalon(ruido(malla.vertices * [1, 3.5, 1], 0.012, semilla), 0.1, 0.8)
    colores = mezcla(material.color, veta, lineas * 0.7)
    girar(malla, rng.uniform(-inclinacion, inclinacion), (1, 0, 0))
    girar(malla, rng.uniform(0, np.pi))
    return pintar(mover(malla, x, y, z), material, colores)


def media_cebolla(x, y, z, angulo=0.0):
    radio = 0.034
    malla = organico((radio, radio * 0.95, radio * 0.9), subdivisiones=4)
    v = np.array(malla.vertices)
    v[:, 2] = np.maximum(v[:, 2], 0)
    malla.vertices = v
    giro = np.arctan2(v[:, 2], v[:, 1])
    distancia = np.hypot(v[:, 1], v[:, 2]) / radio
    vetas = np.abs(np.sin(giro * 11)) ** 3 * escalon(distancia, 0.25, 0.7)
    colores = mezcla(CEBOLLA.color, CEBOLLA_CLARA, vetas * 0.35)
    # la base cortada muestra los anillos
    centro = np.linalg.norm(v, axis=1) / radio
    anillos = np.abs(np.sin(centro * np.pi * 4.5)) ** 2
    colores = mezcla(colores, mezcla(CEBOLLA_CLARA, CEBOLLA.color, anillos * 0.5), (v[:, 2] < 1e-6).astype(float))
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), CEBOLLA, colores)]


def pluma_cebolla(x, y, z, angulo=0.0, radio=0.026, inclinacion=0.0, apertura=1.25):
    n, lados = 20, 10
    arco = [(radio * np.cos(a), radio * np.sin(a), 0) for a in np.linspace(-apertura, apertura, n)]
    malla = tubo(arco, husillo(n, 0.0032, 0.12, 0.12), lados=lados, ancho=0.42)
    lado = np.cos(np.linspace(0, 2 * np.pi, lados, endpoint=False))
    borde = np.concatenate([np.tile(lado, n), [0.0, 0.0]])
    colores = mezcla(CEBOLLA_CLARA, CEBOLLA.color, escalon(-borde, 0.1, 0.8))
    mover(malla, x=-radio * 0.8)
    girar(malla, inclinacion, (0, 1, 0))
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.0032), CEBOLLA, colores)


def plumas(x, y, z, radio, cantidad, caida=0.0):
    piezas = []
    for _ in range(cantidad):
        r = radio * np.sqrt(rng.uniform())
        giro = rng.uniform(0, 2 * np.pi)
        altura = z - caida * (r / radio) ** 2 + rng.uniform(0, 0.004)
        piezas.append(
            pluma_cebolla(
                x + r * np.cos(giro),
                y + r * np.sin(giro),
                altura,
                rng.uniform(0, 2 * np.pi),
                rng.uniform(0.02, 0.03),
                rng.uniform(-0.25, 0.25),
            )
        )
    return piezas


def rodajas_aji(x, y, z, radio, cantidad, caida=0.0):
    piezas = []
    for _ in range(cantidad):
        r = radio * np.sqrt(rng.uniform())
        giro = rng.uniform(0, 2 * np.pi)
        rodaja = anillo(0.0038, 0.0062, 0.0022, secciones=20)
        girar(rodaja, rng.uniform(-0.4, 0.4), (1, 0, 0))
        mover(rodaja, x + r * np.cos(giro), y + r * np.sin(giro), z - caida * (r / radio) ** 2)
        piezas.append(pintar(rodaja, AJI_LIMO))
    return piezas


def limon_entero(x, y, z, angulo=0.0):
    malla = organico((0.022, 0.0195, 0.0195), 0.0006, 0.012, 9)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.0195), LIMON)]


def monton(x, y, z, curado=True):
    # cubos apilados en tres niveles
    piezas = []
    niveles = [(0.036, 8, 0.0, 0.2), (0.015, 4, 0.0, 0.9), (0.022, 5, 0.013, 0.5), (0.0, 1, 0.025, 0.0)]
    for radio, cantidad, altura, fase in niveles:
        for giro in np.linspace(0, 2 * np.pi, cantidad, endpoint=False) + fase:
            r = radio + rng.uniform(-0.003, 0.003)
            piezas.append(cubo_pescado(x + r * np.cos(giro), y + r * np.sin(giro), z + altura, curado))
    return piezas


def rodaja_camote(x, y, z, angulo=0.0, radio=0.026):
    alto = 0.013
    malla = disco(radio, alto, bisel=0.002, paso=0.003, secciones=48)
    malla.apply_scale([1.12, 1.0, 1.0])
    v = malla.vertices
    distancia = np.hypot(v[:, 0] / 1.12, v[:, 1]) / radio
    colores = motas(malla, CAMOTE.color, (0.98, 0.66, 0.24), 0.01, 0.1, 61)
    piel = escalon(distancia, 0.93, 0.99) * escalon(v[:, 2], 0.0, 0.002) * (1 - escalon(v[:, 2], alto - 0.002, alto))
    colores = mezcla(colores, CAMOTE_PIEL, piel)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), CAMOTE, colores)]


def cancha(x, y, z, cantidad=9):
    piezas = []
    for i in range(cantidad):
        semilla = int(rng.integers(1000))
        grano = organico((0.0065, 0.0055, 0.0048), 0.0008, 0.006, semilla, 2)
        colores = motas(grano, CANCHA.color, CANCHA_TOSTADA, 0.006, 0.3, semilla + 1)
        r = 0.013 * np.sqrt(i / cantidad) + 0.002
        giro = i * 2.4
        girar(grano, rng.uniform(0, np.pi))
        mover(grano, x + r * np.cos(giro), y + r * np.sin(giro), z + 0.0048 + (0.006 if i < 2 else 0.0))
        piezas.append(pintar(grano, CANCHA, colores))
    return piezas


def paso_1():
    piezas = tabla(0.38, 0.26)
    piezas += filete(-0.075, 0.045, ALTURA_TABLA, 0.15)
    for fila in range(3):
        for columna in range(4):
            cx = -0.125 + columna * 0.026 + rng.uniform(-0.003, 0.003)
            cy = -0.035 - fila * 0.026 + rng.uniform(-0.003, 0.003)
            piezas.append(cubo_pescado(cx, cy, ALTURA_TABLA, inclinacion=0.0))
    piezas += cuchillo(0.035, -0.075, ALTURA_TABLA, 0.5)
    return piezas


def paso_2():
    piezas = tabla(0.38, 0.26)
    piezas += media_cebolla(-0.095, 0.045, ALTURA_TABLA, 0.3)
    for i in range(7):
        piezas.append(pluma_cebolla(-0.07 + i * 0.017, -0.035 + rng.uniform(-0.004, 0.004), ALTURA_TABLA, 0.25 + rng.uniform(-0.12, 0.12), 0.027))
    piezas += aji(0.085, 0.07, ALTURA_TABLA, 0.2, AJI_LIMO, 0.55)
    piezas += aji(0.105, 0.04, ALTURA_TABLA, -0.35, AJI_LIMO, 0.5)
    piezas += rodajas_aji(0.02, 0.06, ALTURA_TABLA, 0.016, 6)
    piezas += hojas_picadas(rng, 0.125, -0.055, ALTURA_TABLA, CULANTRO, 22, 0.022)
    return piezas


def paso_3():
    piezas = tabla(0.38, 0.26)
    radio, alto, grosor = 0.072, 0.052, 0.004
    cuenco = bol(radio, alto, grosor)
    nivel = 0.03
    cuenco.append(pintar(disco(radio_bol(radio, alto, grosor, nivel) - 0.0005, 0.002, nivel, bisel=0.0005), JUGO))
    piezas += mover(cuenco, x=-0.075, z=ALTURA_TABLA)
    piezas += medio_limon(0.045, 0.06, ALTURA_TABLA, 0.3)
    piezas += medio_limon(0.085, 0.02, ALTURA_TABLA, 1.2)
    piezas += medio_limon(0.04, -0.015, ALTURA_TABLA, 2.1)
    piezas += medio_limon(0.135, 0.065, ALTURA_TABLA, 0.8)
    piezas += limon_entero(0.10, -0.065, ALTURA_TABLA, 0.4)
    piezas += limon_entero(0.145, -0.03, ALTURA_TABLA, 1.5)
    return piezas


def paso_4():
    radio, alto, grosor = 0.10, 0.068, 0.0045
    piezas = bol(radio, alto, grosor, CUENCO)
    nivel = 0.024
    piso = grosor * 1.5
    for r, cantidad, fase in [(0.058, 11, 0.0), (0.032, 6, 0.4), (0.0, 1, 0.0)]:
        for giro in np.linspace(0, 2 * np.pi, cantidad, endpoint=False) + fase:
            d = r + rng.uniform(-0.004, 0.004)
            piezas.append(cubo_pescado(d * np.cos(giro), d * np.sin(giro), piso + 0.004 + rng.uniform(0, 0.006), True))
    for giro in np.linspace(0, 2 * np.pi, 5, endpoint=False) + 0.3:
        piezas.append(cubo_pescado(0.03 * np.cos(giro), 0.03 * np.sin(giro), piso + 0.019, True))
    piezas.append(pintar(disco(radio_bol(radio, alto, grosor, nivel) - 0.0005, 0.002, nivel, bisel=0.0005), LECHE_TIGRE))
    piezas += plumas(0, 0, nivel + 0.022, 0.05, 10, 0.012)
    piezas += rodajas_aji(0, 0, nivel + 0.027, 0.045, 7, 0.014)
    piezas += hojas_picadas(rng, 0, 0, nivel + 0.02, CULANTRO, 16, 0.035)
    return piezas


def paso_5():
    piezas = plato(0.15)
    piezas += hoja_lechuga(-0.04, 0.005, ALTURA_PLATO, 0.2, 0.078, 2)
    x, y, z = -0.028, 0.0, ALTURA_PLATO + 0.004
    piezas += monton(x, y, z)
    piezas += plumas(x, y, z + 0.036, 0.034, 8, 0.016)
    piezas += rodajas_aji(x, y, z + 0.043, 0.026, 5, 0.012)
    piezas += hojas_picadas(rng, x, y, z + 0.04, CULANTRO, 9, 0.016)
    piezas += rodaja_camote(0.058, -0.022, ALTURA_PLATO, 0.4)
    camote = rodaja_camote(0, 0, 0, 1.2)
    girar(camote, -0.5, (0, 1, 0))
    piezas += mover(camote, 0.045, -0.052, ALTURA_PLATO + 0.012)
    piezas += trozo_choclo(0.052, 0.046, ALTURA_PLATO, 0.3)
    piezas += cancha(0.002, -0.07, ALTURA_PLATO)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
