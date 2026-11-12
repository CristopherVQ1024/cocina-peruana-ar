"""Tacacho con cecina, un modelo por paso."""

import numpy as np

from base import (
    ALTURA_PLATO,
    ALTURA_SARTEN,
    ALTURA_TABLA,
    Material,
    bol,
    curva,
    disco,
    escalon,
    girar,
    husillo,
    mezcla,
    motas,
    mover,
    organico,
    pintar,
    plato,
    redondear,
    relieve,
    ruido,
    sarten,
    tabla,
    torno,
    tubo,
)

ID = "tacacho-con-cecina"
rng = np.random.default_rng(11)

PLATANO = Material((0.38, 0.56, 0.17), 0.55)
PLATANO_CLARO = (0.60, 0.66, 0.24)
PLATANO_PUNTA = (0.20, 0.20, 0.10)
ASADO = Material((0.93, 0.80, 0.50), 0.7)
TOSTADO = (0.50, 0.30, 0.12)
TACACHO = Material((0.91, 0.78, 0.47), 0.8)
CHICHARRON = Material((0.58, 0.35, 0.17), 0.6)
MORTERO = Material((0.47, 0.30, 0.17), 0.8)
MAZO = Material((0.62, 0.44, 0.26), 0.7)
CECINA = Material((0.52, 0.17, 0.12), 0.55)
CECINA_OSCURA = (0.27, 0.09, 0.07)
CECINA_GRASA = (0.84, 0.60, 0.44)
CHORIZO = Material((0.47, 0.17, 0.10), 0.4)
CHORIZO_OSCURO = (0.26, 0.09, 0.06)
SALSA = Material((0.95, 0.70, 0.18), 0.3)
SALSA_CEBOLLA = (0.72, 0.30, 0.46)
SALSA_CULANTRO = (0.25, 0.50, 0.15)


def arco(largo, radio_curva, n):
    apertura = largo / radio_curva / 2
    return [(radio_curva * np.sin(a), radio_curva * (1 - np.cos(a)), 0) for a in np.linspace(-apertura, apertura, n)]


def platano(x, y, z, angulo=0.0, asado=False):
    n = 30
    semilla = int(rng.integers(1000))
    grosor = 0.017 if asado else 0.02
    aristas = None if asado else (lambda a: 1 + 0.05 * np.cos(5 * a))
    malla = tubo(arco(0.2, 0.19, n), husillo(n, grosor, 0.16, 0.2), lados=20, seccion=aristas)
    t = malla.metadata["t"]
    if asado:
        colores = motas(malla, ASADO.color, TOSTADO, 0.022, 0.25, semilla)
        material = ASADO
    else:
        colores = mezcla(PLATANO.color, PLATANO_CLARO, escalon(ruido(malla.vertices, 0.06, semilla), -0.2, 0.9) * 0.7)
        colores = mezcla(colores, PLATANO_PUNTA, escalon(np.abs(t - 0.5) * 2, 0.86, 1.0))
        material = PLATANO
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + grosor), material, colores)


def bola_tacacho(x, y, z, radio=0.033):
    semilla = int(rng.integers(1000))
    malla = organico((radio, radio, radio * 0.9), 0.0028, 0.014, semilla, 4)
    colores = motas(malla, TACACHO.color, CHICHARRON.color, 0.007, 0.5, semilla + 1)
    colores = mezcla(colores, (0.97, 0.88, 0.62), escalon(ruido(malla.vertices, 0.03, semilla + 2), 0.1, 0.9) * 0.5)
    return pintar(mover(malla, x, y, z + radio * 0.86), TACACHO, colores)


def trozo_chicharron(x, y, z):
    malla = organico(rng.uniform(0.007, 0.011, 3), 0.002, 0.008, int(rng.integers(1000)), 2)
    girar(malla, rng.uniform(0, np.pi))
    return pintar(mover(malla, x, y, z), CHICHARRON)


def mortero():
    perfil = [(0, 0), (0.06, 0), (0.07, 0.012), (0.066, 0.03), (0.088, 0.085), (0.086, 0.092), (0.074, 0.09), (0.058, 0.03), (0, 0.026)]
    piezas = [pintar(torno(redondear(perfil, 0.004), 64), MORTERO)]
    perfil = [(0, 0.03), (0.058, 0.03), (0.07, 0.07), (0.055, 0.088), (0.03, 0.098), (0, 0.1)]
    masa = relieve(torno(curva(perfil, 20), 64, paso=0.004), 0.004, 0.016, 21)
    colores = motas(masa, TACACHO.color, CHICHARRON.color, 0.008, 0.5, 22)
    piezas.append(pintar(masa, TACACHO, colores))
    perfil = [(0, 0), (0.02, 0.003), (0.026, 0.03), (0.018, 0.07), (0.013, 0.17), (0.016, 0.2), (0, 0.206)]
    mazo = torno(curva(perfil, 28), 32)
    girar(mazo, 0.5, (0, 1, 0))
    piezas.append(pintar(mover(mazo, 0.012, 0.01, 0.088), MAZO))
    return piezas


