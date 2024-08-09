# Índice de documentos de desarrollo

---

Aquí encontrará toda la información necesaria para el desarrollo del proyecto,
como por ejemplo tecnologías, arquitecturas y buenas prácticas.

- [Guía de desarrollo](dev-guide.md)
- [Buenas pácticas para el uso de Git](../dev/git-guide.md)
- [Liberar versiones nuevas](releases.md)
- [Reporte de errores](issues.md)
- [Otros links de interés](extrernal-docs.md)

## Arquitectura


## Convenciones

## Python

## Frontend

```
.
├── src/
│   └── ui/                 -> Proyecto Vue para la interfaz gráfica.
│      ├── scss            -> Estilos usando bulma.
│      ├── components/     -> Componentes presentacionales.
│      ├── models/         -> Comunicación bidireccional via REST.
│      ├── pages/          -> Páginas, puntos de entrada vue-multipage.
│      ├── router/         -> Directivas vue-router.
│      ├── store/          -> Store de estado de la aplicación.
│      ├── utils/          -> Utilidades genéricas
│      ├── public/         -> presentacionales
│      └── main.js         -> Punto de entrada para compilación
...
```

## Docs
```
.
├── docs
│  ├── about.md
│  ├── assets
│  │  ├── logo-small.png
│  │  └── logo.svg
│  ├── css
│  │  └── extra.css
│  ├── dev
│  │  ├── dev-guide.md
│  │  ├── extrernal-docs.md
│  │  ├── git-guide.md
│  │  ├── index.md
│  │  └── releases.md
│  ├── gestion
│  │  ├── agile.md
│  │  ├── ciclo-de-vida-issues.md
│  │  ├── index.md
│  │  └── reportando-bugs.md
│  ├── imgs
│  ├── index.md
│  ├── tech
│  └── users
...
```