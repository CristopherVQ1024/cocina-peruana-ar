"""Anticuchos de corazon, un modelo por paso."""

import numpy as np
import trimesh

from base import (
    ALTURA_PLATO,
    ALTURA_TABLA,
    HIERRO,
    Material,
    aji,
    apoyar,
    bol,
    cuchillo,
    disco,
    escalon,
    extruir,
    girar,
    husillo,
    mezcla,
    motas,
    mover,
    organico,
    pintar,
    plato,
    radio_bol,
    rectangulo,
    relieve,
    ruido,
    tabla,
    trozo_choclo,
    tubo,
)

ID = "anticuchos"
rng = np.random.default_rng(89)

CORAZON = Material((0.52, 0.10, 0.12), 0.45)
CORAZON_GRASA = (0.88, 0.72, 0.62)
MARINADO = Material((0.52, 0.15, 0.08), 0.5)
MARINADO_SOMBRA = (0.32, 0.07, 0.05)
ASADO = Material((0.40, 0.18, 0.08), 0.6)
ASADO_MARCA = (0.13, 0.06, 0.04)
PALITO = Material((0.82, 0.68, 0.46), 0.7)
MARINADA = Material((0.50, 0.14, 0.07), 0.65)
MARINADA_CLARA = (0.68, 0.24, 0.10)
PANCA = Material((0.38, 0.09, 0.07), 0.6)
AJO = Material((0.95, 0.91, 0.80), 0.5)
COMINO = Material((0.56, 0.42, 0.22), 0.9)
CARBON = Material((0.14, 0.13, 0.13), 0.9)
BRASA = (0.96, 0.38, 0.08)
CENIZA = (0.56, 0.54, 0.51)
REJILLA = Material((0.42, 0.42, 0.43), 0.4, 0.8)
PAPA_DORADA = Material((0.95, 0.80, 0.42), 0.65)
DORADO = (0.72, 0.46, 0.17)
SALSA = Material((0.96, 0.58, 0.06), 0.65)
SALSA_MOTA = (0.80, 0.30, 0.08)

ESTADOS = {
    "crudo": (CORAZON, CORAZON_GRASA, 0.55),
    "marinado": (MARINADO, MARINADO_SOMBRA, 0.2),
    "asado": (ASADO, ASADO_MARCA, 0.1),
}
ALTO_TROZO = 0.012


def trozo(estado="crudo", lado=0.03):
    # queda centrado en el origen
    semilla = int(rng.integers(1000))
    contorno = rectangulo(lado, lado * rng.uniform(0.8, 0.95), 0.005, 4)
    malla = extruir(contorno, ALTO_TROZO, bisel=0.003, niveles=2, anillos=3)
    relieve(malla, 0.0008, 0.012, semilla)
    material, tono, umbral = ESTADOS[estado]
    colores = motas(malla, material.color, tono, 0.009, umbral, semilla + 1)
    return pintar(mover(malla, z=-ALTO_TROZO / 2), material, colores)


def palito(largo=0.223):
    recorrido = np.column_stack([np.linspace(0, largo, 6), np.zeros(6), np.zeros(6)])
    return pintar(tubo(recorrido, husillo(6, 0.0018, 0.15, 0.0), lados=8), PALITO)


def anticucho(x, y, z, angulo=0.0, estado="asado", largo=0.223):
    piezas = [mover(palito(largo), x=-0.058)]
    for cx in (-0.034, 0.0, 0.034):
        pieza = trozo(estado)
        girar(pieza, rng.uniform(-0.25, 0.25), (1, 0, 0))
        girar(pieza, np.pi / 2 + rng.uniform(-0.1, 0.1))
        piezas.append(mover(pieza, x=cx))
    apoyar(piezas, 0)
    girar(piezas, angulo)
    return mover(piezas, x, y, z)


def corazon(x, y, z, angulo=0.0):
    malla = organico((0.056, 0.044, 0.03), 0.003, 0.04, 7, 4)
    v = np.array(malla.vertices)
    v[:, 1] *= 1 - 0.35 * escalon(v[:, 0], 0.0, 0.056)
    v[:, 2] = np.maximum(v[:, 2], -0.014)
    malla.vertices = v
    grasa = escalon(-v[:, 0], 0.02, 0.05) * (0.4 + 0.6 * escalon(ruido(v, 0.02, 8), -0.3, 0.5))
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.014), CORAZON, mezcla(CORAZON.color, CORAZON_GRASA, grasa * 0.8))]


