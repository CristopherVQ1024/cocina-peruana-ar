"""Rocoto relleno, un modelo por paso."""

import numpy as np

from base import (
    ALTURA_PLATO,
    ALTURA_SARTEN,
    ALTURA_TABLA,
    TALLO,
    Material,
    agua,
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
    redondear,
    relieve,
    ruido,
    sarten,
    tabla,
    torno,
    tubo,
)

ID = "rocoto-relleno"
rng = np.random.default_rng(23)

ROCOTO = Material((0.80, 0.08, 0.06), 0.22)
ROCOTO_HORNEADO = (0.42, 0.06, 0.04)
RELLENO = Material((0.44, 0.26, 0.15), 0.85)
RELLENO_PASA = (0.16, 0.08, 0.08)
RELLENO_MANI = (0.84, 0.70, 0.46)
QUESO = Material((0.97, 0.90, 0.64), 0.45)
QUESO_DORADO = (0.76, 0.47, 0.15)
BATIDO = Material((0.97, 0.91, 0.70), 0.2)
FUENTE = Material((0.74, 0.40, 0.24), 0.45)
CUCHARA = Material((0.72, 0.54, 0.34), 0.7)
PASTEL = Material((0.95, 0.87, 0.62), 0.7)
PASTEL_CAPA = (0.84, 0.70, 0.40)

ALTO_CORTE = 0.052
EXTERIOR = [(0, 0.003), (0.012, 0), (0.026, 0.008), (0.033, 0.028), (0.034, 0.043), (0.0325, ALTO_CORTE)]
HOMBRO = [(0.0325, ALTO_CORTE), (0.028, 0.062), (0.017, 0.069), (0.006, 0.066), (0, 0.064)]
INTERIOR = [(0.0285, ALTO_CORTE), (0.030, 0.043), (0.029, 0.028), (0.021, 0.012), (0, 0.009)]


def lobular(malla, fase, horneado=False):
    # da los gajos del rocoto y devuelve su color
    giro = np.arctan2(malla.vertices[:, 1], malla.vertices[:, 0])
    factor = 1 + 0.05 * np.cos(4 * giro + fase)
    malla.vertices = malla.vertices * np.column_stack([factor, factor, np.ones(len(factor))])
    if not horneado:
        return None
    tostado = escalon(ruido(malla.vertices, 0.03, int(fase * 100)), 0.0, 0.9)
    return mezcla(ROCOTO.color, ROCOTO_HORNEADO, tostado * 0.6)


def cabo(z):
    recorrido = curva([(0, 0, z - 0.002), (0.001, 0, z + 0.01), (0.006, 0.002, z + 0.022)], 10)
    piezas = [tubo(recorrido, np.linspace(0.0045, 0.003, 10), lados=10)]
    piezas.append(disco(0.010, 0.003, z - 0.0015, bisel=0.0012, secciones=24))
    return [pintar(pieza, TALLO) for pieza in piezas]


def rocoto_entero(x, y, z, angulo=0.0):
    cuerpo = torno(np.vstack([curva(EXTERIOR, 16), curva(HOMBRO, 12)[1:]]), 48)
    lobular(cuerpo, angulo)
    piezas = [pintar(cuerpo, ROCOTO)] + cabo(0.065)
    girar(piezas, angulo)
    return mover(piezas, x, y, z)


def rocoto_hueco(x, y, z, angulo=0.0, horneado=False):
    cuerpo = torno(np.vstack([curva(EXTERIOR, 16), curva(INTERIOR, 12)]), 48)
    colores = lobular(cuerpo, angulo, horneado)
    girar(cuerpo, angulo)
    return [pintar(mover(cuerpo, x, y, z), ROCOTO, colores)]


def tapa(x, y, z, angulo=0.0, inclinacion=0.0, horneado=False):
    perfil = [(0, 0), (0.0325, 0)] + [(r, h - ALTO_CORTE) for r, h in curva(HOMBRO, 12)[1:]]
    cuerpo = torno(redondear(perfil, 0.0015), 48)
    colores = lobular(cuerpo, angulo, horneado)
    piezas = [pintar(cuerpo, ROCOTO, colores)] + cabo(0.065 - ALTO_CORTE)
    girar(piezas, inclinacion, (0, 1, 0))
    girar(piezas, angulo)
    return mover(piezas, x, y, z)


def color_relleno(malla, semilla):
    colores = motas(malla, RELLENO.color, RELLENO_PASA, 0.006, 0.45, semilla)
    return mezcla(colores, RELLENO_MANI, escalon(ruido(malla.vertices, 0.005, semilla + 1), 0.5, 0.65))


def relleno(x, y, z):
    semilla = int(rng.integers(1000))
    base = ALTO_CORTE - 0.006
    perfil = [(0, base), (0.0285, base), (0.0275, base + 0.007), (0.016, base + 0.012), (0, base + 0.013)]
    malla = relieve(torno(perfil, 40, paso=0.0025), 0.0012, 0.005, semilla)
    colores = color_relleno(malla, semilla)
    return [pintar(mover(malla, x, y, z), RELLENO, colores)]


