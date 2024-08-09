# Sobre la gestión de proyecto.

---

Utilizamos la herramienta de gestión de proyectos GitLab para llevar registro de los incidentes, errores o tareas del proyecto.

![Tablero de Tareas en Gilab](/imgs/issues-board.png)

Cómo regla general un **_issue_**:

- Es cualquier tipo de tarea. Realizada por cualquier miembro del equipo
- Su título tiene que ser conciso y dar una noción de su alcance.
- Son atómicos, accionables de forma independiente.
- Deben detallar cuales son los criterios para darlo por **Done** (criterio de aceptación).

Un **_milestone_** refleja un período de dos semanas en el que se resolverá un
conjunto concreto de tareas.

## Etiquetas

Las **_labels_** sirven para indicar el estado de la tarea, así cómo para
clasificarla según alguna característica.

## Ciclo de vida

- **Open**: issues nuevos, sólo requieren un título. Se puede trabajar en su
  definición de forma iterativa. Pueden ser creados por cualquier miembro del
  equipo en cualquier momento.
- **To Do**: pasan a esta columna los issues que cuenten con una descripción
  clara de su alcance y criterios de aceptación definidos. Se los debe asignar a
  un **miltestone**
- **Doing**: son asignadas a un miembro del equipo, en el caso de las tareas de
  _desarrollo_ deben contar con un Merge Request en estado _WIP_.
- **Done**: al completar el desarrollo de una tarea se pasa a esta columna y se
  esperan observaciones y comentarios del resto del equipo. En el caso de tareas
  de _desarrollo_, su MR no debe tener el estado _WIP_. Sobre esto se realiza
  revisión de código. Puede moverse a:
  - **Open**: en el caso que la tarea deba ser re planeada.
  - **Doing**: si tuviera suficientes comentarios cómo para ser retrabajada.
  - **Closed**: si es aceptada y el código se integra a una rama troncal.
- **Closed**: son las tareas aceptadas, completadas con éxito.

## Definición de prioridad

Para que un _issue_ entre en un _milestone_ hace falta un ejercicio de
planificación en dódne el equipo define:

- La **urgencia** de la tarea. Qué tan necesaria o importante es que esté completa para el período del milestone.
- La **complejidad**. Cuánto le cuesta al equipo completarla.

La _urgencia_ empuja una tarea para arriba, la _complejidad_ la empuja para
abajo. El resultado es que las tareas que estén más arriba son las que se
pueden/deben accionar porque son muy urgentes o suficientemente simples. Estas
son movidas al _milestone_ activo para ser resueltas por el equipo.
