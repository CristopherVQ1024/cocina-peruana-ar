# Cocina peruana AR

Guía web de platos peruanos: cada paso de la receta se ve como un modelo 3D, se puede poner sobre la mesa con realidad aumentada desde un celular Android y un asistente con IA responde preguntas y traduce la ficha.

Propuesta del curso en [docs/propuesta.md](docs/propuesta.md).

## Estructura

```
frontend/   Angular 22 con model-viewer, Tailwind y Spartan UI
backend/    FastAPI, fichas de platos en data/platos/*.json y asistente con Gemini
modelos/    scripts que generan los GLB de cada paso de los tres platos
docs/       propuesta y documentación del curso
```

## Desarrollo local

Requisitos: Node 24, uv y Python 3.12 o superior.

```bash
cp .env.example .env            # poner GEMINI_API_KEY para el asistente y la traducción
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000
```

En otra terminal:

```bash
cd frontend && npm install && npx ng serve --port 4300
```

Abrir http://localhost:4300. Angular redirige `/api` al backend con `proxy.conf.json`.

Sin `GEMINI_API_KEY` la app funciona igual: el chat muestra que el guía no está disponible y la ficha se queda en español.

## Pruebas

```bash
cd backend && uv run pytest -q
cd frontend && npx ng build
```

## Docker

```bash
docker compose up -d --build    # http://localhost:8090, el puerto se cambia con WEB_PORT
```

Nginx sirve el frontend, los modelos con el tipo `model/gltf-binary` y redirige `/api` al backend. GitHub Actions corre las pruebas, el build y el build de las imágenes en cada push a `main`.

## Realidad aumentada

- En Android el botón **Ver en tu mesa** abre Scene Viewer, que usa ARCore. Solo aparece si el celular es compatible.
- El modelo se muestra a **tamaño real** (`ar-scale="fixed"`): el plato mide 26 cm.
- **AR exige HTTPS y una URL pública**, porque Scene Viewer descarga el GLB por su cuenta. Para probar desde el celular sin desplegar, sirve un túnel:

```bash
cloudflared tunnel --url http://localhost:8090
```

## Modelos 3D

Los modelos de los tres platos se generan por script con `trimesh`: perfiles de revolución para la vajilla, formas con ruido para los alimentos, color por vértice y normales suaves. Son 15 archivos, uno por paso, de entre 100 y 450 KB.

```bash
uv run modelos/generar.py           # los tres platos
uv run modelos/generar.py rocoto    # solo los platos cuyo id contenga ese texto
```

- `modelos/base.py`: utilidades de geometría y color, y el menaje común (plato, tabla, bol, olla, sartén).
- `modelos/causa.py`, `modelos/tacacho.py`, `modelos/rocoto.py`: una función por paso de cada plato.

Todo se arma en metros, a tamaño real, con el centro en el origen y la base en y = 0.

Para reemplazar un paso por un modelo hecho en Blender o con IA (Meshy, Tripo, Hunyuan3D):

1. Mantener la misma escala en metros, con el centro del plato en el origen y la base en y = 0.
2. Exportar a glTF binario (`.glb`), con Y hacia arriba.
3. Optimizar y apuntar a menos de 3 MB por paso:
   ```bash
   npx @gltf-transform/cli optimize entrada.glb salida.glb --compress meshopt --texture-compress webp --texture-size 1024
   ```
4. Guardar como `paso-N.glb` en la carpeta del plato. No hace falta tocar código.

Para un plato nuevo: crear `backend/data/platos/<id>.json` con la misma forma que `causa-limena.json`, poner sus modelos en `frontend/public/modelos/<id>/` y agregar su id a `ORDEN` en `backend/app/platos.py` si importa su posición en el inicio.

## Pendientes

- Verificar las tres fichas (historia y receta) con fuentes citables antes de la entrega. Los orígenes de los nombres y la leyenda del rocoto relleno están redactados como versiones populares, no como hechos.
- Pruebas E2E con Playwright y prueba de uso en celulares Android reales.
