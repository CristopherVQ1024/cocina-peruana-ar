"""Aji de gallina, un modelo por paso."""

import numpy as np

from base import (
    ALTURA_PLATO,
    ALTURA_SARTEN,
    ALTURA_TABLA,
    Material,
    aceituna,
    agua,
    aji,
    bol,
    cuchara_palo,
    curva,
    disco,
    escalon,
    extruir,
    girar,
    mezcla,
    motas,
    mover,
    olla,
    organico,
    pintar,
    plato,
    radio_bol,
    rectangulo,
    relieve,
    rodaja_huevo,
    sarten,
    tabla,
    timbal_arroz,
    torno,
    tubo,
)

ID = "aji-de-gallina"
rng = np.random.default_rng(73)

POLLO = Material((0.93, 0.87, 0.74), 0.75)
HEBRA = (0.84, 0.74, 0.56)
CREMA = Material((0.96, 0.76, 0.24), 0.4)
CREMA_SOMBRA = (0.90, 0.62, 0.14)
PAN = Material((0.96, 0.91, 0.78), 0.85)
CORTEZA = (0.72, 0.48, 0.22)
LECHE = Material((0.97, 0.96, 0.92), 0.2)
PECANA = Material((0.52, 0.31, 0.16), 0.6)
PECANA_SURCO = (0.30, 0.16, 0.08)
ADEREZO = Material((0.93, 0.60, 0.14), 0.45)
ADEREZO_CEBOLLA = (0.97, 0.86, 0.62)
PAPA_AMARILLA = Material((0.97, 0.84, 0.42), 0.7)
PAPA_SOMBRA = (0.90, 0.70, 0.28)


def hebras(x, y, altura, radio, cantidad):
    # altura es una funcion de la distancia al centro
    piezas = []
    for _ in range(cantidad):
        r = radio * np.sqrt(rng.uniform())
        giro = rng.uniform(0, 2 * np.pi)
        largo = rng.uniform(0.012, 0.022)
        hebra = tubo(curva([(-largo / 2, 0, 0), (0, rng.uniform(-0.003, 0.003), 0.0014), (largo / 2, 0, 0)], 6), 0.0013, lados=6)
        girar(hebra, rng.uniform(0, np.pi))
        tono = mezcla(POLLO.color, HEBRA, np.full(len(hebra.vertices), rng.uniform(0.1, 0.9)))
        piezas.append(pintar(mover(hebra, x + r * np.cos(giro), y + r * np.sin(giro), altura(r)), POLLO, tono))
    return piezas


def pechuga(x, y, z, angulo=0.0):
    semilla = int(rng.integers(1000))
    malla = organico((0.058, 0.036, 0.02), 0.002, 0.03, semilla, 3)
    v = np.array(malla.vertices)
    v[:, 1] *= 1 - 0.45 * escalon(v[:, 0], -0.01, 0.058)
    malla.vertices = v
    fibra = escalon(ruido_fibra(malla, semilla), 0.2, 0.8)
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.02), POLLO, mezcla(POLLO.color, HEBRA, fibra * 0.7))


def ruido_fibra(malla, semilla):
    return np.sin(malla.vertices[:, 1] / 0.004 * np.pi + semilla) * 0.5 + 0.5


def monton_hebras(x, y, z, radio=0.042, alto=0.022):
    perfil = [(0, 0), (radio, 0), (radio * 0.85, alto * 0.45), (radio * 0.45, alto * 0.9), (0, alto)]
    malla = relieve(torno(perfil, 48, paso=0.003), 0.0018, 0.006, 15)
    piezas = [pintar(mover(malla, x, y, z), POLLO, motas(malla, POLLO.color, HEBRA, 0.004, 0.2, 16))]
    return piezas + hebras(x, y, lambda r: z + alto + 0.001 - alto * 0.9 * (r / radio) ** 2, radio * 0.85, 40)


def trozo_pan(x, y, z):
    semilla = int(rng.integers(1000))
    malla = organico(rng.uniform(0.013, 0.02, 3), 0.002, 0.012, semilla, 3)
    girar(malla, rng.uniform(0, np.pi))
    return pintar(mover(malla, x, y, z), PAN, motas(malla, PAN.color, CORTEZA, 0.014, 0.45, semilla + 1))


def rebanada(x, y, z, angulo=0.0):
    lado = 0.088
    malla = extruir(rectangulo(lado, lado, 0.014, 5), 0.012, bisel=0.002, niveles=2, anillos=7)
    v = malla.vertices
    borde = escalon(np.maximum(np.abs(v[:, 0]), np.abs(v[:, 1])), lado / 2 - 0.006, lado / 2 - 0.002)
    colores = mezcla(motas(malla, PAN.color, (0.90, 0.83, 0.66), 0.008, 0.3, 21), CORTEZA, borde)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), PAN, colores)]


def pecana(x, y, z):
    malla = organico((0.012, 0.0075, 0.005), 0.0006, 0.006, int(rng.integers(1000)), 3)
    v = malla.vertices
    surco = (1 - escalon(np.abs(v[:, 1]), 0.0, 0.0018)) * 0.8 + np.abs(np.sin(v[:, 0] / 0.004 * np.pi)) ** 6 * 0.4
    colores = mezcla(PECANA.color, PECANA_SURCO, surco)
    girar(malla, rng.uniform(0, 2 * np.pi))
    return pintar(mover(malla, x, y, z + 0.005), PECANA, colores)


