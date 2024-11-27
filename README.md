# EDDC - Proyecto de especialización

Proyecto final para la [Especialización de Explotación de Datos y Descubrimiento del Conocimiento de la Universidad de Buenos Aires](https://datamining.dc.uba.ar/datamining/).

**Tabla de contenidos**
- [Configuración](#configuración)
    - [Local](#local)
        - [Entorno](#entorno)
        - [Descarga de los datos](#descarga-de-los-datos)
    - [Usando un contenedor](#usando-un-contenedor)
- [Estructura del repositorio](#estructura-del-repositorio)

## Configuración

Para correr el conjunto de _notebooks_ con el código desarrollado, es necesario disponer de un entorno apto para ello. A continuación, se describen dos formas posibles de generar ese entorno: instalando los requerimientos en el local o utilizando un contenedor.

### Local

#### Entorno

Usando [`pyenv`](https://github.com/pyenv/pyenv?tab=readme-ov-file) en combinación con [`virualenv`](https://pypi.org/project/virtualenv/), crear un entorno con `python 3.11.4` y activarlo:

```{bash}
pyenv virtualenv 3.11.4 <env-name> && pyenv activate <env-name>
```

A continuación, instalar los requerimientos:

```{bash}
pip install --upgrade pip && pip install -r requirements.txt
```

#### Descarga de los datos

El repo ya trae un archivo `session_29-12-2020_votes.csv` con los votos de cada uno de los sendaores.

Para descargar los datos de la sesión a analizar, ejecutar:

```{bash}
python -m src download data
```

Este comando:

1. descarga la transcripción de la sesión del Senado n°28 (sesió especial n° 23) del período n°138, celebrada los días 29 y 30 de diciembre del año 2020, en formato `pdf` desde la [página del Senado](https://www.senado.gob.ar/parlamentario/sesiones/)
2. convierte dicha transcripción a texto plano (`.txt`)
3. separa los fragmentos de la transcripción indicando si son fragmentos discursivos o aclaraciones de la transcripción (`speech`) y, en caso de ser fragmentos discursivos, el orador que los pronunción (`speaker`), esta información se guarda en el archivo `session_29-12-2020_discourse.xml`
4. extrae la lista de senadores convocados indicando si estuvieron presentes o ausentes y la almacena en el archivo `session_29-12-2020_attendees.csv`
5. descarga la lista de senadores desde la [página del Senado](https://www.senado.gob.ar/senadores/Historico/Fecha) filtrando por la fecha del período correspondiente y la almacena en el archivo `senators_data.csv`. Dicho archivo contiene no solo el nombre de cada senador sino también la información sobre a qué partido y provincia representa, entre otros datos adicionales.

### En contenedor

Este repositorio cuenta con un contenedor dentro del cual es posible ejecutar el código
y las _notebooks_ disponibles [`eddc-devcontainer`](./.devcontainer/devcontainer.json).

Si se está utilizando _VSCode_, presionar `ctrl+shift+p` y seleccionar la opción
`Dev Containers: Reopen in Container`.

Esta opción incluye todos los pasos mencionados en la [configuración en local](#local).

## Estructura del repositorio

```
└── bibliography
└── data
└── doc
└── notebooks
|   ├── README.md
|   └── ...
└── src
|   ├── __main__.py
|   ├── config_handler.py
|   ├── utils.py
|   ├── downloaders
|   |   ├── attendees.py
|   |   ├── bibliography.py
|   |   └── data.py
|   └── preprocess
|       ├── patterns.py
|       └── pipeline.py
└── config.json
```
