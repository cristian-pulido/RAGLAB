# RAG-LAB | Diseño de agentes de IA

Repositorio de materiales para aprender a crear asistentes inteligentes y sistemas RAG. Incluye la bienvenida al curso, una ruta práctica de programación y agentes de IA, una actividad de análisis de datos y una sesión complementaria sobre ética, equidad y seguridad.

## Materiales del curso

- [Bienvenida y recorrido general](docs/index.html).
- [Módulo 1: herramientas, Python y agentes de IA](docs/modulo-01.html): guía interactiva de ocho horas en dos sesiones. La segunda sesión termina con un proyecto de dos horas para analizar datos públicos, crear un tablero HTML y publicarlo en GitHub Pages.
- [Material de apoyo del módulo 1](modulo-01/README.md) y [ejercicios de Python](modulo-01/ejercicios/).
- [Sesión complementaria: IA responsable en RAG y agentes](docs/modulo-etica.html), con su [guía de actividades y laboratorios](modulo-etica/README.md).
- [Entorno Conda del curso](RAGLAB.yml).

## Ruta de aprendizaje

En el módulo 1, el grupo prepara Git, GitHub, Miniconda y PyCharm; ejecuta ejercicios de Python; explora Kiro y otros agentes disponibles en PyCharm AI Chat; y practica cómo pedir, revisar, ejecutar y validar cambios antes de guardarlos en GitHub.

El paso final parte de una demostración guiada con datos de COVID-19 de Colombia. Después, cada estudiante elige un conjunto de datos público, formula una pregunta, crea un tablero estático con indicadores y gráficos, documenta la fuente y las limitaciones, y comparte el resultado. Los tableros se guardan en `docs/proyectos/<nombre>/` para publicarlos con GitHub Pages. No se deben publicar filas individuales ni datos sensibles.

La sesión complementaria de IA responsable utiliza laboratorios sobre equidad en COMPAS, salvaguardas para RAG y límites de los agentes. Se puede seguir desde la página en el navegador o ejecutar los scripts de Python desde el entorno del curso.

## Preparar el entorno

Desde la carpeta raíz del repositorio, crea y activa el entorno:

```bash
conda env create -f RAGLAB.yml
conda activate RAGLAB
```

Los ejercicios del módulo 1 se ejecutan desde la raíz del repositorio:

```bash
python modulo-01/ejercicios/01_hola_python.py
python modulo-01/ejercicios/02_variables_y_tipos.py
python modulo-01/ejercicios/03_condicionales_y_bucles.py
python modulo-01/ejercicios/04_funciones.py
```

Para los laboratorios de ética que usan los scripts, instala sus dependencias adicionales:

```bash
pip install -r modulo-etica/requirements.txt
```

Después puedes ejecutar los laboratorios desde la raíz:

```bash
python modulo-etica/ejercicios/01_auditoria_compas.py
python modulo-etica/ejercicios/02_mitigacion_compas.py
python modulo-etica/ejercicios/03_rag_con_salvaguardas.py
python modulo-etica/ejercicios/04_agente_con_salvaguardas.py --preguntar
```

La primera ejecución de los ejercicios 1 y 2 descarga los datos públicos de COMPAS de ProPublica. El laboratorio RAG funciona sin clave API; la opción `--llm` requiere una clave de OpenRouter configurada en `.env`.

## Publicar el tablero final

El paso 11 de la guía explica cómo guardar el tablero y sus gráficos en `docs/proyectos/<nombre>/`, subir los cambios a la rama `DEV` de tu fork y seleccionar esa rama y la carpeta `/docs` como fuente de GitHub Pages. La página principal del curso permanece en `docs/index.html`.