def diente_ajo(x, y, z):
    malla = organico((0.011, 0.007, 0.0065), 0.0005, 0.01, int(rng.integers(1000)), 2)
    girar(malla, rng.uniform(0, 2 * np.pi))
    return pintar(mover(malla, x, y, z + 0.0065), AJO)


def parrilla():
    largo, fondo, base, borde = 0.36, 0.22, 0.02, 0.10
    partes = [mover(extruir(rectangulo(largo, fondo, 0.004, 3), 0.006, bisel=0.002), z=base)]
    for lado in (1, -1):
        pared = extruir(rectangulo(largo, 0.006, 0.002, 3), borde - base, bisel=0.0015)
        partes.append(mover(pared, y=lado * (fondo / 2 - 0.003), z=base))
        pared = extruir(rectangulo(0.006, fondo, 0.002, 3), borde - base, bisel=0.0015)
        partes.append(mover(pared, x=lado * (largo / 2 - 0.003), z=base))
        for otro in (1, -1):
            partes.append(mover(disco(0.011, base + 0.002, bisel=0.002, secciones=20), lado * (largo / 2 - 0.03), otro * (fondo / 2 - 0.03)))
    piezas = [pintar(trimesh.util.concatenate(partes), HIERRO)]
    lecho = extruir(rectangulo(largo - 0.014, fondo - 0.014, 0.003, 3), 0.04, bisel=0.002)
    piezas.append(pintar(mover(lecho, z=base + 0.006), CARBON))
    for fila in range(5):
        for columna in range(9):
            semilla = int(rng.integers(1000))
            carbon = organico(rng.uniform(0.013, 0.02, 3), 0.004, 0.012, semilla, 2)
            calor = escalon(ruido(carbon.vertices, 0.014, semilla + 1), -0.1, 0.7)
            colores = mezcla(CARBON.color, BRASA, calor)
            colores = mezcla(colores, CENIZA, escalon(ruido(carbon.vertices, 0.009, semilla + 2), 0.3, 0.8) * 0.7)
            cx = (columna - 4) * 0.037 + rng.uniform(-0.006, 0.006)
            cy = (fila - 2) * 0.038 + rng.uniform(-0.006, 0.006)
            piezas.append(pintar(mover(carbon, cx, cy, base + 0.05 + rng.uniform(0, 0.006)), CARBON, colores))
    barras = []
    for cy in np.linspace(-fondo / 2 + 0.008, fondo / 2 - 0.008, 17):
        barras.append(tubo([(-largo / 2 + 0.002, cy, borde + 0.002), (largo / 2 - 0.002, cy, borde + 0.002)], 0.0018, lados=6))
    for cx in (-largo / 2 + 0.003, 0.0, largo / 2 - 0.003):
        barras.append(tubo([(cx, -fondo / 2 + 0.002, borde + 0.0005), (cx, fondo / 2 - 0.002, borde + 0.0005)], 0.0022, lados=6))
    piezas.append(pintar(trimesh.util.concatenate(barras), REJILLA))
    return piezas, borde + 0.004


def rodaja_papa(inclinacion=0.0, angulo=0.0):
    semilla = int(rng.integers(1000))
    malla = disco(0.026, 0.011, bisel=0.003, paso=0.004, secciones=40)
    malla.apply_scale([1.15, 1.0, 1.0])
    colores = mezcla(PAPA_DORADA.color, DORADO, escalon(ruido(malla.vertices, 0.03, semilla), 0.0, 1.0) * 0.8)
    girar(malla, inclinacion, (0, 1, 0))
    girar(malla, angulo)
    return pintar(malla, PAPA_DORADA, colores)


def paso_1():
    piezas = tabla(0.38, 0.26)
    piezas += corazon(-0.095, 0.06, ALTURA_TABLA, 0.2)
    for fila in range(2):
        for columna in range(4):
            pieza = girar(trozo(), rng.uniform(-0.15, 0.15))
            cx = -0.14 + columna * 0.038 + rng.uniform(-0.003, 0.003)
            piezas.append(mover(pieza, cx, -0.035 - fila * 0.037, ALTURA_TABLA + ALTO_TROZO / 2))
    piezas += cuchillo(0.09, -0.02, ALTURA_TABLA, 1.1)
    return piezas


