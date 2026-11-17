"""Picarones, un modelo por paso."""

import numpy as np
import trimesh

from base import (
    ALTURA_PLATO,
    ALTURA_TABLA,
    CAMOTE,
    CAMOTE_PIEL,
    Material,
    agua,
    bol,
    curva,
    disco,
    escalon,
    extruir,
    girar,
    husillo,
    mezcla,
    motas,
    mover,
    olla,
    organico,
    pintar,
    plato,
    rectangulo,
    relieve,
    ruido,
    sarten,
    tabla,
    torno,
    tubo,
)

ID = "picarones"
rng = np.random.default_rng(59)

ZAPALLO = Material((0.95, 0.56, 0.12), 0.6)
ZAPALLO_CLARO = (0.98, 0.72, 0.28)
ZAPALLO_PIEL = (0.22, 0.36, 0.16)
MASA = Material((0.96, 0.74, 0.34), 0.55)
MASA_SOMBRA = (0.90, 0.60, 0.22)
CRUDO = (0.95, 0.76, 0.40)
FRITO = Material((0.80, 0.48, 0.14), 0.5)
FRITO_OSCURO = (0.52, 0.26, 0.07)
FRITO_CLARO = (0.93, 0.70, 0.32)
CON_MIEL = Material((0.80, 0.48, 0.14), 0.18)
ACEITE = Material((0.96, 0.76, 0.20), 0.05, 0.0, 0.5)
MIEL = Material((0.24, 0.09, 0.03), 0.08, 0.0, 0.93)
MIEL_BRILLO = (0.46, 0.20, 0.05)
CHARCO = Material((0.44, 0.20, 0.05), 0.65)
CHANCACA = Material((0.34, 0.17, 0.07), 0.75)
CHANCACA_CLARA = (0.50, 0.28, 0.12)
CANELA = Material((0.52, 0.29, 0.14), 0.8)
NARANJA = Material((0.95, 0.52, 0.08), 0.5)
HARINA = Material((0.97, 0.95, 0.90), 0.9)
PALITO = Material((0.74, 0.58, 0.38), 0.7)


def rosca(x, y, z, radio=0.027, grosor=0.01, coccion=1.0, miel=False, inclinacion=0.0, angulo=0.0):
    # coccion va de 0 crudo a 1 dorado
    n, m = 56, 18
    fase = rng.uniform(0, 2 * np.pi)
    semilla = int(rng.integers(1000))
    u, v = np.meshgrid(np.linspace(0, 2 * np.pi, n, endpoint=False), np.linspace(0, 2 * np.pi, m, endpoint=False), indexing="ij")
    g = grosor * (1 + 0.16 * np.sin(2 * u + fase) + 0.08 * np.sin(5 * u + 2 * fase))
    r = radio * (1 + 0.07 * np.sin(3 * u + 1.7 * fase)) + g * np.cos(v)
    vertices = np.column_stack([(r * np.cos(u)).ravel(), (r * np.sin(u)).ravel(), (g * 0.82 * np.sin(v)).ravel()])
    i, j = np.meshgrid(np.arange(n), np.arange(m), indexing="ij")
    a = (i * m + j).ravel()
    b = (i * m + (j + 1) % m).ravel()
    c = (((i + 1) % n) * m + j).ravel()
    d = (((i + 1) % n) * m + (j + 1) % m).ravel()
    malla = trimesh.Trimesh(vertices, np.vstack([np.column_stack([a, c, b]), np.column_stack([b, c, d])]), process=False)
    if malla.volume < 0:
        malla.invert()
    relieve(malla, 0.0009, 0.008, semilla)
    altura = malla.vertices[:, 2] / (grosor * 0.82)
    dorado = mezcla(FRITO.color, FRITO_OSCURO, escalon(ruido(malla.vertices, 0.012, semilla + 1), 0.0, 0.9) * 0.7)
    dorado = mezcla(dorado, FRITO_CLARO, np.exp(-((altura / 0.28) ** 2)) * 0.75)
    colores = mezcla(CRUDO, dorado, np.full(len(altura), coccion))
    if miel:
        chorro = escalon(altura, -0.5, 0.6) * (0.6 + 0.4 * escalon(ruido(malla.vertices, 0.035, semilla + 2, 1), -0.6, 0.6))
        colores = mezcla(colores, MIEL_BRILLO, chorro * 0.7)
    girar(malla, inclinacion, (0, 1, 0))
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + grosor * 0.82), CON_MIEL if miel else FRITO, colores)


