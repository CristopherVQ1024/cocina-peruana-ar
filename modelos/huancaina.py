"""Papa a la huancaina, un modelo por paso."""

import numpy as np

from base import (
    ALTURA_PLATO,
    ALTURA_SARTEN,
    ALTURA_TABLA,
    HIERRO,
    MANGO,
    Material,
    aceituna,
    agua,
    aji,
    apoyar,
    curva,
    disco,
    escalon,
    extruir,
    girar,
    hoja_lechuga,
    mezcla,
    motas,
    mover,
    olla,
    organico,
    papa,
    pintar,
    plato,
    rectangulo,
    relieve,
    rodaja_huevo,
    sarten,
    tabla,
    torno,
    tubo,
)

ID = "papa-a-la-huancaina"
rng = np.random.default_rng(43)

SALSA = Material((0.98, 0.76, 0.16), 0.28)
SALSA_SOMBRA = (0.93, 0.64, 0.12)
PAPA_COCIDA = Material((0.97, 0.88, 0.56), 0.7)
PAPA_COCIDA_SOMBRA = (0.90, 0.76, 0.40)
HUEVO = Material((0.90, 0.74, 0.58), 0.45)
HUEVO_PECA = (0.78, 0.58, 0.42)
QUESO = Material((0.97, 0.96, 0.90), 0.6)
QUESO_OJO = (0.86, 0.84, 0.74)
GALLETA = Material((0.92, 0.78, 0.50), 0.8)
GALLETA_TOSTADA = (0.74, 0.52, 0.26)
VIDRIO = Material((0.90, 0.95, 0.97), 0.06, 0.0, 0.28)
LATA = Material((0.93, 0.93, 0.92), 0.35)
LATA_ETIQUETA = (0.16, 0.36, 0.62)
CEBOLLA = Material((0.66, 0.36, 0.50), 0.4)
CEBOLLA_CLARA = (0.95, 0.85, 0.89)
AJO = Material((0.95, 0.91, 0.80), 0.5)


def huevo(x, y, z, angulo=0.0):
    semilla = int(rng.integers(1000))
    malla = organico((0.029, 0.0215, 0.0215), subdivisiones=3)
    v = np.array(malla.vertices)
    estrecho = 1 - 0.16 * v[:, 0] / 0.029
    v[:, 1] *= estrecho
    v[:, 2] *= estrecho
    malla.vertices = v
    colores = motas(malla, HUEVO.color, HUEVO_PECA, 0.004, 0.62, semilla)
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.0215), HUEVO, colores)


def trozo_cebolla(x, y, z):
    semilla = int(rng.integers(1000))
    malla = organico((0.02, 0.011, 0.007), 0.0015, 0.012, semilla, 3)
    v = np.array(malla.vertices)
    v[:, 2] += 0.3 * v[:, 0] ** 2 / 0.02
    malla.vertices = v
    colores = mezcla(CEBOLLA_CLARA, CEBOLLA.color, escalon(v[:, 2], -0.002, 0.006))
    girar(malla, rng.uniform(0, 2 * np.pi))
    return pintar(mover(malla, x, y, z + 0.007), CEBOLLA, colores)


def diente_ajo(x, y, z):
    malla = organico((0.011, 0.007, 0.0065), 0.0005, 0.01, int(rng.integers(1000)), 2)
    girar(malla, rng.uniform(0, 2 * np.pi))
    return pintar(mover(malla, x, y, z + 0.0065), AJO)


