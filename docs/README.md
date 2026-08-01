---
type: index
status: open
created: 2026-08-01
updated: 2026-08-01
owner: DanielMf31
links: []
---


# Jardin Conocimiento — documentation

This tree is the source of truth for everything written about this project. The knowledge vault
receives a read-only mirror of it; nothing ever flows back from there.

## Start here

| I want to | Read |
|---|---|
| Work on this project for the first time | [guides/onboarding.md](guides/onboarding.md) |
| Run something | [guides/how-to.md](guides/how-to.md) |
| Understand how the pieces fit | [architecture/architecture_overview.md](architecture/architecture_overview.md) |
| Know why a decision was taken | [architecture/ADR/ADR-index.md](architecture/ADR/ADR-index.md) |
| See what is being built and why | [development/artifacts/](development/artifacts/) |
| See what comes next | [development/backlog/milestones/milestone-index.md](development/backlog/milestones/milestone-index.md) |
| Know what the interfaces are | [development/contracts/CONTRACT-index.md](development/contracts/CONTRACT-index.md) |
| Learn what the system itself got wrong | [development/discrepancies.md](development/discrepancies.md) |

## State of the project

The project has just been generated. The artifact chain is empty: it is written one document at
a time, each behind a gate that only a human passes. Until the architecture artifact is
approved there is no backlog, and that is a correct state rather than a gap.

## Rules that hold everywhere in this tree

- Every document opens with the front matter block: type, status, created, updated, owner, links.
- Links are relative markdown links. Wiki-style double-bracket links and absolute machine paths
  are rejected by the linter.
- Files whose name ends in `-index.md` are generated. Do not edit them by hand.
- Identifiers are unique, never reused, and follow the formats fixed by the specification.
