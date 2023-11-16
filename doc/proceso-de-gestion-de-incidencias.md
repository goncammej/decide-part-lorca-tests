# Proceso de Gestión de Incidencias

## ¿Qué es una incidencia?

Una incidencia es un problema que se ha detectado, relacionado con el software o la documentación del proyecto.

## ¿Qué es el Registro de Incidencias?

El Registro de Incidencias es un Project Board de GitHub, en el que se registran todas las incidencias detectadas. Cada incidencia se representa como una Issue.

## ¿Qué hacer cuando se detecta una incidencia?

Cuando se detecta una incidencia, se debe seguir el siguiente proceso:

1. Se crea una Issue en el Registro de Incidencias, dentro de la columna *OPEN*,  indicando el nombre de la incidencia y el módulo al que hace referencia, separado por un guión. Por ejemplo: *Import/Export Census - Census*. Si la incidencia está relacionada con la documentación, en lugar de un módulo, se indica *Doc*. Por ejemplo: *Change documentation - Doc*.
2. Si es necesario, se realiza una descripción detallada de la Issue.
3. Se asigna la Issue a la persona responsable de resolverla.
4. Se asigna una Label a la Issue indicando el grupo al que pertenece la persona responsable de resolverla (*lorca-1* o *lorca-2*).
5. Se asigna una Label a la Issue indicando el tipo de incidencia (*Error*, *Improvement* o *New feature*).
6. Se asigna una Label a la Issue indicando la prioridad de la incidencia (*High*, 
*Medium* o *Low*).

## ¿Cuándo queda resuelta una incidencia?

Una incidencia queda resuelta cuando se ha realizado una modificación en el software o la documentación del proyecto que soluciona el problema que se ha detectado, y además, dicha modificación se ha subido al menos a la rama `develop` del repositorio.

## ¿Qué hacer cuando se resuelve una incidencia?

Cuando se resuelve una incidencia, se debe seguir el siguiente proceso:

1. Se mueve la Issue a la columna *CLOSED* del Registro de Incidencias.
2. Se cierra la Issue.