def licuadora():
    perfil = [(0, 0), (0.062, 0), (0.064, 0.012), (0.052, 0.058), (0.046, 0.07), (0, 0.07)]
    piezas = [pintar(torno(perfil[:1] + list(curva(perfil[1:-1], 14)) + perfil[-1:], 64), HIERRO)]
    perilla = disco(0.013, 0.008, bisel=0.002, secciones=24)
    girar(perilla, np.pi / 2, (1, 0, 0))
    piezas.append(pintar(mover(perilla, 0, -0.056, 0.03), Material((0.80, 0.81, 0.82), 0.3, 1.0)))
    base, tope = 0.072, 0.21
    vaso = [(0, base), (0.040, base), (0.060, tope), (0.057, tope), (0.037, base + 0.004), (0, base + 0.004)]
    piezas.append(pintar(torno(vaso, 64), VIDRIO))
    nivel = 0.155
    radio_nivel = 0.037 + (0.057 - 0.037) * (nivel - base) / (tope - base) - 0.0008
    salsa = torno([(0, base + 0.0045), (0.0365, base + 0.0045), (radio_nivel, nivel), (0, nivel + 0.003)], 64, paso=0.004)
    relieve(salsa, 0.0004, 0.01, 5)
    piezas.append(pintar(salsa, SALSA, motas(salsa, SALSA.color, SALSA_SOMBRA, 0.012, 0.2, 6)))
    piezas.append(pintar(disco(0.062, 0.012, tope, bisel=0.003), MANGO))
    piezas.append(pintar(disco(0.02, 0.012, tope + 0.01, bisel=0.003, secciones=32), MANGO))
    asa = curva([(0.05, 0, 0.19), (0.092, 0, 0.185), (0.095, 0, 0.13), (0.045, 0, 0.1)], 18)
    piezas.append(pintar(tubo(asa, 0.0055, lados=10, ancho=1.3), VIDRIO))
    return piezas


def queso_fresco(x, y, z, angulo=0.0):
    malla = extruir(rectangulo(0.075, 0.055, 0.008, 5), 0.034, bisel=0.004, niveles=8, anillos=5)
    colores = motas(malla, QUESO.color, QUESO_OJO, 0.006, 0.55, 14)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), QUESO, colores)]


def galleta(x, y, z, angulo=0.0):
    lado = 0.048
    malla = extruir(rectangulo(lado, lado, 0.004, 4), 0.0045, bisel=0.001, anillos=8)
    v = malla.vertices
    puntos = (np.cos(v[:, 0] / lado * 6 * np.pi) * np.cos(v[:, 1] / lado * 6 * np.pi)) ** 8
    borde = escalon(np.maximum(np.abs(v[:, 0]), np.abs(v[:, 1])), lado * 0.36, lado * 0.5)
    colores = mezcla(GALLETA.color, GALLETA_TOSTADA, np.maximum(puntos * 0.7, borde * 0.6))
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), GALLETA, colores)]


def lata(x, y, z):
    alto = 0.098
    malla = disco(0.037, alto, bisel=0.002, paso=0.006)
    altura = malla.vertices[:, 2]
    banda = escalon(altura, 0.008, 0.012) * (1 - escalon(altura, alto - 0.012, alto - 0.008))
    franja = escalon(altura, 0.04, 0.043) * (1 - escalon(altura, 0.058, 0.061))
    colores = mezcla(LATA.color, LATA_ETIQUETA, banda * (1 - franja * 0.85))
    return [pintar(mover(malla, x, y, z), LATA, colores)]


def rodaja_papa(inclinacion):
    semilla = int(rng.integers(1000))
    malla = disco(0.027, 0.01, bisel=0.002, paso=0.004, secciones=40)
    malla.apply_scale([1.0, rng.uniform(1.05, 1.2), 1.0])
    relieve(malla, 0.0005, 0.012, semilla)
    colores = motas(malla, PAPA_COCIDA.color, PAPA_COCIDA_SOMBRA, 0.012, 0.3, semilla + 1)
    girar(malla, inclinacion, (0, 1, 0))
    return pintar(malla, PAPA_COCIDA, colores)


PASO_RODAJA = 0.02
RODAJAS = 6


def base_plato():
    piezas = plato(0.155)
    piezas += hoja_lechuga(-0.05, 0.02, ALTURA_PLATO, 2.9, 0.07, 1)
    piezas += hoja_lechuga(0.05, -0.02, ALTURA_PLATO, -0.3, 0.07, 4)
    for i in range(RODAJAS):
        rodaja = apoyar(rodaja_papa(-0.5), ALTURA_PLATO + 0.004)
        piezas.append(mover(rodaja, (i - (RODAJAS - 1) / 2) * PASO_RODAJA, rng.uniform(-0.003, 0.003)))
    return piezas


