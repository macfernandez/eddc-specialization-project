## Flujo de trabajo

Flujo de trabajo llevado a cabo para la elaboración del trabajo. Las notebooks comentadas se encuentran en la carpeta [notebooks](./notebooks/)

### [01. Data Preprocessing](./notebooks/01-data-preprocessing.ipynb)

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

### [02. Data Description](./notebooks/02-data-description.ipynb)

Notebook que toma como _input_ la tabla [session_29-12-2020_senators](./data/session_29-12-2020_senators.csv) y el archivo [session_29-12-2020_discourse](./data/session_29-12-2020_discourse.xml) y realiza un análisis exploratorio de los datos.

Se observa:

- 70 senadores
- 24 provincias
- partidos
  - 25 partidos
  - 23 de las provincias se encuentran representadas por 2 partidos, solo La Rioja presenta un único partido que la representa
  - la mayoría de los partidos presentan una clara filiación (ya en su nomenclatura) con los dos grandes partidos de ese momento: la alianza Juntos por el cambio y Frente de todos. Se añade una nueva columna indicando esta filiación en los casos de los casos de clara pertenencia o relación. Los datos quedan agrupados en: Frente de todos (6 partidos), Juntos por el cambio (11 partidos) y Otros (10 partidos)
  - de las 24 provincias, 22 son representadas por 3 senadores y 2 (Tucumás y La Rioja), por solo 2
  - 13 partidos cuentan con un solo representante; 9 cuentan con 2; 2 cuentan con 7 y solo se observa un partido con 3, 10 y 12 representantes
- votos:
  - 4 categorías de voto: positivo, negativo, ausente y abstención
  - una abstención (en el Frente Justicialista)
  - dos ausentes (en Cambiemos Fuerza Cívica Riojana y Frente Unidad Justicialista San Luis)
  - 29 votos negativos (15 en Juntos por el Cambio)
  - 38 votos positivos (mayoría en partidos vinculados con el Frente para la Victoria, aproximadamente 2/3 vs. 1/3 en Juntos por el cambio)
- datos del discurso:
  - a partir del archivo `session_29-12-2020_discourse` se genera un diccionario para matchear los nombres de los senadores con los nombres utilizados en la transcripción (explicar que los nombres utilizados en la transcripción no matchean 100% porque ponen partes del apellido y no el nombre completo, por eso fue necesario diseñar una heurística para hacer corresponder los datos),  se observa que hay senadores que no hablaron y otros que lo hicieron y su nombre corresponde con dos entradas (dos oradores)
  - se revisa manualmente que el mapeo nombre de senador-nombre de orador esté bien hecho (se genera un [diccionario](./notebooks/map_name2speaker.json), se lo revisa manualmente y luego se vuelve a realizar el mapeo tomando como input ese diccionario)
  - a cada senador se le asigna los discursos que pronunció (`speech`)
  - se procesan los discursos usando el modelo `es_core_news_md` de la librería `spaCy` y la librería `nltk`, y se genera el archivo [tokens2tag_as_stopw.csv](./data/tokens2tag_as_stopw.csv) para etiquetar con las siguientes columns:
    - raw: token en minúscula
    - F: frecuencia absoluta observada
    - f: frecuencia relativa (F/sum(F))
    - stemm: token stemizado (utilizando el stemmer `Snowball` en español de la librería `nltk`)
    - lemma: token lematizado (utilizando la librería `spaCy`)
    - pos: etiqueta POS gel token (generada usando la librería `spaCy`)
    - use: indicación para usar el lema del token (`lemma`), otra palabras (en cuyo caso, indicada en este campo)
    - pos_correction: indicación sobre si es necesario cambias la etiqueta POS del token (en cuyo caso, indicada en este mismo campo)

### Decisiones durante la anotación

#### Sobre los verbos

- preferir siempre la lematización (forma infinitiva)
- los clíticos se omiten (la, lo, las, los)
- las formas reflexivas se omiten (se)

#### Sobre los nombres

- por cuestiones de relevancia para el estudio, se mantiene la marca de género pero se omite la marca de número

### Sobre los números

- se omiten todos:
  - los que aparecen en dígitos (\\d+)
  - los que aparecen en caracteres ('cuarenta')

### Sobre los conectores

- se parsean como SCONJ

### Sobre las etiquetas auxiliares

- se las cataloga como verbos si pertenecen a ese tipo
- se desprecia la categoría auxiliar

### Palabras que se omiten

- se indican con `FALSE` en la columna `use`
- se omiten aquellas palabras que:
  - son dígitos (`NUM`)
  - son signos de puntuación (`PUNCT`)
  - son palabras más signo de puntuación (`SYM`)
  - son u operan como conectores (`SCONJ`, `CCONJ`)

  - se preprocesa esos discursos (se lo convierte a minúscula, se le quita las tildes, se remueve la puntuación) (`speech_prep`)
  - se calcula:
        - la cantidad de intervenciones de cada senador (`n_interventions`)
        - la cantidad de tokens totales por senador intervención (`n_tokens_interventions`)
        - la cantidad de tokens únicos por senador intervención (`n_unique_tokens_interventions`)
        - la media de tokens totales de cada senador (`mean_tokens_interventions`)
        - la media de tokens únicos de cada senador (`mean_unique_tokens_interventions`)
        - la mediana de tokens totales de cada senador (`median_tokens_interventions`)
        - la mediana de tokens únicos de cada senador (`median_unique_tokens_interventions`)
    - se grafica:
        - la [distribución de intervenciones](./visualizations/distrib_boxplot_interventions.png) (distribución asimétrica a derecha, mediana y moda 1, media 2.871429 y std 6.229712)
        - la [distribución de tokens](./visualizations/distrib_boxplot_n_tokens_interventions.png) y [tokens únicos en cada intervención](./visualizations/distrib_boxplot_n_unique_tokens_interventions.png)
        - la [distribución de medias y medianas de tokens](./visualizations/distrib_boxplot_tokens.png) y [tokens únicos en cada intervención](./visualizations/distrib_boxplot_tokens_uniq.png)
        - la [distribución de medias de tokens por partido](./visualizations/distrib_boxplot_mean_tokens_party.png) y la [distribución de medias de tokens por familias de partidos](./visualizations/)
    - se observa que:
        - 9 senadores no hablaron
