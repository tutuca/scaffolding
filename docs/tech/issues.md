# Sobre la gestión de proyecto, issues.

---

La herramienta de gestión de proyectos GitLab cuenta con:

- **Issues**
- **Miltestones**
- **Labels**

Cómo regla general un *issue*:
- Es cualquier tipo de tarea. Realizada por cualquier miembro del equipo

- Su título tiene que ser conciso y dar una noción de su alcance.

- Son atómicos, accionables de forma independiente.

- Deben detallar cuáles son los criterios para darlo por **Done** (criterio de
aceptación).

Un *milestones* refleja un período de dos semanas en el que se resolverá un
conjunto concreto de tareas.

Los *labels* sirven para indicar el estado de la tarea, así cómo para
clasificarla según alguna característica.


## Ciclo de vida

- **Open**: issues nuevos, sólo requieren un título. Se puede trabajar en su
definición de forma iterativa. Pueden ser creados por cualquier miembro del
equipo en cualquier momento.

- **To Do**: pasan a esta columna los issues que cuenten con una descripción
clara de su alcance y criterios de aceptación definidos. Se los debe asignar a
un **miltestone**

- **Doing**: son asignadas a un miembro del equipo, en el caso de las tareas de
*desarrollo* deben contar con un Merge Request en estado *WIP*.

- **Done**: al completar el desarrollo de una tarea se pasa a esta columna y se
esperan observaciones y comentarios del resto del equipo. En el caso de tareas
de *desarrollo*, su MR no debe tener el estado *WIP*. Sobre esto se realiza
revisión de código. Puede moverse a:

  - **Open**: en el caso que la tarea deba ser re planeada.
  - **Doing**: si tuviera suficientes comentarios como para ser retrabajada.
  - **Closed**: si es aceptada y el código se integra a una rama troncal.

- **Closed**: son las tareas aceptadas, completadas con éxito.


## Definición de prioridad

Para que un *issue* entre en un *milestone* hace falta un ejercicio de
planificación en donde el equipo define:

- La **urgencia** de la tarea. Qué tan necesaria o importante es que esté
completa para el período del milestone.

- La **complejidad**. Cuánto le cuesta al equipo completarla.


La *urgencia* empuja una tarea para arriba, la *complejidad* la empuja para
abajo. El resultado es que las tareas que estén más arriba son las que se
pueden/deben accionar porque son muy urgentes o suficientemente simples. Estas
son movidas al *milestone* activo para ser resueltas por el equipo.