def trozo_zapallo(x, y, z, angulo=0.0, ancho=0.075, fondo=0.048, alto=0.036):
    malla = extruir(rectangulo(ancho, fondo, 0.008, 5), alto, bisel=0.004, niveles=8, anillos=5)
    v = np.array(malla.vertices)
    v[:, 2] += 0.9 * v[:, 0] ** 2 / ancho
    malla.vertices = v
    altura = v[:, 2] - 0.9 * v[:, 0] ** 2 / ancho
    colores = motas(malla, ZAPALLO.color, ZAPALLO_CLARO, 0.012, 0.1, 81)
    colores = mezcla(colores, ZAPALLO_PIEL, 1 - escalon(altura, 0.004, 0.007))
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), ZAPALLO, colores)]


def camote_entero(x, y, z, angulo=0.0):
    malla = organico((0.066, 0.024, 0.022), 0.0015, 0.04, 83, 3)
    v = np.array(malla.vertices)
    punta = 1 - 0.5 * (v[:, 0] / 0.066) ** 2
    v[:, 1] *= punta
    v[:, 2] *= punta
    malla.vertices = v
    colores = motas(malla, (0.70, 0.38, 0.34), (0.56, 0.27, 0.25), 0.03, 0.2, 84)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.021), Material(CAMOTE_PIEL, 0.75), colores)]


def trozo_cocido(x, y, z, material, claro):
    semilla = int(rng.integers(1000))
    malla = organico(rng.uniform(0.018, 0.026, 3), 0.003, 0.02, semilla, 3)
    girar(malla, rng.uniform(0, np.pi))
    colores = motas(malla, material.color, claro, 0.012, 0.2, semilla + 1)
    return pintar(mover(malla, x, y, z), material, colores)


def monticulo(radio, alto, material, sombra=None, semilla=0):
    perfil = [(0, alto), (radio * 0.45, alto * 0.9), (radio * 0.85, alto * 0.45), (radio, 0), (0, 0)]
    malla = relieve(torno(perfil[::-1], 48, paso=0.004), radio * 0.03, radio * 0.4, semilla)
    colores = motas(malla, material.color, sombra, radio * 0.3, 0.2, semilla + 1) if sombra else None
    return pintar(malla, material, colores)


def cono_chancaca(x, y, z):
    perfil = [(0, 0), (0.034, 0), (0.024, 0.04), (0, 0.04)]
    malla = relieve(torno(perfil, 48, paso=0.004), 0.0008, 0.008, 87)
    colores = motas(malla, CHANCACA.color, CHANCACA_CLARA, 0.01, 0.25, 88)
    return [pintar(mover(malla, x, y, z), CHANCACA, colores)]


def rama_canela(x, y, z, angulo=0.0, largo=0.085):
    recorrido = np.column_stack([np.linspace(-largo / 2, largo / 2, 10), np.zeros(10), np.zeros(10)])
    malla = tubo(recorrido, 0.0045, lados=12, seccion=lambda a: 1 + 0.18 * np.cos(a * 2))
    colores = motas(malla, CANELA.color, (0.36, 0.18, 0.08), 0.01, 0.2, int(rng.integers(1000)))
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.0045), CANELA, colores)]


def cascara_naranja(x, y, z, angulo=0.0):
    recorrido = curva([(-0.035, 0.008, 0), (-0.012, -0.006, 0.006), (0.012, 0.006, 0.004), (0.035, -0.008, 0)], 20)
    malla = tubo(recorrido, husillo(20, 0.0022, 0.1, 0.1), lados=10, ancho=4.5)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.0025), NARANJA)]


