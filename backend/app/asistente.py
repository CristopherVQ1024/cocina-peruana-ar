import asyncio
import logging
import time
from functools import lru_cache

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from .config import Settings, get_settings
from .esquemas import Plato, PreguntaAsistente, RespuestaAsistente

log = logging.getLogger("uvicorn.error")

NOMBRES_IDIOMA = {"es": "español", "en": "inglés", "pt": "portugués", "fr": "francés"}

INSTRUCCIONES = """Eres un guía de cocina peruana dentro de una aplicación que muestra platos en 3D y realidad aumentada.
Respondes preguntas de turistas y estudiantes sobre el plato usando SOLO la ficha que se te entrega.
Reglas:
- Si la respuesta no está en la ficha, dilo con amabilidad, marca fuera_de_ficha en true y sugiere una pregunta que sí puedas responder. No inventes datos, fechas ni cifras.
- Responde en {idioma}, en texto plano sin markdown, en un máximo de 120 palabras.
- Si te preguntan por el paso actual, usa el número de paso indicado.
- Puedes traducir o explicar nombres de ingredientes, pero sin cambiar la receta."""

INSTRUCCIONES_TRADUCCION = """Traduce al {idioma} todos los textos de esta ficha de un plato peruano.
Mantén sin traducir los nombres propios de platos e ingredientes típicos (causa, ají amarillo, papa amarilla, aceituna de botija, tacacho, cecina, cocona, ají charapita, rocoto, ají panca, queso paria, ceviche, leche de tigre, ají limo, cancha, choclo, camote, huancaína, picarones, chancaca, zapallo macre, lomo saltado, sillao, ají de gallina, anticuchos, ají mirasol) y añade entre paréntesis una explicación breve la primera vez que aparezcan.
No cambies id, numero, duracion_min, porciones ni modelo."""


def pasa_al_respaldo(error: Exception) -> bool:
    # cambia de modelo salvo con clave invalida u otro error 4xx
    if isinstance(error, errors.APIError):
        return error.code in (404, 429) or (error.code or 0) >= 500
    return True


class Asistente:
    def __init__(self, settings: Settings):
        # sin reintentos internos del cliente
        self._cliente = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=1)),
        )
        nombres = [settings.gemini_model, *settings.gemini_fallback_models.split(",")]
        self.modelos = list(dict.fromkeys(n.strip() for n in nombres if n.strip()))
        self._espera = settings.gemini_timeout_s
        self._espera_traducir = settings.gemini_timeout_traducir_s
        self._espera_total = settings.gemini_timeout_total_s
        self._traducciones: dict[tuple[str, str], Plato] = {}

    async def _generar[T: BaseModel](self, contenidos, config: types.GenerateContentConfig, esquema: type[T], espera: float) -> T:
        limite = time.monotonic() + self._espera_total
        fallo: Exception = TimeoutError("no quedó tiempo para consultar a Gemini")
        for modelo in self.modelos:
            restante = limite - time.monotonic()
            # salta el intento si queda menos de un cuarto de su espera
            if restante < espera / 4:
                break
            # el ultimo modelo usa todo el tiempo que queda
            plazo = restante if modelo == self.modelos[-1] else min(espera, restante)
            try:
                respuesta = await asyncio.wait_for(
                    self._cliente.aio.models.generate_content(model=modelo, contents=contenidos, config=config),
                    plazo,
                )
                if not respuesta.text:
                    raise ValueError("respuesta vacía")
                return esquema.model_validate_json(respuesta.text)
            except Exception as error:
                log.warning("Gemini %s falló (%s)", modelo, getattr(error, "code", None) or type(error).__name__)
                if not pasa_al_respaldo(error):
                    raise
                fallo = error
        raise fallo

    async def responder(self, plato: Plato, pregunta: PreguntaAsistente) -> RespuestaAsistente:
        contexto = f"FICHA DEL PLATO:\n{plato.model_dump_json(indent=1)}"
        if pregunta.paso:
            contexto += f"\n\nEl usuario está viendo el paso {pregunta.paso}."
        contenidos = [types.Content(role="user", parts=[types.Part(text=contexto)])]
        for mensaje in pregunta.historial:
            rol = "user" if mensaje.rol == "usuario" else "model"
            contenidos.append(types.Content(role=rol, parts=[types.Part(text=mensaje.texto)]))
        contenidos.append(types.Content(role="user", parts=[types.Part(text=pregunta.pregunta)]))

        config = types.GenerateContentConfig(
            system_instruction=INSTRUCCIONES.format(idioma=NOMBRES_IDIOMA[pregunta.idioma]),
            response_mime_type="application/json",
            response_schema=RespuestaAsistente,
            temperature=0.3,
        )
        return await self._generar(contenidos, config, RespuestaAsistente, self._espera)

    async def traducir(self, plato: Plato, idioma: str) -> Plato:
        clave = (plato.id, idioma)
        if clave not in self._traducciones:
            config = types.GenerateContentConfig(
                system_instruction=INSTRUCCIONES_TRADUCCION.format(idioma=NOMBRES_IDIOMA[idioma]),
                response_mime_type="application/json",
                response_schema=Plato,
                temperature=0.1,
            )
            traducido = await self._generar(plato.model_dump_json(), config, Plato, self._espera_traducir)
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
    return Asistente(settings)
