from typing import Literal

from pydantic import BaseModel, Field

Idioma = Literal["es", "en", "pt", "fr"]


class Ingrediente(BaseModel):
    nombre: str
    cantidad: str


class Paso(BaseModel):
    numero: int
    titulo: str
    descripcion: str
    duracion_min: int
    modelo: str


class Plato(BaseModel):
    id: str
    nombre: str
    region: str
    resumen: str
    historia: str
    porciones: int
    ingredientes: list[Ingrediente]
    pasos: list[Paso]


class PlatoResumen(BaseModel):
    id: str
    nombre: str
    region: str
    resumen: str
    modelo: str


class Mensaje(BaseModel):
    rol: Literal["usuario", "asistente"]
    texto: str


class PreguntaAsistente(BaseModel):
    plato_id: str
    pregunta: str = Field(min_length=1, max_length=500)
    idioma: Idioma = "es"
    paso: int | None = None
    historial: list[Mensaje] = Field(default_factory=list, max_length=10)


class RespuestaAsistente(BaseModel):
    respuesta: str
    fuera_de_ficha: bool = Field(description="true si la pregunta no se puede responder con la ficha del plato")
