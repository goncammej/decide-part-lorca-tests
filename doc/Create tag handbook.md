<h1 align="center">Manual para crear un nuevo tag</h1>

<h5 align="center">Realizado por: Alejandro Gallardo Pelayo</h5>

### Cómo elegir un número de versión correcto

#### Semantic Versioning
Antes de empezar, es importante entender Semantic Versioning. Este es un estándar para asignar números de versión a software con el formato "X.Y.Z" (por ejemplo, "1.2.3"). Bajo este estándar:
* "X" representa la versión principal (cambios mayores). <br>
* "Y" representa la versión secundaria (cambios menores). <br>
* "Z" representa la versión de patch (correción de errores). <br>

### Identificar los cambios
* Cambio Mayor: Si introduces cambios que rompen la compatibilidad con versiones anteriores, incrementa el número de versión mayor (X) y reinicia los valores de versión secundaria (Y) y de patch (Z) a cero. Por ejemplo, pasar de 1.2.3 a 2.0.0.

* Nuevas Funcionalidades: Si agregas nuevas funcionalidades manteniendo la compatibilidad con versiones anteriores, incrementa el número de versión secundaria (Y) y reinicia el número de versión de patch (Z) a cero. Por ejemplo, de 1.2.3 a 1.3.0.

* Corrección de Errores: Si realizas correcciones de errores sin agregar nuevas funcionalidades ni romper la compatibilidad con versiones anteriores, incrementa el número de versión de patch (Z). Por ejemplo, de 1.2.3 a 1.2.4.

#### Crear un nuevo tag
Una vez elegido el número de versión adecuado y con todos los cambios en la rama main, debes ejecutar estos comandos para crear un nuevo tag:

- Recuerda estar siempre situado en la rama main
- Sutitye "v1.0.0." por el número de versión escogido

1. Creación del nuevo tag
    - `git tag -a v1.0.0 -m “mensaje para añadir al tag que también aparecerá en la release”`

2.  Subir el nuevo tag
    - `git push origin v1.0.0.`

Una vez hecho esto, se creará autmáticamente una nueva release con el tag indicado.