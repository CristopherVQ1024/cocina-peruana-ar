"""Lomo saltado, un modelo por paso."""

import numpy as np

from base import (
    AJI,
    ALTURA_PLATO,
    ALTURA_TABLA,
    HIERRO,
    MANGO,
    TALLO,
    Material,
    aji,
    apoyar,
    curva,
    disco,
    escalon,
    extruir,
    girar,
    hojas_picadas,
    husillo,
    mezcla,
    motas,
    mover,
    organico,
    pintar,
    plato,
    rectangulo,
    relieve,
    ruido,
    sarten,
    tabla,
    timbal_arroz,
    torno,
    tubo,
)

ID = "lomo-saltado"
rng = np.random.default_rng(67)

CARNE = Material((0.62, 0.13, 0.13), 0.5)
CARNE_GRASA = (0.90, 0.68, 0.62)
SALTEADA = Material((0.42, 0.23, 0.12), 0.55)
SALTEADA_OSCURA = (0.22, 0.11, 0.06)
TOMATE = Material((0.82, 0.12, 0.08), 0.25)
TOMATE_PULPA = (0.93, 0.40, 0.28)
TOMATE_SEMILLA = (0.96, 0.76, 0.46)
CEBOLLA = Material((0.58, 0.16, 0.38), 0.35)
CEBOLLA_CLARA = (0.96, 0.86, 0.90)
FRITA = Material((0.96, 0.78, 0.32), 0.6)
FRITA_DORADA = (0.78, 0.50, 0.16)
PAPA_CRUDA = (0.96, 0.90, 0.64)
ACEITE = Material((0.96, 0.76, 0.20), 0.05, 0.0, 0.5)
CULANTRO = Material((0.18, 0.48, 0.16), 0.7)
JUGO = Material((0.40, 0.21, 0.10), 0.7)

RADIO_WOK = 0.19
ALTO_WOK = 0.17
GROSOR_WOK = 0.003


def fondo_wok(r):
    # altura del interior del wok a una distancia r del centro
    return GROSOR_WOK + ALTO_WOK * (1 - np.sqrt(1 - np.clip(r / (RADIO_WOK - GROSOR_WOK), 0, 1) ** 2))


def wok():
    exterior = [(RADIO_WOK * np.sin(a), ALTO_WOK * (1 - np.cos(a))) for a in np.linspace(0, 1.0, 14)]
    interior = [
        ((RADIO_WOK - GROSOR_WOK) * np.sin(a), GROSOR_WOK + ALTO_WOK * (1 - np.cos(a)))
        for a in np.linspace(0.97, 0, 14)
    ]
    borde = exterior[-1][0]
    cuerpo = pintar(torno(exterior + interior, 96), HIERRO)
    recorrido = curva([(borde - 0.004, 0, 0.074), (borde + 0.06, 0, 0.088), (borde + 0.17, 0, 0.096)], 16)
    mango = pintar(tubo(recorrido, husillo(16, 0.009, 0.0, 0.05), lados=14, ancho=1.4), MANGO)
    arco = curva([(-borde + 0.002, -0.03, 0.074), (-borde - 0.02, -0.02, 0.08), (-borde - 0.02, 0.02, 0.08), (-borde + 0.002, 0.03, 0.074)], 16)
    asa = pintar(tubo(arco, 0.004, lados=10), HIERRO)
    return [cuerpo, mango, asa]


def cuarto(radios):
    # cuarto de elipsoide apoyado en una cara plana, devuelve la malla y los vertices de corte
    malla = organico(radios, subdivisiones=3)
    v = np.array(malla.vertices)
    v[:, 1] = np.maximum(v[:, 1], 0)
    v[:, 2] = np.maximum(v[:, 2], 0)
    malla.vertices = v
    malla.update_faces(malla.nondegenerate_faces())
    malla.remove_unreferenced_vertices()
    v = malla.vertices
    return malla, (v[:, 1] < 1e-9) | (v[:, 2] < 1e-9)


def soltar(malla, x, y, z, volteo=0.0):
    girar(malla, rng.uniform(-volteo, volteo) if volteo else 0.0, (1, 0, 0))
    girar(malla, rng.uniform(0, 2 * np.pi))
    return mover(apoyar(malla, z), x, y)


def gajo_tomate(escala=1.0):
    semilla = int(rng.integers(1000))
    malla, corte = cuarto(np.array([0.028, 0.03, 0.03]) * escala)
    pulpa = motas(malla, TOMATE_PULPA, TOMATE_SEMILLA, 0.006 * escala, 0.3, semilla)
    colores = mezcla(np.tile(TOMATE.color, (len(corte), 1)), pulpa, corte.astype(float))
    return pintar(malla, TOMATE, colores)


