# Cocina peruana en AR: guía interactiva de platos típicos con realidad aumentada e inteligencia artificial

**Curso:** Herramientas de Desarrollo Profesional - TIC (10000096SI)
**Integrantes:** Jose Antonio Quio Uscamayta, Cristopher Gabriel Vera Quispe

---

## 1. Introducción

La gastronomía es uno de los principales atractivos turísticos del Perú y forma parte de su imagen como destino. Sin embargo, el visitante que llega a un restaurante o a una región nueva muchas veces no conoce los platos, sus ingredientes, su origen ni la forma en que se preparan, y la información disponible suele ser texto o fotografías estáticas.

La realidad aumentada (AR) permite mostrar un objeto tridimensional sobre el entorno real desde un celular, sin visores costosos. Junto con modelos 3D ligeros, una aplicación web y un asistente de inteligencia artificial, es posible presentar un plato peruano paso a paso, girarlo, verlo sobre la mesa y resolver dudas sobre su historia y preparación.

El proyecto propone una aplicación web que enseña platos típicos peruanos mediante modelos 3D que muestran el estado del plato en cada paso de la receta, visibles en AR desde un celular Android, con un asistente de IA que explica y traduce el contenido.

## 2. Problemática

- La promoción de la gastronomía peruana se apoya sobre todo en medios planos como fotos, videos y cartas impresas, que muestran el resultado final pero no cómo se arma el plato ni qué lo hace propio de una región.
- El turista extranjero y el estudiante que no conoce la cocina local encuentran barreras de idioma y de contexto cultural, por ejemplo al leer nombres como tacacho, juane o causa.
- Existen aplicaciones de AR para menús o cocina, pero la literatura revisada se centra en menús de restaurantes o en dispositivos costosos, y no se encontró un estudio que combine modelos 3D por pasos de receta, asistente con IA y orientación a la promoción de la gastronomía de un país.
- Muchas soluciones inmersivas requieren hardware especializado o instalación de aplicaciones, lo que limita su alcance frente a una solución web accesible desde un celular común.

**Pregunta de investigación:** ¿Cómo puede una aplicación web con modelos 3D, realidad aumentada e inteligencia artificial ayudar a difundir y enseñar la preparación de platos de la gastronomía peruana de forma accesible?

## 3. Objetivos

**Objetivo general**
Desarrollar un prototipo web de guía culinaria interactiva que presente platos típicos peruanos en modelos 3D y realidad aumentada, con un asistente de inteligencia artificial, para promover la gastronomía peruana.

**Objetivos específicos**
1. Seleccionar de dos a tres platos representativos de distintas regiones del Perú y documentar sus recetas e historia con fuentes confiables.
2. Obtener y optimizar los modelos 3D de cada paso de preparación en formato glTF/GLB, aptos para celulares.
3. Implementar una aplicación web en Angular con visor 3D y modo AR para Android.
4. Integrar un asistente basado en un modelo de lenguaje que responda preguntas sobre cada plato y traduzca su contenido.
5. Automatizar la construcción y el despliegue con contenedores Docker y un flujo de integración continua.
6. Validar el prototipo con pruebas funcionales y con una prueba de uso en celulares reales.

## 4. Marco teórico

### 4.1 Antecedentes

**Trabajo de referencia.** Flores y Rodríguez (2025) desarrollaron, en una tesis de título profesional, un museo virtual de realidad virtual con fines educativos. Combinaron el motor Godot 4 con OpenXR, visores Meta Quest 3, Blender para los escenarios, Meshy AI para generar modelos 3D de personajes a partir de texto o imágenes, plataformas de IA para voces y animación facial, y un chatbot local con Ollama para responder preguntas de los estudiantes. Es la base conceptual de este proyecto, que adopta la idea de combinar modelos 3D generados con IA y un asistente conversacional, pero la lleva a la gastronomía y a una plataforma más sencilla, la web con AR en celular.

**AR aplicada a alimentos y menús.** Seo, Han y Howlett (Washington State University) realizaron dos estudios experimentales con menús de AR que mostraban información de origen de los alimentos. Comparados con menús impresos y con código QR, los menús AR aumentaron la intención de visita y la disposición a compartir la información (Washington State University, 2026). Esto respalda el uso de AR para presentar platos de forma atractiva e informativa.

**AR para guiar la cocina.** Majil, Yang y Yang (2022) construyeron un asistente de cocina en AR sobre un visor Magic Leap One que reconoce ingredientes con YOLOv5, sugiere recetas y muestra tutoriales paso a paso. En una prueba con 20 participantes, 19 recomendarían el sistema. Es un antecedente directo de la guía paso a paso, aunque con hardware costoso que este proyecto sustituye por el celular.

**Gastronomía y turismo en el Perú.** Esparza et al. (2023) estudiaron a visitantes de Lima y encontraron que la satisfacción y la valoración de la experiencia, incluida la gastronomía tradicional limeña, influyen positivamente en la lealtad del turista, es decir, en que recomiende y regrese. Sustenta que mejorar cómo se conoce y se vive la gastronomía puede aportar a la promoción del destino.

**AR en la web y patrimonio cultural.** Boutsi et al. (2023) presentan una plataforma web de código abierto para gestionar y publicar contenido de patrimonio cultural con visualización 3D, VR y AR, dirigida tanto a expertos como a público general. Muestra que el patrimonio puede difundirse con 3D desde el navegador sin instalar aplicaciones. Un caso de estudio de Chialab describe una experiencia de AR web con el componente model-viewer, motivada por que los usuarios vean los objetos en su entorno sin descargar una app.

