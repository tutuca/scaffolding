# Trabajando con git

---

Esta página describe convenciones y usos de la herramienta de control de
versiones `git`.

## Crear una rama de desarrollo.

Una vez que elegimos un issue y lo movimos a doing. Creamos una rama con el
formato `<numero-issue>-<slug-del-titulo>`. Por ejemplo, si el issue es el
numero 4 y se titula "Levantar wagtail", usaremos:

```bash
$ git checkout master
$ git checkout -b 4-levantar-wagtail
```


## Agregar cambios:

Con el propósito de facilitar la revisión de nuestros cambios buscamos que cada
commit:

- Sean una unidad completa de trabajo. Pudiendo revisarse, agregarse o
removerse individualmente.
- Tiene pocos cambios por commit, en lo posible en un sólo archivo.
- En cualquier caso entre en una sola pantalla.

## El mensaje de commit.

Es muy importante que el mensaje de commit sea claro.
La primer línea no supera los 50 caracteres a forma de título.
Se puede agregar más detalle en el resto del mensaje a forma de cuerpo. Se usa
el modo imperativo como tiempo verbal. Es útil el ejercicio de pensar que el
mensaje de commit responde a la pregunta de ¿Qué pasa si agrego este cambio?.
Por ejemplo: Si se agrega, este cambio va a *agregar soporte multimplataforma*.

Este es un buen molde de mensaje de commit completo:

> Extracto de los cambios en 50 caracteres o menos
>
> Texto explicativo más detallado, sólo si es necesario. La línea en blanco que
> separa el asunto del resto del texto es crucial (a no ser que omitas el
> cuerpo y el mensaje sólo tenga asunto);
>
>     - Se pueden añadir listas
>     - Para las listas se usan guiones o asteriscos (como en Markdown)
>
> En el pie, se pueden poner referencias a los ids de los issue trackers, por
> ejemplo:
>
> Resolves: #123
> See also: #456, #789

No siempre es viable agregar un mensaje tan detallado para cada cambio trivial.
Lo central es considerar que este mensaje ayuda a próximo desarrollador a
continuar el trabajo o revisarlo, este desarrollador podes ser vos.
