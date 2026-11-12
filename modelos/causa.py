"""Causa limena, un modelo por paso."""

import numpy as np

from base import (
    ALTURA_PLATO,
    ALTURA_TABLA,
    TALLO,
    Material,
    aceituna,
    agua,
    anillo,
    bol,
    curva,
    disco,
    escalon,
    girar,
    mezcla,
    motas,
    mover,
    olla,
    organico,
    pintar,
    plato,
    relieve,
    rodaja_huevo,
    ruido,
    tabla,
    torno,
    tubo,
)

ID = "causa-limena"
rng = np.random.default_rng(7)

PAPA = Material((0.82, 0.64, 0.32), 0.8)
PAPA_OJO = (0.55, 0.38, 0.18)
MASA = Material((0.97, 0.78, 0.20), 0.65)
MASA_SOMBRA = (0.91, 0.66, 0.12)
PALTA = Material((0.60, 0.72, 0.28), 0.5)
PALTA_CLARA = (0.86, 0.86, 0.50)
POLLO = Material((0.93, 0.87, 0.74), 0.75)
HEBRA = (0.84, 0.74, 0.56)
LIMON = Material((0.36, 0.58, 0.14), 0.45)
PULPA = Material((0.80, 0.87, 0.45), 0.3)
PULPA_GAJO = (0.93, 0.95, 0.78)
AJI = Material((0.96, 0.56, 0.08), 0.28)
ACRILICO = Material((0.92, 0.95, 0.97), 0.08, 0.0, 0.25)
PEREJIL = Material((0.18, 0.48, 0.16), 0.7)

RADIO_ARO = 0.040
RADIO_CAPA = 0.0395


def papa(x, y, z, escala=1.0):
    semilla = int(rng.integers(1000))
    malla = organico(np.array([0.036, 0.026, 0.022]) * escala, 0.003, 0.035, semilla)
    colores = motas(malla, PAPA.color, PAPA_OJO, 0.011, 0.5, semilla + 1)
    colores = mezcla(colores, PAPA_OJO, escalon(ruido(malla.vertices, 0.05, semilla + 2), 0.2, 1.0) * 0.35)
    girar(malla, rng.uniform(0, np.pi))
    return pintar(mover(malla, x, y, z + 0.022 * escala), PAPA, colores)


def medio_limon(x, y, z, angulo=0.0):
    radio = 0.021
    arco = [(radio * np.sin(a), radio * 0.85 * (1 - np.cos(a))) for a in np.linspace(0, np.pi / 2, 9)]
    alto = arco[-1][1]
    cascara = torno(arco + [(0, alto)], 40)
    pulpa = disco(radio - 0.002, 0.0012, alto - 0.0004, bisel=0.0004, paso=0.002, secciones=48)
    giro = np.arctan2(pulpa.vertices[:, 1], pulpa.vertices[:, 0])
    distancia = np.linalg.norm(pulpa.vertices[:, :2], axis=1) / (radio - 0.002)
    gajos = np.abs(np.sin(giro * 4)) ** 0.25
    colores = mezcla(PULPA_GAJO, PULPA.color, gajos * escalon(distancia, 0.1, 0.25))
    colores = mezcla(colores, PULPA_GAJO, escalon(distancia, 0.86, 0.95))
    piezas = [pintar(cascara, LIMON), pintar(pulpa, PULPA, colores)]
    girar(piezas, angulo)
    return mover(piezas, x, y, z)


def aji_amarillo(x, y, z, angulo=0.0):
    recorrido = curva([(-0.055, 0, 0), (-0.02, 0.005, 0), (0.02, 0.003, 0), (0.058, -0.008, 0)], 28)
    t = np.linspace(0, 1, 28)
    radios = 0.0135 * np.sqrt(np.clip(t / 0.07, 0, 1)) * (1 - t) ** 0.65 + 0.0008
    cuerpo = tubo(recorrido, radios, lados=18)
    cabo = tubo(curva([(-0.054, 0, 0.002), (-0.064, 0, 0.006), (-0.072, 0.002, 0.014)], 8), 0.0026, lados=8)
    piezas = [pintar(cuerpo, AJI), pintar(cabo, TALLO)]
    girar(piezas, angulo)
    return mover(piezas, x, y, z + 0.0135)


def capa(z, alto, material, sombra, tamano=0.006, semilla=0, radio=RADIO_CAPA):
    malla = disco(radio, alto, z, bisel=0.0012, paso=0.003)
    relieve(malla, 0.0005, 0.007, semilla)
    return pintar(malla, material, motas(malla, material.color, sombra, tamano, 0.25, semilla + 1))


def aro(alto=0.075):
    return pintar(anillo(RADIO_ARO, RADIO_ARO + 0.002, alto, ALTURA_PLATO), ACRILICO)