def tira_cecina(x, y, z, angulo=0.0, largo=0.11):
    n = 36
    semilla = int(rng.integers(1000))
    t = np.linspace(-0.5, 0.5, n)
    fase = rng.uniform(0, 6)
    recorrido = np.column_stack([t * largo, 0.006 * np.sin(t * 5 + fase), 0.0022 * np.sin(t * 17 + fase)])
    malla = tubo(recorrido, husillo(n, 0.0032, 0.1, 0.1), lados=18, ancho=6.5)
    colores = motas(malla, CECINA.color, CECINA_OSCURA, 0.014, 0.1, semilla)
    veta = escalon(ruido(malla.vertices * [0.25, 1, 1], 0.012, semilla + 1), 0.55, 0.75)
    colores = mezcla(colores, CECINA_GRASA, veta * 0.45)
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.0045), CECINA, colores)


def chorizo(x, y, z, angulo=0.0, largo=0.075):
    n = 20
    malla = tubo(arco(largo, 0.09, n), husillo(n, 0.012, 0.14, 0.14), lados=16)
    colores = motas(malla, CHORIZO.color, CHORIZO_OSCURO, 0.008, 0.3, int(rng.integers(1000)))
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.012), CHORIZO, colores)


def salsa_cocona(x, y, z, radio=0.026):
    piezas = bol(radio, 0.026, 0.003)
    salsa = disco(radio * 0.86, 0.004, 0.017, bisel=0.001, paso=0.002, secciones=48)
    colores = motas(salsa, SALSA.color, SALSA_CEBOLLA, 0.005, 0.5, 31)
    colores = mezcla(colores, SALSA_CULANTRO, escalon(ruido(salsa.vertices, 0.004, 32), 0.6, 0.75))
    piezas.append(pintar(salsa, SALSA, colores))
    return mover(piezas, x, y, z)


def paso_1():
    piezas = tabla(0.36, 0.26)
    piezas.append(platano(-0.02, 0.065, ALTURA_TABLA, 0.12))
    piezas.append(platano(0.0, 0.02, ALTURA_TABLA, -0.05))
    piezas.append(platano(-0.01, -0.03, ALTURA_TABLA, 0.08, asado=True))
    piezas.append(platano(0.015, -0.075, ALTURA_TABLA, -0.04, asado=True))
    return piezas


def paso_2():
    piezas = tabla(0.38, 0.26)
    piezas += mover(mortero(), x=-0.07, z=ALTURA_TABLA)
    cuenco = bol(0.045, 0.03, 0.0035)
    for giro in np.linspace(0, 2 * np.pi, 7)[:-1]:
        cuenco.append(trozo_chicharron(0.02 * np.cos(giro), 0.02 * np.sin(giro), 0.022))
    cuenco.append(trozo_chicharron(0, 0, 0.03))
    piezas += mover(cuenco, 0.115, -0.045, ALTURA_TABLA)
    return piezas


def paso_3():
    piezas = plato(0.14)
    piezas.append(bola_tacacho(-0.046, -0.026, ALTURA_PLATO))
    piezas.append(bola_tacacho(0.046, -0.026, ALTURA_PLATO))
    piezas.append(bola_tacacho(0.0, 0.052, ALTURA_PLATO))
    return piezas


def paso_4():
    piezas = sarten(0.125)
    piezas.append(tira_cecina(-0.025, 0.05, ALTURA_SARTEN, 0.15, 0.12))
    piezas.append(tira_cecina(-0.03, 0.0, ALTURA_SARTEN, -0.1, 0.125))
    piezas.append(tira_cecina(-0.02, -0.05, ALTURA_SARTEN, 0.05, 0.11))
    piezas.append(chorizo(0.065, 0.03, ALTURA_SARTEN, 1.5))
    piezas.append(chorizo(0.07, -0.04, ALTURA_SARTEN, 1.9))
    return piezas


def paso_5():
    piezas = plato(0.16)
    piezas.append(bola_tacacho(-0.045, 0.04, ALTURA_PLATO))
    piezas.append(bola_tacacho(0.025, 0.055, ALTURA_PLATO))
    piezas.append(tira_cecina(-0.035, -0.03, ALTURA_PLATO, 0.26, 0.11))
    piezas.append(tira_cecina(-0.03, -0.058, ALTURA_PLATO + 0.003, -0.09, 0.10))
    piezas.append(chorizo(0.078, 0.012, ALTURA_PLATO, 1.75))
    piezas += salsa_cocona(0.05, -0.055, ALTURA_PLATO)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
