# Sesión complementaria | IA responsable en RAG y agentes

Es la segunda sesión del curso: en la primera se instaló el entorno y todavía no se ha construido ningún asistente. Aquí se revisa, antes de construirlo, qué puede salir mal en un RAG y en un agente desde la ética, la equidad y la seguridad. Siempre se compara el mismo sistema **sin ajuste** y **con ajuste**. La duración es de **dos horas** e incluye tres laboratorios.

- Página del módulo: `docs/modulo-etica.html` (usa `docs/styles.css` y `docs/script.js` del curso).

## Cómo se usan los laboratorios

Los laboratorios están listos: **no hay que programar nada**. Solo se descargan, se ejecutan, se revisa la salida y se analiza. Cada uno tiene dos versiones equivalentes:

1. **En el navegador:** la página del módulo, pestañas Lab 1, Lab 2 y Lab 3. No requiere instalar nada.
2. **En PyCharm:** los scripts de `ejercicios/`, con el entorno `RAGLAB` de la sesión 1.

## Resultados de aprendizaje

Al finalizar la sesión, cada estudiante podrá:

- Medir una brecha de equidad con datos reales y explicar qué cuesta cerrarla en cada etapa: datos, modelo o decisión.
- Identificar los riesgos de cada etapa de un pipeline RAG: privacidad, sesgo de fuente, envenenamiento, inyección indirecta, versiones derogadas y alucinación.
- Reconocer las salvaguardas que aplicará entre el recuperador y el prompt cuando construya su RAG: metadatos, procedencia, vigencia, aislamiento del contexto y abstención.
- Analizar los límites de un agente: mínimo privilegio, regla de dos, destinos permitidos y aprobación humana.
- Ubicar su futuro proyecto frente al AI Act europeo y a las normas vigentes en Colombia.

## Ejercicios

| Archivo | Tema | Requiere |
| --- | --- | --- |
| `ejercicios/01_auditoria_compas.py` | Auditoría de COMPAS con los datos y filtros de ProPublica | `pandas` |
| `ejercicios/02_mitigacion_compas.py` | Mitigación en tres etapas (datos, modelo y decisión) con métricas por grupo | `scikit-learn`; `fairlearn` para la etapa del modelo |
| `ejercicios/03_rag_con_salvaguardas.py` | RAG con corpus normativo: sesgo, envenenamiento, desactualización y abstención | Solo la biblioteca estándar. Opcional: `--llm` usa `langchain-openai` y una clave de OpenRouter en `.env` |
| `ejercicios/04_agente_con_salvaguardas.py` | Agente con capa de políticas frente a una inyección indirecta | Solo la biblioteca estándar |
| `ejercicios/datos/corpus_regulacion.json` | Corpus didáctico: síntesis de normas reales y un ataque construido | — |

Desde la raíz del repositorio, ejecuta con el entorno `RAGLAB` activo:

```bash
conda activate RAGLAB
pip install -r modulo-etica/requirements.txt   # pandas, scikit-learn y fairlearn
python modulo-etica/ejercicios/01_auditoria_compas.py
python modulo-etica/ejercicios/02_mitigacion_compas.py
python modulo-etica/ejercicios/03_rag_con_salvaguardas.py
python modulo-etica/ejercicios/04_agente_con_salvaguardas.py --preguntar
```

El ejercicio 1 (y el 2, que lo reutiliza) descarga una sola vez `compas-scores-two-years.csv` desde el repositorio público de ProPublica (<https://github.com/propublica/compas-analysis>) y lo guarda en `ejercicios/datos/`.

## Guía de cada laboratorio (solo ejecutar, revisar y analizar)

**Lab 1 · COMPAS (20 min)**

| Minutos | Qué hacer |
| --- | --- |
| 0–3 | Abrir la pestaña Lab 1 o ejecutar `01_auditoria_compas.py`. |
| 3–7 | Pulsar “Sin ajuste” (decil ≥ 5) y anotar falsos positivos y negativos por grupo. |
| 7–11 | Pulsar “Con ajuste” (umbrales 7 y 5). Observar qué pasa con el valor predictivo. |
| 11–15 | Ejecutar `02_mitigacion_compas.py` y comparar las tres formas de mitigar. |
| 15–20 | En parejas: ¿qué error importa más aquí y quién debería decidirlo? |

**Lab 2 · RAG responsable (15 min)**

| Minutos | Qué hacer |
| --- | --- |
| 0–2 | Abrir la pestaña Lab 2 o ejecutar `03_rag_con_salvaguardas.py` (sin clave ni internet). |
| 2–6 | Sin salvaguardas, probar las cuatro preguntas y anotar qué fragmentos llegan al modelo. |
| 6–11 | Activar una salvaguarda a la vez: ¿cuál saca el ataque? ¿cuál quita la norma derogada? |
| 11–15 | Con la pregunta fuera del corpus, ¿el sistema se abstiene? ¿Qué salvaguarda pondrías primero en tu RAG? |

**Lab 3 · Agente (10 min)**

| Minutos | Qué hacer |
| --- | --- |
| 0–2 | Ejecutar el agente sin salvaguardas (pestaña Lab 3 o `04_agente_con_salvaguardas.py`) y leer la bitácora. |
| 2–5 | Activar solo la regla de dos: ¿evita la fuga? ¿y el borrado? |
| 5–8 | Buscar el conjunto mínimo que evita ambos daños y aún responde a Ana y a Luis. |
| 8–10 | Activar la aprobación humana y aprobar todo: ¿quién falló? |

## Secuencia sugerida (120 minutos)

| Minutos | Bloque | Actividad |
| --- | --- | --- |
| 0–12 | Casos reales | Qué es un RAG; Air Canada, Mata v. Avianca, Sentencia T-323 de 2024 |
| 12–37 | Sesgo y equidad | Qué hace COMPAS, tres definiciones de “justo”, teorema de imposibilidad y su demostración, mitigación |
| 37–59 | Lab 1 · COMPAS | Ejecutar y analizar: página del módulo y scripts 01–02, más puesta en común |
| 59–69 | Pausa | — |
| 69–77 | Riesgos del RAG | Etapas del RAG, METR y alucinaciones, envenenamiento, EchoLeak, equidad y privacidad |
| 77–96 | Lab 2 · RAG responsable | Ejecutar y analizar: página del módulo y script 03, más puesta en común |
| 96–102 | Agentes con límites | Agencia excesiva, caso Replit, regla de dos |
| 102–113 | Lab 3 · Agente | Ejecutar y analizar: página del módulo y script 04, más puesta en común |
| 113–120 | Regulación y cierre | AI Act, Colombia, checklist y votación de casos |

## Notas

- Las cifras de COMPAS son cálculos propios con los datos públicos de ProPublica. ProPublica reportó 44,9 % frente a 23,5 % en su análisis original; con el archivo `compas-scores-two-years.csv` y sus filtros se obtiene 42,3 % frente a 22,0 %.
- El corpus del ejercicio 3 contiene síntesis fieles, no citas textuales. Consulta siempre el texto oficial en la URL de cada fragmento. El fragmento `web-01` es un ataque construido para la demostración.
- El agente del ejercicio 4 es una simulación determinista y sus datos son ficticios.
- Material base: Rodríguez Meléndez, O. (2026). *Riesgos éticos y técnicos en IA generativa* y *Chats y sistemas RAG*. Diplomado en IA Generativa, Universidad de la Sabana.

Autor: Diego Hernández, DataLab UNAL.
