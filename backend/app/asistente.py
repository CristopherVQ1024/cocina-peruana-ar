from functools import lru_cache

from google import genai
from google.genai import types

from .config import get_settings
from .esquemas import Plato, PreguntaAsistente, RespuestaAsistente

NOMBRES_IDIOMA = {"es": "español", "en": "inglés", "pt": "portugués", "fr": "francés"}

INSTRUCCIONES = """Eres un guía de cocina peruana dentro de una aplicación que muestra platos en 3D y realidad aumentada.
Respondes preguntas de turistas y estudiantes sobre el plato usando SOLO la ficha que se te entrega.
Reglas:
- Si la respuesta no está en la ficha, dilo con amabilidad, marca fuera_de_ficha en true y sugiere una pregunta que sí puedas responder. No inventes datos, fechas ni cifras.
- Responde en {idioma}, en texto plano sin markdown, en un máximo de 120 palabras.
- Si te preguntan por el paso actual, usa el número de paso indicado.
- Puedes traducir o explicar nombres de ingredientes, pero sin cambiar la receta."""

INSTRUCCIONES_TRADUCCION = """Traduce al {idioma} todos los textos de esta ficha de un plato peruano.
Mantén sin traducir los nombres propios de platos e ingredientes típicos (causa, ají amarillo, papa amarilla, aceituna de botija, tacacho, cecina, cocona, ají charapita, rocoto, ají panca, queso paria) y añade entre paréntesis una explicación breve la primera vez que aparezcan.
No cambies id, numero, duracion_min, porciones ni modelo."""


class Asistente:
    def __init__(self, api_key: str, modelo: str):
        self._cliente = genai.Client(api_key=api_key)
        self._modelo = modelo
        self._traducciones: dict[tuple[str, str], Plato] = {}

    async def responder(self, plato: Plato, pregunta: PreguntaAsistente) -> RespuestaAsistente:
        contexto = f"FICHA DEL PLATO:\n{plato.model_dump_json(indent=1)}"
        if pregunta.paso:
            contexto += f"\n\nEl usuario está viendo el paso {pregunta.paso}."
        contenidos = [types.Content(role="user", parts=[types.Part(text=contexto)])]
        for mensaje in pregunta.historial:
            rol = "user" if mensaje.rol == "usuario" else "model"
            contenidos.append(types.Content(role=rol, parts=[types.Part(text=mensaje.texto)]))
        contenidos.append(types.Content(role="user", parts=[types.Part(text=pregunta.pregunta)]))

        respuesta = await self._cliente.aio.models.generate_content(
            model=self._modelo,
            contents=contenidos,
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCCIONES.format(idioma=NOMBRES_IDIOMA[pregunta.idioma]),
                response_mime_type="application/json",
                response_schema=RespuestaAsistente,
                temperature=0.3,
            ),
        )
        return RespuestaAsistente.model_validate_json(respuesta.text)

    async def traducir(self, plato: Plato, idioma: str) -> Plato:
        clave = (plato.id, idioma)
        if clave not in self._traducciones:
            respuesta = await self._cliente.aio.models.generate_content(
                model=self._modelo,
                contents=plato.model_dump_json(),
                config=types.GenerateContentConfig(
                    system_instruction=INSTRUCCIONES_TRADUCCION.format(idioma=NOMBRES_IDIOMA[idioma]),
                    response_mime_type="application/json",
                    response_schema=Plato,
                    temperature=0.1,
                ),
            )
            traducido = Plato.model_validate_json(respuesta.text)
            # los datos estructurales se toman del original por si el modelo los altera
            for original, paso in zip(plato.pasos, traducido.pasos):
                paso.numero, paso.modelo, paso.duracion_min = original.numero, original.modelo, original.duracion_min
            traducido.id, traducido.nombre = plato.id, plato.nombre
            self._traducciones[clave] = traducido
        return self._traducciones[clave]


@lru_cache
def get_asistente() -> Asistente | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    return Asistente(settings.gemini_api_key, settings.gemini_model)