def pollo_deshilachado(z):
    perfil = [(0, z), (RADIO_CAPA - 0.001, z), (RADIO_CAPA - 0.001, z + 0.009), (0.028, z + 0.015), (0, z + 0.018)]
    monton = relieve(torno(perfil, 64, paso=0.003), 0.0016, 0.006, 11)
    piezas = [pintar(monton, POLLO, motas(monton, POLLO.color, HEBRA, 0.004, 0.2, 12))]
    for _ in range(34):
        r = 0.033 * np.sqrt(rng.uniform())
        giro = rng.uniform(0, 2 * np.pi)
        largo = rng.uniform(0.010, 0.018)
        hebra = tubo(curva([(-largo / 2, 0, 0), (0, rng.uniform(-0.002, 0.002), 0.0012), (largo / 2, 0, 0)], 6), 0.0011, lados=6)
        girar(hebra, rng.uniform(0, np.pi))
        altura = z + 0.0185 - (r / RADIO_CAPA) ** 2 * 0.008
        tono = mezcla(POLLO.color, HEBRA, np.full(len(hebra.vertices), rng.uniform(0.2, 1.0)))
        piezas.append(pintar(mover(hebra, r * np.cos(giro), r * np.sin(giro), altura), POLLO, tono))
    return piezas


def perejil(x, y, z):
    hojas = []
    for _ in range(7):
        hoja = organico((0.0065, 0.004, 0.0007), 0.0006, 0.004, int(rng.integers(100)), 2)
        girar(hoja, rng.uniform(-0.5, 0.5), (1, 0, 0))
        girar(hoja, rng.uniform(0, 2 * np.pi))
        mover(hoja, x + rng.uniform(-0.007, 0.007), y + rng.uniform(-0.007, 0.007), z + rng.uniform(0.001, 0.004))
        hojas.append(pintar(hoja, PEREJIL))
    return hojas


def base_causa(capas):
    # apila las capas sobre el plato y devuelve tambien la altura final
    piezas = plato()
    z = ALTURA_PLATO
    for i, (alto, material, sombra) in enumerate(capas):
        piezas.append(capa(z, alto, material, sombra, semilla=20 + i * 3))
        z += alto
    return piezas, z


def paso_1():
    piezas = mover(olla() + agua(0.081, 0.076), x=-0.06)
    for giro in np.linspace(0, 2 * np.pi, 5)[:-1]:
        piezas.append(papa(-0.06 + 0.036 * np.cos(giro + 0.5), 0.036 * np.sin(giro + 0.5), 0.05, rng.uniform(0.85, 1.0)))
    piezas.append(papa(0.10, -0.045, 0.0, 1.05))
    piezas.append(papa(0.135, 0.04, 0.0, 0.9))
    piezas.append(papa(0.075, 0.065, 0.0, 0.95))
    return piezas


def paso_2():
    piezas = tabla(0.36, 0.24)
    vajilla = bol()
    perfil = [(0, 0.02), (0.060, 0.02), (0.064, 0.035), (0.055, 0.053), (0.03, 0.067), (0, 0.071)]
    masa = relieve(torno(curva(perfil, 24), 64, paso=0.004), 0.0022, 0.02, 4)
    vajilla.append(pintar(masa, MASA, motas(masa, MASA.color, MASA_SOMBRA, 0.012, 0.2, 5)))
    piezas += mover(vajilla, x=-0.055, z=ALTURA_TABLA)
    piezas += medio_limon(0.075, -0.07, ALTURA_TABLA, 0.4)
    piezas += medio_limon(0.125, -0.035, ALTURA_TABLA, 1.3)
    piezas += aji_amarillo(0.095, 0.055, ALTURA_TABLA, 0.35)
    return piezas


def paso_3():
    piezas, _ = base_causa([(0.022, MASA, MASA_SOMBRA)])
    return piezas + [aro()]


def paso_4():
    piezas, z = base_causa([(0.022, MASA, MASA_SOMBRA), (0.010, PALTA, PALTA_CLARA)])
    return piezas + pollo_deshilachado(z) + [aro()]


def paso_5():
    piezas, z = base_causa(
        [
            (0.022, MASA, MASA_SOMBRA),
            (0.010, PALTA, PALTA_CLARA),
            (0.014, POLLO, HEBRA),
            (0.022, MASA, MASA_SOMBRA),
        ]
    )
    piezas += rodaja_huevo(-0.013, 0.006, z + 0.003, 0.5, -0.28)
    piezas += rodaja_huevo(0.010, -0.010, z + 0.002, -0.7, 0.22)
    piezas += aceituna(0.008, 0.019, z, 0.6)
    piezas += perejil(-0.016, -0.018, z)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
