# References

Sources found in the projects this scaffold consolidates, grouped by what they
inform. Nothing here is invented — each entry was cited by one of the reviewed
projects, noted in parentheses.

## Architecture

- **Three-tier architecture** — https://en.wikipedia.org/wiki/Multitier_architecture#Three-tier_architecture (bigpear `tecnologias.md`).
- **The Twelve-Factor App** — https://12factor.net/ (bigpear `tecnologias.md`; the scaffold's `conf/` and `.env` policy follow it).
- **Tom Christie, *Django models and encapsulation*** — https://www.dabapps.com/insights/django-models-and-encapsulation/ (invoices `ARCHITECTURE.md`) — "never write to a model field or call `save()` directly"; the source of the "writes belong to the model" rule.
- **James Bennett, *Against service layers in Django*** — https://www.b-list.org/weblog/2020/mar/16/no-service/ (invoices `ARCHITECTURE.md`) — the counterweight that keeps the `service/` layer narrow.
- **Octopus Energy Django conventions** — https://github.com/octoenergy/public-conventions/blob/master/conventions/django.md (invoices `ARCHITECTURE.md`) — factories/mutators/queries grouping; filters on querysets, not managers; properties never hit the database.
- **`tutuca/django_service_layer`** — https://github.com/tutuca/django_service_layer/tree/master/src/reservas (invoices `ARCHITECTURE.md`) — the `conf`/`data`/`service`/`interface` layout the scaffold inherits.
- **Bergin & Winder, *Understanding OOP*** — http://www.csis.pace.edu/~bergin/patterns/ppoop.html (invoices `ARCHITECTURE.md`) — "data, not hierarchy": a searched table beats a class per case.
- **Unix design philosophy** — http://wiki.c2.com/?UnixDesignPhilosophy · the Jargon File http://www.catb.org/~esr/jargon/ · http://harmful.cat-v.org/software/OO_programming/ (bigpear `extrernal-docs.md`).
- **Akin's Laws of Spacecraft Design** — https://spacecraft.ssl.umd.edu/akins_laws.html (bigpear `extrernal-docs.md`).

## Stack

The current stack and the reasons for each choice are in [`STACK.md`](STACK.md),
grouped by layer. The former bigpear/olmo stack — PostgreSQL, Wagtail, ElasticSearch,
Webpack, Sass, Bulma — is recorded in `bigpear/self/docs/desarrollo/tecnologias.md`;
its homepages, for provenance: PostgreSQL https://www.postgresql.org/ · Wagtail
https://docs.wagtail.org/ · ElasticSearch https://www.elastic.co/ · Webpack
https://webpack.js.org/ · Sass https://sass-lang.com/ · Bulma https://bulma.io/.

## Project / configuration management

- **Scrum & Agile** — Atlassian https://www.atlassian.com/agile/scrum · Agile Alliance https://www.agilealliance.org/ · GitLab https://about.gitlab.com/blog/2018/03/05/gitlab-for-agile-software-development/ (bigpear `agile.md`).
- **Prioritised requirements / user stories** — Scott Ambler, http://agilemodeling.com/essays/prioritizedRequirements.htm · http://www.agilemodeling.com/artifacts/userStory.htm (bigpear).
- **Extreme Programming** — http://www.extremeprogramming.org/ (bigpear).
- **Bug reporting** — Mozilla *Bug writing guidelines* https://developer.mozilla.org/en-US/docs/Mozilla/QA/Bug_writing_guidelines (bigpear `reportando-bugs.md`).
- **Estimation** — *Software estimation in the fractal dimension* https://codeburst.io/software-estimation-in-the-fractal-dimension-914569e2ccb9 (bigpear).
- **Keep a Changelog** — https://keepachangelog.com/ (bigpear `contributing.md`).
- **Semantic Versioning** — https://semver.org/ (bigpear `contributing.md`).
- **Git** — *Oh shit, git!* https://ohshitgit.com/ · GitLab flow https://docs.gitlab.com/ee/workflow/gitlab_flow.html (bigpear).

## Core values

- **Hadley Wickham, *Tidy Data*** (Journal of Statistical Software 59(10), 2014) — https://www.jstatsoft.org/article/view/v059i10 (invoices `DATA.md`) — one variable per column, one observation per row, one unit per table.
- **Ellis & Leek, *How to share data for collaboration*** (PeerJ Preprints, 2017) — https://peerj.com/preprints/3139/ (invoices `DATA.md`) — raw data, tidy data, a code book, and the recipe.
- **Jorge Sábato, *El triángulo de la ciencia y la tecnología*** — the "triángulo de Sabato" in the AGC "Software, Trabajo, Derechos" deck.
- **AGC — Asociación Gremial de Computación** — the workers' organization these values come from; Personería Gremial: https://www.boletinoficial.gob.ar/detalleAviso/primera/234133/20200826 (AGC slides).
- **Escalando bigpear** (internal) — "No sos la tarea que realizás", "Trabajar diferido", "Cultivando peras".

## Documentation structure

- **Wagtail documentation** — https://docs.wagtail.org/ — the `users`/`admin`/`developer` audience split that the scaffold's guides mirror (bigpear/olmo docs, which follow Wagtail's own layout).
- **Keep a Changelog** — https://keepachangelog.com/ — the CHANGELOG format.
- **Semantic Versioning** — https://semver.org/ — the versioning the changelog keys off.
- **Ellis & Leek's data package** (above) — the "code book + recipe" idea applied to data documentation.