**IA generativa y 3D.** Behravan (2025) propone un marco que usa modelos de visión-lenguaje y modelos de lenguaje para convertir imágenes y voz en objetos 3D interactivos en AR, con tiempos de generación de menos de 50 segundos y retos de latencia y uso. Respalda la generación de modelos 3D con IA y sus limitaciones, que conviene tener en cuenta al preparar los platos.

**Vacío identificado.** En la búsqueda realizada no se encontró un estudio que integre modelos 3D por pasos de receta, AR web y un asistente de IA para promover la gastronomía de un país. Ese vacío justifica la propuesta.

### 4.2 Bases teóricas

- **Realidad aumentada.** Tecnología que superpone objetos virtuales al entorno real captado por la cámara. En celulares Android se apoya en ARCore.
- **WebAR y glTF.** El formato glTF/GLB es un estándar para modelos 3D ligeros en la web. El componente model-viewer de Google permite mostrarlos y abrirlos en AR desde el navegador. En Android usa el visor de escenas del sistema, y en iPhone requiere además el formato USDZ, por lo que el proyecto se limita a Android.
- **Generación 3D con IA.** Herramientas de IA generativa crean modelos 3D desde imágenes o texto, con resultados que suelen requerir limpieza, como se vio en el trabajo de referencia con Meshy AI.
- **Modelos de lenguaje como asistentes.** Un LLM con instrucciones de rol y datos propios puede responder preguntas, traducir y mantener un tono de guía, siempre que se le entregue una base de conocimiento verificada para limitar errores.
- **DevOps.** Los contenedores Docker y la integración continua permiten construir, probar y desplegar el prototipo de forma repetible, tal como plantea la primera unidad del curso.

## 5. Tecnologías propuestas

| Capa | Herramienta |
|---|---|
| Interfaz | Angular y model-viewer |
| Modelos 3D | glTF/GLB, Blender, herramientas de generación 3D con IA y bibliotecas con licencia libre |
| Asistente | API de un modelo de lenguaje con salida estructurada |
| API | Node o FastAPI |
| Despliegue | Docker Compose y GitHub Actions |
| Pruebas | Playwright y prueba en celulares Android |

## 6. Referencias

Estas referencias tienen sus datos verificados en la fuente. Se citan en formato cercano a APA y deben ajustarse a la norma que pida el docente.

- Boutsi, A.-M., Tallis, I., Pastos, I., Verykokou, S., & Ioannidis, C. (2023). 5dMeteora framework: Management and web publishing of cultural heritage data. *ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences, X-M-1-2023*, 33-40. https://doi.org/10.5194/isprs-annals-X-M-1-2023-33-2023
- Esparza Huamanchumo, R. M., Hernández-Rojas, R. D., Longa-López, R. A., & Cárdenas-Jarama, M. (2023). Gastronomy as an effect of visitor loyalty: The Peruvian (Lima) case. *International Journal of Tourism Cities, 9*(2), 362-376. https://doi.org/10.1108/IJTC-03-2022-0071
- Majil, I., Yang, M.-T., & Yang, S. (2022). Augmented reality based interactive cooking guide. *Sensors, 22*(21), 8290. https://doi.org/10.3390/s22218290
- Seo, S., Han, J., & Howlett, E. (2026). Estudio sobre menús de realidad aumentada. *International Journal of Hospitality Management*. Datos tomados de la nota de prensa: Washington State University (18 de febrero de 2026), https://news.wsu.edu/press-release/2026/02/18/augmented-reality-menus-may-help-restaurants-attract-customers/ . Artículo: https://www.sciencedirect.com/science/article/pii/S0278431925002634

## 7. Pendientes antes de entregar

Estas referencias salieron de la búsqueda y **aún no tienen sus datos completos verificados**. Ábranlas y completen autor, año, título y DOI antes de citarlas, o descártenlas.

- **Flores, B., & Rodríguez, A. (2025).** Tesis de título profesional. Falta el título completo y la universidad. El nombre del archivo es `B_Flores-A_Rodriguez_Tesis_Título_Profesional_2025_HYWMAN.pdf`. Hay que tomarlos de la carátula.
- **Título del artículo de Seo, Han y Howlett y su año de publicación en la revista.** Se obtienen en el enlace de ScienceDirect.
- **Behravan, M. (2025).** arXiv 2502.15869, https://arxiv.org/abs/2502.15869 . Confirmen título y autores en el propio artículo, porque la página de Warwick que se consultó es solo un resumen automático.
- **Chialab.** Caso de estudio sobre AR web con model-viewer, https://www.chialab.it/objects/augmented-reality-on-the-web-with-model-viewer . No muestra autor ni fecha, úsenlo como referencia web.
- **Tesis de TU Delft sobre un menú AR en un restaurante neerlandés**, https://repository.tudelft.nl/record/uuid:0a814007-0d67-4ec0-9a7c-f789e8d80e1e . Reportó que el menú AR se percibe más representativo de los platos, pero sin aumento del gasto. No se pudo abrir para sacar sus datos.
- **Ghasemi et al. (2023).** Sistema sAR Kitchen de AR espacial para cocina, presentado en un taller de IEEE VR. Falta título exacto y datos.
- **Karim y Chi (2010).** Marco muy citado sobre la imagen de la comida de un destino. Hay que ubicar el artículo original.
- **Oxford y Qreal sobre postres con menús AR.** Se vio solo en una nota de prensa y la empresa participó en el estudio. Si lo usan, mencionen ese conflicto de interés.