def paso_1():
    piezas = mover(olla() + agua(0.081, 0.076), x=-0.095)
    for giro, material, claro in [(0.4, ZAPALLO, ZAPALLO_CLARO), (2.5, CAMOTE, (0.98, 0.66, 0.24)), (4.6, ZAPALLO, ZAPALLO_CLARO)]:
        piezas.append(trozo_cocido(-0.095 + 0.04 * np.cos(giro), 0.04 * np.sin(giro), 0.068, material, claro))
    piezas.append(trozo_cocido(-0.095, 0.0, 0.07, CAMOTE, (0.98, 0.66, 0.24)))
    piezas += mover(tabla(0.22, 0.2), x=0.13)
    piezas += trozo_zapallo(0.115, 0.04, ALTURA_TABLA, 0.2)
    piezas += camote_entero(0.14, -0.045, ALTURA_TABLA, -0.15)
    return piezas


def paso_2():
    piezas = tabla(0.38, 0.26)
    cuenco = bol(0.09, 0.06)
    perfil = [(0, 0.02), (0.068, 0.02), (0.073, 0.036), (0.062, 0.056), (0.034, 0.072), (0, 0.077)]
    masa = relieve(torno(curva(perfil, 24), 64, paso=0.004), 0.0025, 0.018, 91)
    cuenco.append(pintar(masa, MASA, motas(masa, MASA.color, MASA_SOMBRA, 0.012, 0.25, 92)))
    piezas += mover(cuenco, x=-0.07, z=ALTURA_TABLA)
    harina = bol(0.042, 0.028, 0.0035)
    harina.append(mover(monticulo(0.034, 0.022, HARINA, None, 93), z=0.012))
    piezas += mover(harina, 0.095, 0.055, ALTURA_TABLA)
    piezas += trozo_zapallo(0.1, -0.055, ALTURA_TABLA, 0.5, 0.05, 0.036, 0.026)
    return piezas


def paso_3():
    piezas = sarten(0.125)
    nivel = 0.018
    piezas.append(pintar(disco(0.108, 0.002, nivel, bisel=0.0005), ACEITE))
    for k, giro in enumerate(np.linspace(0, 2 * np.pi, 4, endpoint=False) + 0.4):
        piezas.append(rosca(0.06 * np.cos(giro), 0.06 * np.sin(giro), nivel - 0.011, coccion=[0.15, 0.5, 0.8, 1.0][k]))
    palito = tubo([(0.015, -0.015, nivel + 0.006), (0.13, -0.11, 0.07), (0.2, -0.17, 0.105)], 0.0028, lados=8)
    piezas.append(pintar(palito, PALITO))
    return piezas


def paso_4():
    radio, alto = 0.065, 0.06
    cazo = olla(radio, alto)
    cazo.append(pintar(disco(radio - 0.004, 0.002, alto * 0.62, bisel=0.0005), MIEL))
    piezas = mover(cazo, x=-0.095)
    piezas += mover(tabla(0.22, 0.2), x=0.115)
    piezas += cono_chancaca(0.085, 0.04, ALTURA_TABLA)
    piezas += rama_canela(0.145, 0.05, ALTURA_TABLA, 0.5)
    piezas += rama_canela(0.155, 0.03, ALTURA_TABLA, 0.2)
    piezas += cascara_naranja(0.12, -0.05, ALTURA_TABLA, 0.3)
    return piezas


def paso_5():
    piezas = plato(0.15)
    charco = disco(0.07, 0.0018, ALTURA_PLATO - 0.0004, bisel=0.0007, paso=0.006, secciones=64)
    v = np.array(charco.vertices)
    giro = np.arctan2(v[:, 1], v[:, 0])
    factor = 1 + 0.08 * np.sin(giro * 3 + 1) + 0.05 * np.sin(giro * 5)
    v[:, 0] *= factor
    v[:, 1] *= factor
    charco.vertices = v
    piezas.append(pintar(charco, CHARCO, motas(charco, CHARCO.color, MIEL.color, 0.03, 0.0, 95)))
    for giro in np.linspace(0, 2 * np.pi, 3, endpoint=False) + 0.5:
        piezas.append(rosca(0.048 * np.cos(giro), 0.048 * np.sin(giro), ALTURA_PLATO + 0.001, 0.03, 0.0125, miel=True))
    piezas.append(rosca(0.0, 0.0, ALTURA_PLATO + 0.019, 0.03, 0.0125, miel=True, inclinacion=0.12, angulo=0.8))
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