def rodaja_papa(x, y, z, angulo=0.0):
    malla = disco(0.026, 0.012, bisel=0.003, paso=0.004, secciones=40)
    malla.apply_scale([1.18, 1.0, 1.0])
    colores = motas(malla, PAPA_AMARILLA.color, PAPA_SOMBRA, 0.014, 0.3, int(rng.integers(1000)))
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), PAPA_AMARILLA, colores)]


def cuchara(x, y, z, inclinacion, angulo):
    piezas = cuchara_palo()
    girar(piezas, -inclinacion, (0, 1, 0))
    girar(piezas, angulo)
    return mover(piezas, x, y, z)


def paso_1():
    piezas = mover(olla() + agua(0.081, 0.076), x=-0.095)
    piezas.append(pechuga(-0.118, 0.014, 0.05, 0.5))
    piezas.append(pechuga(-0.072, -0.02, 0.052, 2.4))
    piezas += mover(tabla(0.22, 0.2), x=0.13)
    piezas += monton_hebras(0.1, 0.045, ALTURA_TABLA)
    piezas.append(pechuga(0.15, -0.055, ALTURA_TABLA, 0.2))
    return piezas


def paso_2():
    piezas = tabla(0.38, 0.26)
    radio, alto, grosor = 0.075, 0.05, 0.004
    cuenco = bol(radio, alto, grosor)
    nivel = 0.03
    cuenco.append(pintar(disco(radio_bol(radio, alto, grosor, nivel) - 0.0005, 0.002, nivel, bisel=0.0005), LECHE))
    for giro in np.linspace(0, 2 * np.pi, 5, endpoint=False) + 0.3:
        cuenco.append(trozo_pan(0.034 * np.cos(giro), 0.034 * np.sin(giro), nivel + 0.002))
    cuenco.append(trozo_pan(0, 0, nivel + 0.006))
    piezas += mover(cuenco, x=-0.09, z=ALTURA_TABLA)
    piezas += rebanada(0.05, 0.06, ALTURA_TABLA, 0.15)
    piezas += rebanada(0.058, 0.055, ALTURA_TABLA + 0.012, -0.2)
    piezas += aji(0.045, -0.05, ALTURA_TABLA, 0.2)
    piezas += aji(0.06, -0.085, ALTURA_TABLA, -0.2)
    for cx, cy in [(0.14, 0.0), (0.155, -0.02), (0.13, -0.025), (0.15, 0.022), (0.165, 0.002)]:
        piezas.append(pecana(cx, cy, ALTURA_TABLA))
    return piezas


def paso_3():
    piezas = sarten(0.125)
    z = ALTURA_SARTEN
    perfil = [(0, z), (0.098, z), (0.1, z + 0.005), (0.07, z + 0.008), (0, z + 0.009)]
    aderezo = relieve(torno(perfil, 96, paso=0.003), 0.0012, 0.006, 31)
    colores = motas(aderezo, ADEREZO.color, ADEREZO_CEBOLLA, 0.006, 0.3, 32)
    colores = mezcla(colores, CREMA_SOMBRA, escalon(np.linalg.norm(aderezo.vertices[:, :2], axis=1), 0.07, 0.1) * 0.5)
    piezas.append(pintar(aderezo, ADEREZO, colores))
    piezas += cuchara(0.0, -0.01, z + 0.011, 0.16, 0.9)
    return piezas


def paso_4():
    radio, alto = 0.095, 0.08
    piezas = olla(radio, alto)
    nivel = 0.052
    crema = relieve(disco(radio - 0.004, 0.004, nivel, bisel=0.001, paso=0.004), 0.0012, 0.02, 41)
    piezas.append(pintar(crema, CREMA, motas(crema, CREMA.color, CREMA_SOMBRA, 0.02, 0.2, 42)))
    piezas += hebras(0, 0, lambda r: nivel + 0.0045, 0.078, 46)
    piezas += cuchara(-0.03, 0.0, nivel + 0.004, 0.9, 0.5)
    return piezas


def paso_5():
    piezas = plato(0.16)
    x, y = -0.03, -0.012
    largo, ancho, alto = 0.064, 0.05, 0.014
    centro = ALTURA_PLATO + 0.011
    piezas += rodaja_papa(-0.088, 0.03, ALTURA_PLATO, 1.3)
    piezas += rodaja_papa(-0.094, -0.012, ALTURA_PLATO, 1.7)
    piezas += rodaja_papa(-0.078, -0.052, ALTURA_PLATO, 2.2)
    crema = organico((largo, ancho, alto), 0.0025, 0.022, 51, 4)
    colores = motas(crema, CREMA.color, HEBRA, 0.007, 0.35, 52)
    colores = mezcla(colores, CREMA_SOMBRA, escalon(ruido_fibra(crema, 1), 0.6, 1.0) * 0.25)
    piezas.append(pintar(mover(crema, x, y, centro), CREMA, colores))

    def cima(dx, dy):
        return centro + alto * np.sqrt(max(0.0, 1 - (dx / largo) ** 2 - (dy / ancho) ** 2))

    for _ in range(26):
        r = 0.04 * np.sqrt(rng.uniform())
        giro = rng.uniform(0, 2 * np.pi)
        dx, dy = r * np.cos(giro), r * np.sin(giro) * 0.8
        piezas += hebras(x + dx, y + dy, lambda _: cima(dx, dy) + 0.0008, 0.0, 1)
    piezas += rodaja_huevo(x + 0.014, y - 0.014, cima(0.014, -0.014) + 0.001, -0.4, 0.1)
    piezas += aceituna(x - 0.022, y + 0.014, cima(-0.022, 0.014) - 0.001, 0.6)
    piezas += timbal_arroz(0.058, 0.04, ALTURA_PLATO, 0.04, 0.032, 8)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
