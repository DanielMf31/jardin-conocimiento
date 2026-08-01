# Jardin Conocimiento — rules for agents working in this repository

This file is read by every agent that touches this project. It is short on purpose: everything here
is operative. The reasoning behind these rules lives in the SDS meta-repository, under
`spec/structure_v1.md`.

## What this project is

{{ONE_LINE_WHAT_THIS_PROJECT_IS}}

Slug: `jardin-conocimiento` · Created: 2026-08-01 · Manifest: `sds.project.json`.

The manifest declares the language, the paths and which `make` targets are `real`, `planned` or
`n/a`. Read it before assuming a command does anything.

## Commands: `make <target>`, and nothing else

Never type `pytest`, `npm test`, `go build`, `ruff`, `tsc` or any other tool directly. Every command
this project accepts is a target of the `Makefile`:

```
setup  fmt  fmt-check  lint  typecheck  test-unit  test-integration  test
e2e  build  run  contracts-check  verify  clean
```

- `make verify` (= `fmt-check` + `lint` + `typecheck` + `test` + `build`) is **the only definition of
  done**. Work is finished when that command exits 0, never because prose says so.
- A target that prints `n/a` is a declared no-op, not a broken command. If you need it to do
  something real, change the `*_CMD` variable at the top of the `Makefile` and update
  `sds.project.json` in the same commit.
- Report exit codes in the implementation log. A command whose exit code was not observed did not run.

## Where documentation lives

Documentation lives beside the code, in `docs/`, and the repository is its source of truth. The
knowledge vault only ever receives a read-only mirror; nothing flows back from it.

| Path | What it holds |
|---|---|
| `docs/development/artifacts/` | The artifact chain: problem, domain, requirements, tech stack, architecture, milestones |
| `docs/development/contracts/` | Frozen interfaces (`CONTRACT-NNNN-<slug>.vN.md`) and their schemas |
| `docs/development/backlog/` | Milestones, epics, issues |
| `docs/development/development_log/` | Daily and monthly execution trace |
| `docs/development/discrepancies.md` | Append-only ledger of systemic failures of the system itself |
| `docs/architecture/` | Overview, ADRs, components |
| `docs/guides/` | How-to and onboarding |

Rules that hold everywhere in `docs/`:

- Every document starts with the front matter block of §6.1 (`type`, `status`, `created`, `updated`,
  `owner`, `links`).
- Links are relative markdown links. `[[wikilinks]]` are forbidden, and so are absolute machine paths.
- `*-index.md` files are **generated**. Do not hand-edit them; run the structure linter with `--fix`.
- Identifiers follow §4: `FR-NNN`, `NFR-NNN`, `ADR-NNNN`, `C-NN`, `CT-NNNN`, `MN`, `MN-ENN`,
  `MN-ENN-INNN`. They are unique and never reused.

## File whitelist

Every issue declares in its `user_story.md` the exact files it may touch. That whitelist is a hard
boundary:

- Do not create, edit, move or delete a file outside it — not even a "tiny fix", not even a typo.
- If the work cannot be finished without touching something outside the whitelist, **stop and
  report**. Hitting the boundary is information the conductor needs; silently crossing it corrupts a
  parallel wave.
- Whitelists of issues running at the same time are disjoint. If two issues need the same file, the
  split was wrong and it belongs back in wave 0.

## Commits

Only `sds-scribe` commits. Every other agent leaves the working tree dirty and reports what it
changed. Do not run `git commit`, `git push`, `git rebase` or `git reset`.

## Frozen contracts are read-only

A contract with `status: frozen` cannot be edited, not even to "fix" it. Implement against it as it
is written. If it is genuinely broken, stop: the epic returns to wave 0, a new version `CT-NNNN v2`
is issued, v1 is marked `superseded_by`, and the incident is recorded in
`docs/development/discrepancies.md`. This is expensive on purpose.

## Gates

Artifacts are written with `status: proposed`. **Only a human approves** by setting
`status: approved` with `approved_by` and `approved_at`. Never approve your own work, and never
start work downstream of an unapproved gate — the linter fails on it.

## Pointers to the specification

In the SDS meta-repository:

- `spec/structure_v1.md` — the contract: layout (§2.1), artifact chain (§3), identifiers (§4),
  commands (§5), waves (§7), levels of done (§8).
- `spec/conventions/` — coding, testing, documentation, naming, definition of done, agentic workflow.
- `scripts/structure_lint.py` — run it against this project before declaring anything finished.

Agent definitions for this project are pinned under `.claude/agents/` with a hash manifest. If you
believe one is wrong, report it; do not edit the copy, because drift from the canonical definition is
a lint failure.
