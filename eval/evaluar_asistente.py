"""Evalúa el asistente con la ficha del plato frente al mismo modelo sin ficha, y la traducción de las fichas.

Uso desde backend/:
  uv run python ../eval/evaluar_asistente.py respuestas gemini:gemini-3.5-flash-lite [n]
  uv run python ../eval/evaluar_asistente.py respuestas ollama:gemma3:12b [n]
  uv run python ../eval/evaluar_asistente.py traducciones gemini-3.5-flash-lite
  uv run python ../eval/evaluar_asistente.py reporte
Cada llamada se guarda en eval/resultados/*.jsonl y se reanuda si se corta.
"""

import asyncio
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import httpx
from google.genai import types

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.asistente import INSTRUCCIONES, INSTRUCCIONES_TRADUCCION, NOMBRES_IDIOMA, Asistente  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.esquemas import PreguntaAsistente, RespuestaAsistente  # noqa: E402
from app.platos import cargar_platos  # noqa: E402

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "resultados"
OLLAMA = "http://localhost:11434/api/chat"

SIN_FICHA = """Eres un guía de cocina peruana dentro de una aplicación que muestra platos en 3D y realidad aumentada.
Respondes preguntas de turistas y estudiantes sobre el plato {nombre}.
Reglas:
- Si no conoces la respuesta, dilo con amabilidad y marca fuera_de_ficha en true.
- Responde en {idioma}, en texto plano sin markdown, en un máximo de 120 palabras."""

PALABRAS = {
    "es": [" el ", " los ", " con ", " es ", " para ", "ción", " una ", " del ", " se "],
    "en": [" the ", " and ", " you ", " with ", " is ", " of ", " it "],
    "pt": [" não ", " você ", " com ", "ção", "ões", " são ", " uma ", " do ", " da "],
    "fr": [" le ", " les ", " des ", " et ", " est ", " vous ", " pour ", " avec ", " du "],
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower().replace("œ", "oe"))
    return "".join(c for c in texto if not unicodedata.combining(c))


def numeros(texto: str) -> set[str]:
    return {n.replace(",", ".") for n in re.findall(r"\d+(?:[.,]\d+)?", texto)}


def idioma_detectado(texto: str) -> str:
    try:
        from langdetect import DetectorFactory, detect_langs

        DetectorFactory.seed = 0
        candidatos = [c for c in detect_langs(texto) if c.lang in PALABRAS]
        if candidatos:
            return candidatos[0].lang
    except ImportError:
        pass
    t = f" {texto.lower()} "
    return max(PALABRAS, key=lambda k: sum(t.count(p) for p in PALABRAS[k]))