def paso_2():
    piezas = tabla(0.38, 0.26)
    radio, alto, grosor = 0.085, 0.058, 0.004
    cuenco = bol(radio, alto, grosor)
    nivel = 0.03
    marinada = disco(radio_bol(radio, alto, grosor, nivel) - 0.0005, 0.002, nivel, bisel=0.0005, paso=0.005)
    cuenco.append(pintar(marinada, MARINADA, motas(marinada, MARINADA.color, MARINADA_CLARA, 0.02, 0.1, 21)))
    for r, cantidad, altura, fase in [(0.046, 7, 0.0, 0.0), (0.02, 3, 0.004, 0.5)]:
        for giro in np.linspace(0, 2 * np.pi, cantidad, endpoint=False) + fase:
            pieza = trozo("marinado")
            girar(pieza, rng.uniform(-0.5, 0.5), (1, 0, 0))
            girar(pieza, rng.uniform(0, np.pi))
            cuenco.append(mover(pieza, r * np.cos(giro), r * np.sin(giro), nivel + 0.002 + altura))
    piezas += mover(cuenco, x=-0.08, z=ALTURA_TABLA)
    piezas += aji(0.085, 0.07, ALTURA_TABLA, 0.2, PANCA, 0.9)
    piezas += aji(0.095, 0.035, ALTURA_TABLA, -0.2, PANCA, 0.85)
    for cx, cy in [(0.05, -0.02), (0.07, -0.035), (0.045, -0.045)]:
        piezas.append(diente_ajo(cx, cy, ALTURA_TABLA))
    especia = bol(0.03, 0.02, 0.003)
    especia.append(pintar(relieve(disco(0.022, 0.004, 0.011, bisel=0.0015, paso=0.003, secciones=32), 0.0006, 0.004, 22), COMINO))
    piezas += mover(especia, 0.135, -0.065, ALTURA_TABLA)
    return piezas


def paso_3():
    piezas = tabla(0.40, 0.27)
    for cy in [0.092, 0.046, 0.0]:
        piezas += anticucho(-0.06, cy, ALTURA_TABLA, rng.uniform(-0.05, 0.05), "marinado")
    for i in range(3):
        suelto = palito()
        girar(suelto, rng.uniform(-0.06, 0.06))
        piezas.append(mover(suelto, -0.13, -0.05 - i * 0.012, ALTURA_TABLA + 0.0018))
    for cx, cy in [(0.13, -0.045), (0.16, -0.075), (0.125, -0.09), (0.165, -0.035)]:
        pieza = girar(trozo("marinado"), rng.uniform(0, np.pi))
        piezas.append(mover(pieza, cx, cy, ALTURA_TABLA + ALTO_TROZO / 2))
    return piezas


def paso_4():
    piezas, altura = parrilla()
    for i in range(5):
        piezas += anticucho(-0.12 + i * 0.06, 0.035, altura, -np.pi / 2 + rng.uniform(-0.05, 0.05))
    return piezas


def paso_5():
    piezas = plato(0.165)
    piezas += anticucho(-0.03, 0.032, ALTURA_PLATO, 0.12, largo=0.2)
    piezas += anticucho(-0.035, -0.008, ALTURA_PLATO, 0.05, largo=0.2)
    for cx in [0.0, 0.03, 0.06]:
        rodaja = apoyar(rodaja_papa(-0.45, 0.2), ALTURA_PLATO)
        piezas.append(mover(rodaja, cx, -0.064))
    piezas += trozo_choclo(-0.058, -0.058, ALTURA_PLATO, 0.3)
    salsa = bol(0.025, 0.024, 0.003)
    crema = disco(0.02, 0.003, 0.015, bisel=0.001, paso=0.002, secciones=40)
    salsa.append(pintar(crema, SALSA, motas(crema, SALSA.color, SALSA_MOTA, 0.004, 0.5, 31)))
    piezas += mover(salsa, 0.0, 0.078, ALTURA_PLATO)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