def lamina_queso(x, y, z, angulo=0.0):
    malla = extruir(rectangulo(0.066, 0.066, 0.008), 0.004, bisel=0.001)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), QUESO)]


def queso_gratinado(x, y, z):
    semilla = int(rng.integers(1000))
    malla = organico((0.039, 0.039, 0.009), 0.0035, 0.02, semilla, 4)
    colores = motas(malla, QUESO.color, QUESO_DORADO, 0.012, 0.05, semilla + 1)
    return [pintar(mover(malla, x, y, z), QUESO, colores)]


def fuente(radio=0.12, alto=0.045):
    grosor = 0.006
    perfil = [
        (0, 0),
        (radio - 0.012, 0),
        (radio, alto),
        (radio + 0.006, alto + 0.002),
        (radio - grosor, alto),
        (radio - grosor - 0.01, grosor),
        (0, grosor),
    ]
    return [pintar(torno(redondear(perfil, 0.005), 96), FUENTE)]


def cuchara_palo():
    recorrido = curva([(0, 0, 0), (0.09, 0, 0.012), (0.19, 0, 0.03)], 14)
    mango = tubo(recorrido, 0.0055, lados=10, ancho=1.3)
    pala = organico((0.03, 0.019, 0.005), 0, 0.01, 0, 3)
    return [pintar(mango, CUCHARA), pintar(mover(pala, x=-0.022), CUCHARA)]


def pastel_papa(x, y, z, angulo=0.0):
    alto = 0.034
    malla = extruir(rectangulo(0.075, 0.058, 0.004, 4), alto, bisel=0.0015, niveles=22, anillos=7)
    altura = malla.vertices[:, 2]
    capas = np.abs(np.sin(altura / alto * np.pi * 4.5)) ** 6
    colores = mezcla(PASTEL.color, PASTEL_CAPA, capas * 0.9)
    dorado = escalon(altura, alto - 0.003, alto) * (0.55 + 0.45 * ruido(malla.vertices, 0.012, 41))
    colores = mezcla(colores, QUESO_DORADO, dorado)
    girar(malla, angulo)
    return [pintar(mover(malla, x, y, z), PASTEL, colores)]


def en_fuente(piezas_por_rocoto):
    piezas = fuente()
    for i, giro in enumerate(np.linspace(0, 2 * np.pi, 4)[:-1] + 0.5):
        x, y = 0.052 * np.cos(giro), 0.052 * np.sin(giro)
        piezas += rocoto_hueco(x, y, 0.006, giro) + relleno(x, y, 0.006)
        piezas += piezas_por_rocoto(i, x, y, giro)
    return piezas


def paso_1():
    piezas = mover(olla() + agua(0.081, 0.076), x=-0.095)
    piezas += rocoto_hueco(-0.125, 0.012, 0.037, 0.4)
    piezas += rocoto_hueco(-0.062, -0.018, 0.037, 1.7)
    piezas += mover(tabla(0.22, 0.2), x=0.13)
    piezas += rocoto_entero(0.085, 0.045, ALTURA_TABLA, 0.3)
    piezas += rocoto_hueco(0.16, 0.02, ALTURA_TABLA, 1.1)
    piezas += tapa(0.115, -0.045, ALTURA_TABLA, 0.8, 0.25)
    return piezas


def paso_2():
    piezas = sarten(0.125)
    perfil = [(0, ALTURA_SARTEN), (0.098, ALTURA_SARTEN), (0.1, ALTURA_SARTEN + 0.008), (0.07, ALTURA_SARTEN + 0.014), (0, ALTURA_SARTEN + 0.016)]
    carne = relieve(torno(perfil, 96, paso=0.003), 0.002, 0.006, 51)
    piezas.append(pintar(carne, RELLENO, color_relleno(carne, 52)))
    cuchara = cuchara_palo()
    girar(cuchara, -0.16, (0, 1, 0))
    girar(cuchara, 2.3)
    piezas += mover(cuchara, -0.02, 0.02, ALTURA_SARTEN + 0.018)
    return piezas


def paso_3():
    return en_fuente(lambda i, x, y, giro: [])


def paso_4():
    def cubierta(i, x, y, giro):
        piezas = lamina_queso(x, y, 0.006 + ALTO_CORTE + 0.005, giro)
        return piezas + tapa(x, y, 0.006 + ALTO_CORTE + 0.009, giro, 0.12)

    piezas = en_fuente(cubierta)
    piezas.append(pintar(disco(0.106, 0.012, 0.006, bisel=0.002), BATIDO))
    return piezas


def paso_5():
    piezas = plato(0.135)
    x, y = -0.042, -0.005
    piezas += rocoto_hueco(x, y, ALTURA_PLATO, 0.6, horneado=True)
    piezas += queso_gratinado(x, y, ALTURA_PLATO + ALTO_CORTE + 0.003)
    piezas += tapa(x + 0.004, y, ALTURA_PLATO + ALTO_CORTE + 0.009, 0.6, 0.2, horneado=True)
    piezas += pastel_papa(0.048, 0.005, ALTURA_PLATO, 0.25)
    return piezas


PASOS = [paso_1, paso_2, paso_3, paso_4, paso_5]