def gajo_cebolla(escala=1.0):
    malla, corte = cuarto(np.array([0.03, 0.017, 0.026]) * escala)
    v = malla.vertices
    capas = np.abs(np.sin(np.hypot(v[:, 1] / 0.017, v[:, 2] / 0.026) / escala * np.pi * 3.5)) ** 2
    interior = mezcla(CEBOLLA_CLARA, CEBOLLA.color, capas * 0.55)
    vetas = np.abs(np.sin(np.arctan2(v[:, 2], v[:, 1]) * 9)) ** 3
    piel = mezcla(CEBOLLA.color, CEBOLLA_CLARA, vetas * 0.3)
    return pintar(malla, CEBOLLA, mezcla(piel, interior, corte.astype(float)))


def tomate_entero(x, y, z):
    cuerpo = organico((0.031, 0.031, 0.026), 0.0012, 0.03, 5, 4)
    v = np.array(cuerpo.vertices)
    v[:, 2] -= 0.006 * np.exp(-(np.hypot(v[:, 0], v[:, 1]) / 0.012) ** 2) * (v[:, 2] > 0)
    cuerpo.vertices = v
    cabo = disco(0.008, 0.002, 0.021, bisel=0.0008, secciones=5)
    palo = tubo([(0, 0, 0.021), (0.001, 0, 0.027), (0.003, 0.001, 0.032)], 0.0018, lados=8)
    piezas = [pintar(cuerpo, TOMATE), pintar(cabo, TALLO), pintar(palo, TALLO)]
    return mover(piezas, x, y, z + 0.026)


def tira_carne(x, y, z, angulo=0.0, cocida=False, largo=0.055):
    n = 16
    semilla = int(rng.integers(1000))
    t = np.linspace(-0.5, 0.5, n)
    fase = rng.uniform(0, 6)
    recorrido = np.column_stack([t * largo, 0.004 * np.sin(t * 4 + fase), 0.0015 * np.sin(t * 9 + fase)])
    malla = tubo(recorrido, husillo(n, 0.0045, 0.15, 0.15), lados=12, ancho=2.3)
    if cocida:
        colores = motas(malla, SALTEADA.color, SALTEADA_OSCURA, 0.012, 0.0, semilla)
    else:
        veta = escalon(ruido(malla.vertices * [0.3, 1, 1], 0.01, semilla), 0.45, 0.7)
        colores = mezcla(CARNE.color, CARNE_GRASA, veta * 0.55)
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.006), SALTEADA if cocida else CARNE, colores)


def trozo_lomo(x, y, z, angulo=0.0):
    malla = organico((0.055, 0.032, 0.02), 0.002, 0.03, 9, 4)
    v = np.array(malla.vertices)
    v[:, 2] = np.maximum(v[:, 2], -0.012)
    malla.vertices = v
    veta = escalon(ruido(malla.vertices * [0.3, 1, 1], 0.014, 10), 0.5, 0.75)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z + 0.012), CARNE, mezcla(CARNE.color, CARNE_GRASA, veta * 0.6))]


def papa_frita(coccion=1.0, largo=0.055):
    malla = extruir(rectangulo(largo, 0.009, 0.002, 3), 0.009, bisel=0.0018, niveles=2, anillos=2)
    punta = escalon(np.abs(malla.vertices[:, 0]) / (largo / 2), 0.55, 1.0)
    dorada = mezcla(FRITA.color, FRITA_DORADA, punta * 0.8)
    return pintar(malla, FRITA, mezcla(PAPA_CRUDA, dorada, np.full(len(punta), coccion)))


def tira_aji(x, y, z, angulo=0.0):
    largo = rng.uniform(0.04, 0.05)
    recorrido = curva([(-largo / 2, 0, 0), (0, rng.uniform(-0.004, 0.004), 0.001), (largo / 2, 0, 0)], 10)
    malla = tubo(recorrido, husillo(10, 0.0028, 0.1, 0.1), lados=8, ancho=1.8)
    girar(malla, angulo)
    return pintar(mover(malla, x, y, z + 0.0028), AJI)


def carne_en_wok():
    piezas = []
    for radio, cantidad, fase in [(0.0, 1, 0.0), (0.045, 5, 0.3), (0.088, 9, 0.0)]:
        for giro in np.linspace(0, 2 * np.pi, cantidad, endpoint=False) + fase:
            r = radio + rng.uniform(-0.005, 0.005) if radio else 0.0
            piezas.append(tira_carne(r * np.cos(giro), r * np.sin(giro), fondo_wok(r) + 0.001, giro + np.pi / 2 + rng.uniform(-0.4, 0.4), True))
    return piezas


def verduras(x, y, altura, radio, cebollas, tomates, ajies, escala=0.75):
    # altura es una funcion de la distancia al centro
    piezas = []
    lista = [gajo_cebolla] * cebollas + [gajo_tomate] * tomates
    for i, forma in enumerate(lista):
        giro = i * 2.4 + 0.5
        r = radio * np.sqrt((i + 0.5) / len(lista))
        piezas.append(soltar(forma(escala), x + r * np.cos(giro), y + r * np.sin(giro), altura(r), 0.5))
    for i in range(ajies):
        giro = i * 2.4 + 1.7
        r = radio * np.sqrt((i + 0.5) / ajies) * 0.9
        piezas.append(tira_aji(x + r * np.cos(giro), y + r * np.sin(giro), altura(r) + 0.012, rng.uniform(0, np.pi)))
    return piezas


