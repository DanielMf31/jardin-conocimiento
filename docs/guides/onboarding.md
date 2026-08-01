---
type: index
status: open
created: 2026-08-01
updated: 2026-08-01
owner: DanielMf31
links: []
---


# Onboarding — Jardin Conocimiento

What someone joining this project needs in order to be useful on day one. Keep it to what is
true today; aspirations belong in the backlog.

## First hour

1. Clone the repository and run `make setup`.
2. Run `make verify`. It must exit 0 before you change anything, so that a later failure is
   unambiguously yours.
3. Read [../architecture/architecture_overview.md](../architecture/architecture_overview.md).
4. Read `CLAUDE.md` at the root of the repository: it is the operating manual for anyone,
   human or agent, who changes files here.

## The command contract

Every tool is invoked through `make`. Run `make help` for the full list. `make verify` is the
only definition of done: it chains formatting, linting, type checking, tests and build.

A target that prints `n/a` is a declared no-op, not a broken command. The `targets` block of
`sds.project.json` says which ones are real, planned or not applicable.

`make lint-structure` is the exception that reaches outside this repository: it runs the SDS
structure linter, which lives in the meta-repository. Copy `.env.example` to `.env` and set
`SDS_HOME` to your clone of it, or pass it on the command line.

## How work flows

| Stage | What happens |
|---|---|
| Discovery | The artifact chain is written, one document per gate, each approved by a human |
| Contract freeze | Interfaces, types and failing tests are frozen before any parallel work |
| Implementation | Several workers in parallel, each restricted to a disjoint file whitelist |
| Integration | Wiring without mocks, until `make verify` exits 0 |
| Review | Someone who did not implement it re-runs the commands |

## Local setup notes

To be filled in once the technology stack is decided: required runtime versions, services that
must be running, credentials needed and how to obtain them.