def manto_salsa():
    largo, ancho = 0.066, 0.046
    malla = organico((largo, ancho, 0.011), subdivisiones=4)
    v = np.array(malla.vertices)
    distancia = np.hypot(v[:, 0] / largo, v[:, 1] / ancho)
    borde = 1 + 0.1 * np.sin(np.arctan2(v[:, 1], v[:, 0]) * 5 + 1) * escalon(distancia, 0.5, 1.0)
    v[:, 0] *= borde
    v[:, 1] *= borde
    # ondas sobre cada rodaja
    onda = np.cos((v[:, 0] / PASO_RODAJA + 0.5) * 2 * np.pi) * 0.003
    v[:, 2] += onda * (1 - escalon(distancia, 0.5, 1.0)) - 0.012 * distancia**2
    malla.vertices = v
    colores = motas(malla, SALSA.color, SALSA_SOMBRA, 0.016, 0.3, 71)
    return [pintar(mover(malla, 0.006, 0, ALTURA_PLATO + 0.027), SALSA, colores)]


def charco_salsa():
    malla = disco(0.066, 0.003, ALTURA_PLATO, bisel=0.0014, paso=0.005, secciones=64)
    v = np.array(malla.vertices)
    giro = np.arctan2(v[:, 1], v[:, 0])
    factor = 1 + 0.07 * np.sin(giro * 3 + 0.5) + 0.04 * np.sin(giro * 7)
    v[:, 0] *= factor * 1.08
    v[:, 1] *= factor * 0.82
    malla.vertices = v
    return [pintar(malla, SALSA, motas(malla, SALSA.color, SALSA_SOMBRA, 0.02, 0.3, 72))]


def paso_1():
    piezas = mover(olla() + agua(0.081, 0.076), x=-0.07)
    for giro in np.linspace(0, 2 * np.pi, 4)[:-1]:
        piezas.append(papa(rng, -0.07 + 0.04 * np.cos(giro + 0.3), 0.04 * np.sin(giro + 0.3), 0.05, rng.uniform(0.85, 1.0)))
    piezas.append(huevo(-0.07, 0.0, 0.046, 0.6))
    piezas.append(huevo(-0.115, 0.012, 0.046, 2.0))
    piezas.append(papa(rng, 0.09, 0.055, 0.0, 1.05))
    piezas.append(papa(rng, 0.14, 0.0, 0.0, 0.95))
    piezas.append(huevo(0.075, -0.035, 0.0, 0.4))
    piezas.append(huevo(0.125, -0.07, 0.0, 1.9))
    return piezas


def paso_2():
    piezas = sarten(0.125)
    piezas += aji(-0.012, 0.045, ALTURA_SARTEN, 0.12)
    piezas += aji(0.005, 0.005, ALTURA_SARTEN, 3.3)
    for cx, cy in [(-0.045, -0.04), (-0.01, -0.058), (0.03, -0.045), (0.058, -0.02), (-0.07, -0.01)]:
        piezas.append(trozo_cebolla(cx, cy, ALTURA_SARTEN))
    for cx, cy in [(0.012, -0.03), (0.07, 0.03), (-0.03, -0.075)]:
        piezas.append(diente_ajo(cx, cy, ALTURA_SARTEN))
    return piezas


def paso_3():
    piezas = tabla(0.42, 0.27)
    piezas += mover(licuadora(), x=-0.115, z=ALTURA_TABLA)
    piezas += queso_fresco(0.03, 0.055, ALTURA_TABLA, 0.2)
    piezas += galleta(0.03, -0.062, ALTURA_TABLA, 0.15)
    piezas += galleta(0.038, -0.058, ALTURA_TABLA + 0.0045, 0.5)
    piezas += galleta(0.085, -0.075, ALTURA_TABLA, -0.3)
    piezas += lata(0.145, 0.03, ALTURA_TABLA)
    return piezas


def paso_4():
    return base_plato()


def paso_5():
    piezas = base_plato() + charco_salsa() + manto_salsa()
    piezas += rodaja_huevo(-0.03, 0.006, ALTURA_PLATO + 0.034, 0.5, -0.15)
    piezas += rodaja_huevo(0.012, -0.006, ALTURA_PLATO + 0.036, -0.4, 0.1)
    piezas += rodaja_huevo(0.05, 0.004, ALTURA_PLATO + 0.031, 0.9, 0.25)
    piezas += aceituna(-0.008, 0.02, ALTURA_PLATO + 0.03, 0.6)
    piezas += aceituna(0.032, -0.022, ALTURA_PLATO + 0.028, 1.8)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