def paso_1():
    piezas = tabla(0.40, 0.27)
    piezas += trozo_lomo(-0.125, 0.065, ALTURA_TABLA, 0.15)
    for i in range(5):
        piezas.append(tira_carne(-0.165 + i * 0.027, -0.055 + rng.uniform(-0.004, 0.004), ALTURA_TABLA, np.pi / 2 + rng.uniform(-0.1, 0.1)))
    for i in range(4):
        gajo = girar(gajo_cebolla(), np.pi / 2 + rng.uniform(-0.15, 0.15))
        piezas.append(mover(gajo, -0.025 + i * 0.03, 0.06, ALTURA_TABLA))
    for i, (cx, cy) in enumerate([(0.0, -0.06), (0.045, -0.07), (0.085, -0.045)]):
        gajo = girar(gajo_tomate(), 1.2 + i * 0.5)
        piezas.append(mover(gajo, cx, cy, ALTURA_TABLA))
    piezas += tomate_entero(0.15, 0.075, ALTURA_TABLA)
    piezas += aji(0.13, 0.0, ALTURA_TABLA, 0.3)
    for i in range(4):
        piezas.append(tira_aji(0.135 + rng.uniform(-0.01, 0.01), -0.07 - i * 0.012, ALTURA_TABLA, rng.uniform(-0.2, 0.2)))
    return piezas


def paso_2():
    piezas = sarten(0.125)
    nivel = 0.016
    piezas.append(pintar(disco(0.107, 0.002, nivel, bisel=0.0005), ACEITE))
    for i in range(13):
        giro = i * 2.4
        r = 0.075 * np.sqrt((i + 0.5) / 13)
        frita = papa_frita(0.25 + 0.75 * i / 12, rng.uniform(0.045, 0.06))
        girar(frita, rng.uniform(-0.12, 0.12), (0, 1, 0))
        girar(frita, rng.uniform(0, np.pi))
        piezas.append(mover(frita, r * np.cos(giro), r * np.sin(giro), nivel - 0.005))
    return piezas


def paso_3():
    return wok() + carne_en_wok()


def paso_4():
    piezas = wok() + carne_en_wok()
    piezas += verduras(0, 0, lambda r: fondo_wok(r) + 0.011, 0.1, 7, 6, 6)
    for i in range(6):
        giro = i * 2.4 + 0.9
        r = 0.03 + 0.012 * i
        piezas += hojas_picadas(rng, r * np.cos(giro), r * np.sin(giro), fondo_wok(r) + 0.02, CULANTRO, 3, 0.008)
    return piezas


def paso_5():
    piezas = plato(0.165)
    x, y, z = -0.048, -0.008, ALTURA_PLATO
    perfil = [(0, z), (0.058, z), (0.052, z + 0.003), (0.03, z + 0.008), (0, z + 0.009)]
    jugo = relieve(torno(perfil, 48, paso=0.004), 0.0008, 0.012, 3)
    piezas.append(pintar(mover(jugo, x, y), JUGO, motas(jugo, JUGO.color, SALTEADA_OSCURA, 0.012, 0.1, 4)))
    for radio, cantidad, altura, fase in [(0.043, 9, 0.001, 0.0), (0.02, 5, 0.007, 0.6), (0.0, 1, 0.012, 0.0)]:
        for giro in np.linspace(0, 2 * np.pi, cantidad, endpoint=False) + fase:
            piezas.append(tira_carne(x + radio * np.cos(giro), y + radio * np.sin(giro), z + altura, giro + np.pi / 2 + rng.uniform(-0.5, 0.5), True, 0.05))
    piezas += verduras(x, y, lambda r: z + 0.022 - 0.012 * (r / 0.045) ** 2, 0.045, 4, 4, 4, 0.62)
    piezas += hojas_picadas(rng, x, y, z + 0.034, CULANTRO, 8, 0.03)
    piezas += timbal_arroz(0.05, 0.05, ALTURA_PLATO, 0.04, 0.032, 6)
    capas = [(0.0, 5, 0.25), (0.009, 4, 1.35), (0.018, 2, 0.4)]
    for altura, cantidad, angulo in capas:
        for i in range(cantidad):
            frita = papa_frita(1.0, rng.uniform(0.045, 0.058))
            girar(frita, angulo + rng.uniform(-0.35, 0.35))
            salto = (i - (cantidad - 1) / 2) * 0.011
            piezas.append(mover(frita, 0.05 - salto * np.sin(angulo), -0.052 + salto * np.cos(angulo), ALTURA_PLATO + altura))
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
