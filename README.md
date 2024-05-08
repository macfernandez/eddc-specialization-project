# EDDC - Proyecto de especialización

Proyecto final para la [Especialización de Explotación de Datos y Descubrimiento del Conocimiento de la Universidad de Buenos Aires](https://datamining.dc.uba.ar/datamining/).

## Configuración

Para correr el conjunto de _notebooks_ con el código desarrollado, es necesario disponer de un entorno apto para ello. A continuación, se describen dos formas posibles de generar ese entorno: instalando los requerimientos en el local o utilizando un contenedor.

### Local

#### Entorno

Usando alguna versión de `python3` (para el desarrollo del proyecto se usó `3.11.4`), crear un entorno virtual:
```{bash}
python -m venv venv
```

Activarlo:
```{bash}
source venv/bin/activate
```

E instalar los requerimientos:
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

Luego, descargar los datos de los senadores en ejercicio durante el período en el que tuvo lugar la sesión:
```{bash}
python -m src download attendees
```

Este comando descarga la lista de senadores desde la [página del Senado](https://www.senado.gob.ar/senadores/Historico/Fecha) filtrando por la fecha del período correspondiente y la almacena en el archivo `senators_data.csv`. Dicho archivo contiene no solo el nombre de cada senador sino también la información sobre a qué partido y provincia representa, entre otros datos adicionales.

### Usando un contenedor

#TODO

#Cuando se arme el contenedor, ya descargar todo

## Flujo de trabajo

### [01-data-preprocessing](./notebooks/01-data-preprocessing.ipynb)

Notebook que toma como _input_ las tablas:

1. [session_29-12-2020_attendees](./data/session_29-12-2020_attendees.csv): tabla generada a partir de la transcripción de la sesión
- primera columna: rol del asistente en la sesión
- segunda columna: nombre del asistente tal cual aparece en la transcripción de la sesión

2. [senators_data](./data/senators_data.csv): tabla descargada de la [página del Senado](https://www.senado.gob.ar/senadores/Historico/Fecha) con la información de los senadores en ejercicio durante el período en el que tuvo lugar la sesión
- Senador: nombre del senador o senadora
- Nº de Orden: número de orden en el Libro de Matrículas de la Dirección Secretaría Parlamentaria
- Período Legal: período legal de su mandato
- Período Real: período real de su mandato
- Provincia: distrito o provincia que representa
- Partido Político o alianza: partido político o alianza por el que ingresó
- Reemplazo: apellido y nombre del senador que lo reemplazó
- Observaciones: observaciones

    Esta información fue extraída de [la paǵina de introductoria al buscador del Senado](https://www.senado.gob.ar/senadores/Historico/Introduccion).

3. [session_29-12-2020_votes](session_29-12-2020_votes.csv): tabla generada manualmente con el voto de cada senador
- name: nombre del asistente tal cual aparece en la transcripción de la sesión
- vote: voto emitido

y genera la tabla:

[session_29-12-2020_senators](./data/session_29-12-2020_senators.csv)

- name: nombre del asistente tal cual aparece en la transcripción de la sesión
- vote: voto emitido
- senator: nombre del senador o senadora tal cual aparece en la tabla `senators_data`
- province: distrito o provincia que representa
- party: partido político o alianza por el que ingresó

Las tablas se unen a partir de los nombres de los senadores, para lo cual es necesario preprocesar los datos en la columna correspondiente en cada una a fin de estandarizarla.
