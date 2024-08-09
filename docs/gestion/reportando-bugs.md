# Reportando errores

En computación, un _bug_ es un error o falla en el sistema. Puede ser un resultado incorrecto o un comportamiento inesperado de forma que **afecta a los usuarios en su uso normal del sistema**. A veces, una nueva solicitud de función, un refactor o una mejora necesaria pueden disfrazarse de error. Esto debe detectarse oportunamente, el problema debe crearse adecuadamente en el directorio del proyecto y el reportero debe ser notificado.


## Definición de error y niveles de prioridad

#### Definición de error

 - PO estaría de acuerdo en que hay un comportamiento inaceptable del sistema, _Y_ el equipo de desarrollo cree que el comportamiento es inconsistente (con requisitos que se entendieron previamente).

Si se tarda más de 10 minutos en decidir si el problema cumple con esta definición, lanza una moneda para decidir si es un error o no, porque no vale la pena dedicar más tiempo en este momento.


#### Niveles de prioridad

Los _niveles de prioridad_ para los errores deben ser bien conocidos y documentados para todo el proyecto. Como ejemplo / referencia, se pueden usar:

* **Bloqueante**: Errores que están deteniendo el uso de la aplicación. Se necesitan lo antes posible. Dejamos todo lo que estamos trabajando actualmente y solucionamos el problema. \

* **Mayor**: errores que, si bien pueden dificultar el uso de la aplicación, no están afectando ninguna de las funcionalidades principales. Los problemas de rendimiento pueden caer en esta categoría. Haremos todo lo posible para convertir estos errores en requisitos regulares, con una planificación adecuada. Deben abordarse en el sprint actual o en el siguiente. \

* **Menor**: "Quirks" en la aplicación que pueden estar molestando a los usuarios pero que no están afectando la funcionalidad. Haremos todo lo posible para convertir estos errores en requisitos regulares, con una planificación adecuada. Estos deben abordarse en el próximo sprint. \

* **No es un error**: Causado por una falta de comunicación entre un cliente y atención al cliente o entre la atención al cliente y el equipo de desarrollo. Funcionalidad esperada que no se definió previamente. Estos se convertirán en requisitos. \



# Mejores prácticas de informe de errores


### Cómo escribir mejores informes de errores

Pasar un poco más de tiempo escribiendo un informe de errores reduce el tiempo dedicado a volver a encontrar, comprender y, de hecho, corregir el error. También ofrece una mejor oportunidad para que el desarrollador entienda lo que estaba sucediendo cuando se informó el error.

Un informe de error incorrecto requiere un esfuerzo adicional para comprenderlo y, si no se incluyen suficientes detalles, se puede marcar como "no se puede reproducir" y no se puede corregir.

Los errores que siguen un patrón en su título facilitan la búsqueda y reducen el tiempo dedicado a tratar de averiguar si un error es un duplicado o no.

Las siguientes son algunas pautas sobre cómo escribir informes de errores decentes, estas no son la verdad absoluta, pero describen cosas aprendidas de la experiencia.


## Antes de escribir su informe de errores


#### Asegúrese de que el problema aún no se haya informado:

use las herramientas de búsqueda en la aplicación de administración de proyectos para buscar errores que sean similares a los suyos, si hay alguno, vea si es el mismo error. Si el error está marcado como solucionado, asegúrate de que estás probando la última versión, si es así, vuelve a abrir el problema. En cualquier caso, si tiene detalles adicionales para proporcionar este error, agréguelos, cualquier desarrollador que tome este problema más tarde se lo agradecerá.


#### Aísle el problema correctamente:

asegúrese de saber cómo reproducir el problema,



* ¿sucede todo el tiempo?
* ¿Solo sucede cuando está utilizando datos nuevos o un tipo particular de cuenta?
* ¿Esto sucede todo el tiempo o solo cuando el usuario ha realizado una acción específica?
* ¿Esto sucede con todos los navegadores o es específico para el navegador que está utilizando?
* Si sigue los pasos que ha aislado, ¿se activará el error cada vez o solo el 80%, 50%, 10% de las veces?
* ¿El error ocurrió en una instancia local o en el entorno de ensayo?

La lista continúa, pero entiendes lo esencial, trata de hacerte una buena idea de _QUÉ_ pasa y _CUÁNDO_.


## El informe de error real


### Título

El título es probablemente la parte más importante de su error, los títulos buenos son fáciles de buscar y siguen un patrón específico, un buen ejercicio es tratar de resumir el problema en 80 caracteres.

Un buen título debe incluir: La sección / secciones de la aplicación en la que ocurre el error y una breve descripción del error real



