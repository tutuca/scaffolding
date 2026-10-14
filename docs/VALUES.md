# Values

How we work, and why. The engineering values are enforced by the tooling and the
convention tests; the working values are enforced by us — they are the conscience
behind the method.

## Engineering values

These are named here but live as *rules* in [`ARCHITECTURE.md`](ARCHITECTURE.md)
and [`TESTING.md`](TESTING.md):

- **One source of truth.** A fact is written once; everything else derives it.
- **Minimal by default.** A resource absent from a role's row is invisible to it;
  nobody gets more access than they need.
- **Contracts, not implementations.** Each layer is tested through its public
  surface, not its wiring.
- **Refusals are messages, not tracebacks.** The person at the terminal did
  nothing wrong; the tool tells them what to do next.

## Working values

Not checked by a linter. They are commitments between the people on the project.

- **You are not your task.** Polishing your skills is a responsibility to
  yourself, not a metric of your worth. ("No sos la tarea que realizás.")
- **Async and flexible by default.** Organize your own day; when schedules
  differ, no one becomes the other's blocker. Minimize interaction moments, and
  make the work legible in writing so it can be accounted for.
- **Respect the operator.** Errors name the fix. Bug reports respect the
  reporter: triage by impact, report facts, focus on communication. The person is
  never the problem.
- **Knowledge is a collective good.** Documentation exists to onboard the next
  person, not to gatekeep them. Writing it is part of the job — ramp-up is a
  duty, not a favour.
- **Trust through kept commitments.** Confidence is built by doing what was said,
  on time and in form. ("Construir confianza a través de compromisos cumplidos.")
- **We are not indifferent.** Software is a workplace like any other — young and
  under-regulated. The people who build it organize, and the tools we make should
  treat people with dignity: operators, reporters, and users alike.
  ("Software, Trabajo, Derechos.")
