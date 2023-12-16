<h1 align="center">Gestión de repositorio y código</h1>
<h6 align="center">Documento que contiene la estrategia de ramificación, política de commits, estrategia de pull requests, política de versionado y estructura de carpetas</h6>

## Tabla de Contenidos

1. [Política de *Commits*](#id1)
2. [Estructura del Repositorio](#id2)
3. [Estrategia de Ramificación](#id3)
    1. [Ramas Principales](#id3.1)
    2. [Corrección de Bugs en Producción](#id3.2)
    3. [Ramas Épicas y Features](#id3.3)
4. [Estrategia de Revisiones de código y *Pull Requests*](#id4)
5. [Política de Versionado](#id5)

 <div id='id1'/>

### 1. Política de Commits
Es importante establecer una política de commits para el proyecto, ya que mensajes de commit claros y descriptivos ayudarán a los miembros del equipo a comprender los cambios realizados en el commit y a rastrear el progreso del proyecto. La plantilla que usaremos, siguiendo las mejores prácticas, será de la forma:

```
# No más de 50 caracteres. #### Aquí hay 50 caracteres: #

# Ajustar a 72 caracteres. ################################## Esto está aquí: #

tipo: asunto #id

cuerpo

### tipo
# feat (nueva funcionalidad)
# fix (corrección de errores)
# research (incorporación de código experimental, puede no ser funcional)
# refactor (refactorización de código)
# docs (actualización de documentación)
# test (incorporación o modificación de pruebas)
# conf (modificación de archivos de configuración)

### issue
# Consiste en una breve descripción del problema abordado y debe comenzar con un verbo en participio pasado.
# Se hará referencia al problema correspondiente (si lo hay) de la siguiente manera: `#<ID_issue>`.

### cuerpo (opcional)
# Se utilizará en caso de que el problema no sea lo suficientemente descriptivo.

### Ejemplo
# conf: Actualizar docker-compose.yml
```
<div id='id2'/>

### 2. Estructura del Repositorio
La estructura del proyecto se compone de diversas carpetas que contienen elementos clave para su funcionamiento. El directorio principal alberga subcarpetas como `.github` con flujos de trabajo para GitHub Actions, `decide` con módulos de autenticación, visualización y procesamiento de datos, junto con directorios como `doc` para documentación, `docker` para configuraciones relacionadas, y `loadtest` para herramientas de pruebas de carga. Además, se incluyen archivos fundamentales como `README.md` para información básica, `requirements.txt` con las dependencias de Python y archivos de configuración como `.gitignore` y `LICENSE`, delineando la estructura organizativa y funcional del proyecto.

```
- .github/workflows
- decide
	- authentication
	- base
	- booth
	- census
	- configurator
	- decide
	- gateway
	- mixnet
	- postproc
	- store
	- test-scripts
	- visualizer
	- voting
	- config.jsonne.example
	- local_settings.py
	- local_settings_example.py
	- local_settings_gactions.py
	- manage.py
	- populate.json
	- secondauth.example.py
- doc
- docker
- loadtest
- resources
- vagrant
- .gitignore
- .gitmessage.txt
- .travis.yml
- LICENSE
- README.md
- launch.sh
- requirements.txt
```
<div id='id3'/>

### 3. Estrategia de ramificación
<div id='id3.1'/>

#### 3.1. Ramas principales

Las ramas principales del proyecto serán *main* y *develop*, donde se reunirán la funcionalidad estable y la funcionalidad en desarrollo, respectivamente. Ambas ramas están protegidas para evitar la fusión sin 2 revisiones aprobadas.

<div id='id3.2'/>

#### 3.2. Corrección de errores en producción

En caso de encontrar un error en *main*, se creará una nueva rama llamada *hotfix* para corregirlo con la siguiente estructura:
- `hotfix/nombre_rama`.
Luego, se creará una nueva solicitud de extracción para fusionar en *main* y *develop*.

<div id='id3.3'/>

#### 3.3. Ramas Épicas y Features

En nuestro proyecto hemos definido algunos incrementos para implementar, por lo que usaremos ramas épicas para gestionar las modificaciones de varios desarrolladores. Cuando una épica contenga la nueva funcionalidad implementada con sus respectivas pruebas, se creará una solicitud de extracción para fusionarla en *develop*. La épica tendrá la siguiente estructura: `epic/ID_issue-nombre_rama`.

Los desarrolladores crearán sus ramas a partir de esta épica para trabajar en un módulo de esa función con la estructura: `feature/nombre_rama-módulo`. Solo cuando hayan terminado sus cambios y hayan creado sus pruebas se creará una solicitud de extracción para fusionarse en su épica.

<div id='id4'/>

### 4. Estrategia de revisiones de código y *pull requests*

Cuando haya un incremento funcional en una épica, se creará una solicitud de extracción para fusionarlo en *develop*. Una vez creada, se revisará el incremento en busca de errores y se fusionará. Solo cuando dos revisores hayan verificado los cambios y las acciones de GitHub se hayan completado correctamente, se fusionará la solicitud de extracción.

<div id='id5'/>

### 5. Política de versionado

Como política de versionado, utilizaremos un versionado semántico con la siguiente estructura:
- `[Mayor].[Menor].[Parche]`.
En los siguientes casos se incrementará el número de versión:
- Mayor: cambios importantes en el proyecto. Por ejemplo: un cambio que rompe la compatibilidad.
- Menor: cambios en la funcionalidad del proyecto, ya sean mejoras o nuevas funcionalidades compatibles con versiones anteriores.
- Parche: correcciones de errores de versiones anteriores.
Se pueden agregar etiquetas para versiones preliminares y para la compilación de metadatos, aunque puede significar que la versión no es estable o que no cumple con los requisitos de compatibilidad.

Además, debe cumplir con los siguientes requisitos:
- Cuando se incrementa el *Mayor*, *Menor* y *Parche* se deben restablecer a 0.
- Cuando se incrementa el *Menor*, *Parche* se debe restablecer a 0.
- La precedencia se determina por la diferencia al comparar identificadores de izquierda a derecha. Por ejemplo: 1.0.0 < 2.0.0 < 2.1.0.

En nuestro caso, las etiquetas se utilizarán principalmente en versiones de producción. Por ejemplo: la primera versión será 1.0.0.

Una vez elegido el número de versión adecuado, es posible crear una nueva release de forma automática. 
Teniendo la rama main actualizada, debes ejecutar estos comandos para crear un nuevo tag:

- Recuerda estar siempre situado en la rama main
- Sutitye "v1.0.0." por el número de versión escogido

1. Creación del nuevo tag
    - `git tag -a v1.0.0 -m “mensaje para añadir al tag que también aparecerá en la release”`

2.  Subir el nuevo tag
    - `git push origin v1.0.0.`

Una vez ejecutados estos comandos, se creará automáticamente un nuevo tag en el repositorio y automáticamente se generará una nueva release con el tag indicado.