* Buen ejemplo: \
 \
 \
 Explorer: un error no se detecta cuando se cambian los productos (en la pagina principal) \
 \

* Mal ejemplo: \
 \
 \
 EntityCollection caso esquina la paginación \
 \


Resumiendo , un buen título debe seguir el siguiente formato:

Ubicación: Descripción breve (entorno opcional)


### Descripción del error

Una descripción útil del error siempre debe incluir lo siguiente:



* _Descripción larga_: Sea lo más descriptivo posible, explique dónde y cómo ocurre este error y por qué piensa es un error \

* _Pasos para reproducir_: incluya todos los pasos necesarios para reproducir este problema, incluidos los detalles de la cuenta utilizada (si corresponde) \

* _Resultado esperado_: explique cuál fue el comportamiento esperado para la aplicación después de seguir los pasos anteriores \

* _Resultado real_: explique qué fue el resultado real. \

* _Detalles del navegador_: cuando pruebe aplicaciones web, es una buena idea incluir el nombre y la versión del navegador que está utilizando, especialmente cuando cree que el problema podría ser inespecífico del navegador \

* _mensaje de error_ (si lo hay): copie cualquier mensaje de error lanzado por el Solicitud aquí \

* _Información adicional_ (si hay alguna disponible): incluya Tracebacks, registros de la consola de JavaScript, etc. \

* _Captura de pantalla_: al probar una aplicación frontend, siempre incluya una captura de pantalla que muestre el error, si es un error que es complicado de reproducir, incluya un breve video que demuestre el error \



### Prioridad

Es importante tratar de evaluar la importancia del error que está informando. Utilice una de las prioridades ya definidas (discutidas anteriormente en este documento).


### Otras recomendaciones generales:



* solo informe un problema en un informe de error. Si es necesario, cree muchos informes.
* Informar hechos. Opcionalmente, incluya sus suposiciones como _información adicional_.
* Concéntrese en la comunicación:
* Intente utilizar la gramática y la puntuación adecuadas.
* El formato de texto es tu amigo, úsalo para llamar la atención sobre cosas importantes en tu descripción.
* Usa oraciones cortas y simples.


## Un ejemplo del mundo real:

**Título:** La interfaz de contenido no aplica los ajustadores cuando el usuario ingresa a la página

**Un mejor enfoque:** Interfaz de contenido: Los filtros no se aplican cuando el usuario ingresa a la página (producción)

**Descripción:** "Necesita más información"

**A mejor la descripción sería:** Este problema ocurre en todas las subvistas de la Interfaz de contenido. Cuando el usuario ingresa a cualquier subvista de la interfaz de contenido, se muestran todos los elementos de contenido para esa sección, independientemente de los filtros seleccionados.

**Pasos para reproducir:**



* Realice una nueva implementación con el script de datos de prueba
* Inicie sesión en la aplicación como foo@example.com
* Vaya a la "Sección de interfaz de contenido"
* Seleccione algunos filtros y guárdelos como predeterminados _Esto podría ser aún más específico y enumerar los filtros que deberían seleccionarse_
* Volver a cargar la página

**Resultado esperado:** los filtros seleccionados deberían haberse aplicado y solo deberían mostrarse los elementos de contenido que coinciden con los criterios

**Resultado real:** los filtros se ignoran y se muestran todos los elementos de contenido para esta sección.

**Detalles del navegador:** Esto se probó en la versión 58.0.3029.110 de Chromium, desarrollada en Ubuntu, que se ejecuta en Ubuntu 16.04 (64 bits), pero parece suceder con todos los navegadores.

**Captura de pantalla:** Aquí querrás incluir un video que muestre cómo reproducir este error y lo que sucede cuando los filtros se aplican realmente.


# Extra:


## un flujo de trabajo típico


## Consideraciones adicionales sobre la gestión del proyecto



* El tablero de trabajo atrasado debe incluir _errores_ problemas de.
* Cualquier error que aparezca que haya sido clasificado y haya decidido que debe corregirse en el sprint actual debe estar en el tablero principal del sprint actual.
* Durante las reuniones retrospectivas, debe recordar cuántos errores tuvimos en el sprint y el esfuerzo que tomó para solucionarlos. Intente encontrar cierta previsibilidad para poder abordar problemas más grandes que podrían ser causas de "síntomas" de errores.


## Referencias

[https://docs.djangoproject.com/en/dev/internals/contributing/bugs-and-features/](https://docs.djangoproject.com/en/dev/internals/contributing/bugs-and-features/)

https://help.ubuntu.com/community/ReportingBugs
