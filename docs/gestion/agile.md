# Notas sobre la metodología

---

Utilizaremos la metodología de desarrollo ágil Scrum.
Nos apoyaremos sobre las funciones que brinda el servicio de Gitlab en cuanto
nos permite tener en un sólo lugar:

- Los objetivos generales y específicos del proyecto
  ([milestones](https://docs.gitlab.com/ee/user/project/milestones/)).

- Las tareas y actividades
  ([issues](https://docs.gitlab.com/ee/user/project/issues/)).

- El código fuente
  ([repositorio](https://docs.gitlab.com/ee/user/project/repository/)).

- El historial de cambios y despliegues
  ([CI/CD](https://docs.gitlab.com/ee/ci/README.html)).

Las actividades que surjan durante el proyecto estarán listadas como
[issues](ciclo-de-vida-issues.md). Esto nos permite establecer clara y
rápidamente el estado del desarrollo.

El issue puede ser una tarea aislada o una User Story.

Los issues se crean en cualquier momento e idealmente cuentan con:

Título: claro, que comunique qué expectativa estará satisfecha cuando se
cierre. En el caso de una historia de usuario usar el formato: "Como <usuario>
quiero <feature> para poder <objetivo>"

**Detalle**: dando a entender cual es la necesidad de la que surje y también
los pasos para verificar que está completa (ver Definition of Done)

**Etiquetas**: que permitan filtrar rápidamente por tipo (desarrollo, diseño,
user-story) y estado (to-do, done).


## Ceremonias

Periódicamente, el equipo debe revisar el tablero de issues para revisar:

- Si todas las necesidades y actividades están registradas o hay que crear nuevos issues.
- El estado de los issues, si son accionables, necesitan mayor definición o se pueden cerrar.
- Si se cuenta con suficientes tareas para ocupar todo el equipo.
- Si se cuenta con suficiente equipo para realizar todas las urgencias.

Con suficientes issues podemos realizar un sprint planning, para tal fin
crearemos un milestone, detallando:

Los objetivos generales a preserguir.

- Fecha de inicio y fin,

- El equipo luego prioriza los issues según su urgencia y factibilidad,
  agregándolos al milestone activo.

- Una vez completo el tiempo del milestone (típicamente, dos semanas), se
  demuestra lo realizado y se planifica un nuevo sprint.

Este seguimiento está articulado por algunas **ceremonias** que se pueden
calendarizar desde un principio:

**Standup**: Puesta en común de avances, trabas y
necesidades generales.

**Sprint planning** (Cada dos semanas): Conversación a fondo sobre las tareas,
su estado, las urgencias, etc. Establece el alcance del sprint.

**Retrospectiva** (Cada dos plannings): Instancia de revisión de funcionamiento
de equipo, busca mejorar la capacidad de entrega del equipo.

Estas ceremonias son los espacios formales de toma de decisión del equipo. Como
es natural que las necesidades no esperen a las ceremonias, nos apoyaremos en
la herramienta Slack para poner en común detalles de cualquier issue, realizar
preguntas o sugerencias y en general llevar el día a día del proyecto.

- #general: conversaciones operativas generales.
- #dev: temas técnicos y detalles de funcionamiento.
- #diseño: propuestas y bocetos sobre la aplicación.
- #random: cualquier otra cosa que no esté contenido en lo anterior.

Al final del día, lo importante es que nosotros tengamos una dinámica clara
para llevar el proyecto y tener evidencia de las decisiones tomadas.

## Roles en la toma de decisión.

**Cliente**

**Coordinador**

**Programador**


## Otras lecturas recomendadas:

Las guias de atlassian (jira) son muy completas para dar un pantallazo de la
metodología, recomiendo empezar por estos artículos:

https://www.atlassian.com/agile/project-management
https://www.atlassian.com/agile/scrum
https://www.atlassian.com/agile/scrum/roles
Agile alliance

Usaremos Gitlab que usa una jerga ligeramente distinta para algunos artefactos.

https://about.gitlab.com/blog/2018/03/05/gitlab-for-agile-software-development/
https://docs.gitlab.com/ee/user/project/issues/

Casi todo en gitlab utiliza markdown.