def leer(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    return [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]


def guardar(ruta: Path, fila: dict):
    SALIDA.mkdir(exist_ok=True)
    with ruta.open("a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def mensajes(plato, p: dict, condicion: str) -> tuple[str, list[str]]:
    idioma = NOMBRES_IDIOMA[p["idioma"]]
    if condicion == "ficha":
        contexto = f"FICHA DEL PLATO:\n{plato.model_dump_json(indent=1)}"
        if p.get("paso"):
            contexto += f"\n\nEl usuario está viendo el paso {p['paso']}."
        return INSTRUCCIONES.format(idioma=idioma), [contexto, p["pregunta"]]
    contexto = f"El usuario pregunta por el plato {plato.nombre}."
    if p.get("paso"):
        contexto += f" Está viendo el paso {p['paso']} de la receta."
    return SIN_FICHA.format(nombre=plato.nombre, idioma=idioma), [contexto, p["pregunta"]]


async def gemini(asistente: Asistente, plato, p: dict, condicion: str) -> RespuestaAsistente:
    if condicion == "ficha":
        return await asistente.responder(plato, PreguntaAsistente(
            plato_id=plato.id, pregunta=p["pregunta"], idioma=p["idioma"], paso=p.get("paso")))
    sistema, partes = mensajes(plato, p, condicion)
    respuesta = await asistente._cliente.aio.models.generate_content(
        model=asistente._modelo,
        contents=[types.Content(role="user", parts=[types.Part(text=t)]) for t in partes],
        config=types.GenerateContentConfig(system_instruction=sistema, response_mime_type="application/json",
                                           response_schema=RespuestaAsistente, temperature=0.3),
    )
    return RespuestaAsistente.model_validate_json(respuesta.text)


async def ollama(cliente: httpx.AsyncClient, modelo: str, plato, p: dict, condicion: str) -> RespuestaAsistente:
    sistema, partes = mensajes(plato, p, condicion)
    r = await cliente.post(OLLAMA, json={
        "model": modelo, "stream": False, "think": False, "format": RespuestaAsistente.model_json_schema(), "keep_alive": "2m",
        "messages": [{"role": "system", "content": sistema}] + [{"role": "user", "content": t} for t in partes],
        "options": {"temperature": 0.3, "seed": 7, "num_ctx": 4096},
    })
    r.raise_for_status()
    return RespuestaAsistente.model_validate_json(r.json()["message"]["content"])


def archivo(prefijo: str, modelo: str) -> Path:
    return SALIDA / f"{prefijo}_{modelo.replace(':', '_')}.jsonl"


async def correr_respuestas(spec: str, limite: int | None):
    proveedor, modelo = spec.split(":", 1)
    ruta = archivo("respuestas", modelo)
    platos = cargar_platos()
    preguntas = json.loads((AQUI / "preguntas.json").read_text(encoding="utf-8"))
    hechas = {(f["condicion"], f["qid"]) for f in leer(ruta) if "error" not in f}
    asistente = Asistente(get_settings().gemini_api_key, modelo) if proveedor == "gemini" else None
    pausa = 4.0 if proveedor == "gemini" else 0.0
    cuenta = 0
    async with httpx.AsyncClient(timeout=300) as cliente:
        for condicion in ("ficha", "sin_ficha"):
            for qid, p in enumerate(preguntas):
                if (condicion, qid) in hechas:
                    continue
                if limite is not None and cuenta >= limite:
                    return
                cuenta += 1
                plato = platos[p["plato"]]
                inicio = time.perf_counter()
                try:
                    if proveedor == "gemini":
                        r = await asyncio.wait_for(gemini(asistente, plato, p, condicion), 120)
                    else:
                        r = await ollama(cliente, modelo, plato, p, condicion)
                    fila = {"condicion": condicion, "qid": qid, "respuesta": r.respuesta,
                            "fuera_de_ficha": r.fuera_de_ficha, "s": round(time.perf_counter() - inicio, 2)}
                except Exception as e:
                    fila = {"condicion": condicion, "qid": qid, "error": str(e)[:1500]}
                guardar(ruta, fila)
                print(modelo, condicion, qid, fila.get("s", fila.get("error", "")[:200]), flush=True)
                if "error" in fila and ("429" in fila["error"] or "RESOURCE_EXHAUSTED" in fila["error"]):
                    print("cuota agotada, se reanuda después", flush=True)
                    return
                await asyncio.sleep(pausa)


async def correr_traducciones(modelo: str):
    ruta = archivo("traducciones", modelo)
    asistente = Asistente(get_settings().gemini_api_key, modelo)
    hechas = {(f["plato"], f["idioma"]) for f in leer(ruta) if "error" not in f}
    for plato in cargar_platos().values():
        for idioma in ("en", "pt", "fr"):
            if (plato.id, idioma) in hechas:
                continue
            inicio = time.perf_counter()
            try:
                traducido = await asyncio.wait_for(asistente.traducir(plato, idioma), 180)
                primera = time.perf_counter() - inicio
                inicio = time.perf_counter()
                await asistente.traducir(plato, idioma)
                fila = {"plato": plato.id, "idioma": idioma, "s": round(primera, 2),
                        "s_cache": round(time.perf_counter() - inicio, 6), "ficha": traducido.model_dump()}
            except Exception as e:
                fila = {"plato": plato.id, "idioma": idioma, "error": str(e)[:1500]}
            guardar(ruta, fila)
            print(plato.id, idioma, fila.get("s", fila.get("error", "")[:200]), flush=True)
            if "error" in fila and ("429" in fila["error"] or "RESOURCE_EXHAUSTED" in fila["error"]):
                print("cuota agotada, se reanuda después", flush=True)
                return
            await asyncio.sleep(4.0)


def percentil(valores: list[float], q: float) -> float:
    v = sorted(valores)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]


def medir(filas: dict, preguntas: list[dict], platos: dict, condicion: str, detalle: list, modelo: str) -> dict | None:
    vp = fp = fn = vn = 0
    aciertos = dentro = idioma_ok = 0
    con_cifra_dentro = con_cifra_fuera = n_fuera = 0
    tiempos = []
    for qid, p in enumerate(preguntas):
        f = filas.get((condicion, qid))
        if f is None:
            continue
        plato = platos[p["plato"]]
        texto = normalizar(f["respuesta"])
        soporte = numeros(plato.model_dump_json()) | numeros(p["pregunta"]) | {str(p.get("paso", ""))}
        inventadas = sorted(numeros(f["respuesta"]) - soporte)
        tiempos.append(f["s"])
        idioma_ok += idioma_detectado(f["respuesta"]) == p["idioma"]
        if p["fuera"]:
            n_fuera += 1
            vp += f["fuera_de_ficha"]
            fn += not f["fuera_de_ficha"]
            con_cifra_fuera += bool(inventadas)
            ok = None
        else:
            dentro += 1
            fp += f["fuera_de_ficha"]
            vn += not f["fuera_de_ficha"]
            ok = all(any(normalizar(c) in texto for c in grupo) for grupo in p["claves"])
            aciertos += ok
            con_cifra_dentro += bool(inventadas)
        detalle.append({"modelo": modelo, "condicion": condicion, "qid": qid, "plato": p["plato"],
                        "idioma": p["idioma"], "fuera_esperado": p["fuera"], "fuera_de_ficha": f["fuera_de_ficha"],
                        "clave_ok": ok, "cifras_sin_soporte": inventadas, "respuesta": f["respuesta"]})
    n = vp + fp + fn + vn
    if not n:
        return None
    prec = vp / (vp + fp) if vp + fp else 0.0
    rec = vp / (vp + fn) if vp + fn else 0.0
    return {
        "n": n, "vp": vp, "fp": fp, "fn": fn, "vn": vn,
        "exactitud_fuera": round((vp + vn) / n, 3), "precision_fuera": round(prec, 3),
        "recall_fuera": round(rec, 3), "f1_fuera": round(2 * prec * rec / (prec + rec), 3) if prec + rec else 0.0,
        "n_dentro": dentro, "exactitud_clave": round(aciertos / dentro, 3) if dentro else None,
        "n_fuera": n_fuera,
        "cifras_sin_soporte_dentro": round(con_cifra_dentro / dentro, 3) if dentro else None,
        "cifras_sin_soporte_fuera": round(con_cifra_fuera / n_fuera, 3) if n_fuera else None,
        "idioma_ok": round(idioma_ok / n, 3),
        "s_media": round(sum(tiempos) / len(tiempos), 2), "s_p95": percentil(tiempos, 0.95),
    }


def medir_traduccion(trad: list[dict], platos: dict) -> dict:
    nombres = re.search(r"\((.*?)\)", INSTRUCCIONES_TRADUCCION).group(1).split(", ")
    conservados = total_nombres = num_ok = num_total = estructura_ok = 0
    for f in trad:
        original = platos[f["plato"]]
        texto_o = normalizar(original.model_dump_json())
        texto_t = normalizar(json.dumps(f["ficha"], ensure_ascii=False))
        for nombre in nombres:
            if normalizar(nombre) in texto_o:
                total_nombres += 1
                conservados += normalizar(nombre) in texto_t
        n_o, n_t = numeros(original.model_dump_json()), numeros(json.dumps(f["ficha"]))
        num_total += len(n_o)
        num_ok += len(n_o & n_t)
        estructura_ok += (len(f["ficha"]["pasos"]) == len(original.pasos)
                          and len(f["ficha"]["ingredientes"]) == len(original.ingredientes)
                          and f["ficha"]["porciones"] == original.porciones)
    tiempos = [f["s"] for f in trad]
    return {"n": len(trad), "nombres_conservados": round(conservados / total_nombres, 3),
            "nombres_total": total_nombres, "numeros_conservados": round(num_ok / num_total, 3),
            "estructura_ok": estructura_ok, "s_media": round(sum(tiempos) / len(tiempos), 2),
            "s_max": max(tiempos), "s_cache_max": max(f["s_cache"] for f in trad)}


def reporte():
    platos = cargar_platos()
    preguntas = json.loads((AQUI / "preguntas.json").read_text(encoding="utf-8"))
    resumen, detalle = {}, []
    for ruta in sorted(SALIDA.glob("respuestas_*.jsonl")):
        modelo = ruta.stem.removeprefix("respuestas_")
        filas = {(f["condicion"], f["qid"]): f for f in leer(ruta) if "error" not in f}
        resumen[modelo] = {c: m for c in ("ficha", "sin_ficha")
                           if (m := medir(filas, preguntas, platos, c, detalle, modelo))}
    for ruta in sorted(SALIDA.glob("traducciones_*.jsonl")):
        trad = [f for f in leer(ruta) if "error" not in f]
        if trad:
            resumen.setdefault(ruta.stem.removeprefix("traducciones_"), {})["traduccion"] = medir_traduccion(trad, platos)
    (SALIDA / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    (SALIDA / "detalle.json").write_text(json.dumps(detalle, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "reporte"
    if accion == "respuestas":
        asyncio.run(correr_respuestas(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None))
    elif accion == "traducciones":
        asyncio.run(correr_traducciones(sys.argv[2]))
    else:
        reporte()
