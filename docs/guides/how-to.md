---
type: index
status: open
created: 2026-08-01
updated: 2026-08-01
owner: DanielMf31
links: []
---


# How-to — Jardin Conocimiento

Task-shaped recipes. One heading per task, in the imperative, with commands that can be pasted.
If a recipe needs a paragraph of explanation, that explanation belongs in the architecture
documentation and this page links to it.

## Run the command contract

```bash
make help          # list the targets
make setup         # install dependencies
make run           # run locally
make verify        # fmt-check + lint + typecheck + test + build
```

## Check the structure of the documentation

From this project, through the command contract:

```bash
make lint-structure                  # needs SDS_HOME (see .env.example)
make lint-structure SDS_HOME=/path/to/software-development-system
```

Or from the SDS meta-repository, pointing at this project:

```bash
python3 scripts/structure_lint.py <path-to-this-project>
python3 scripts/structure_lint.py <path-to-this-project> --fix     # regenerate the indexes
python3 scripts/structure_lint.py <path-to-this-project> --agents  # detect agent drift
```

## Add a decision record

Copy the ADR template from the meta-repository into `../architecture/ADR/`, name it with the
next free identifier, fill it in, then regenerate the index with `--fix`. Never edit an index by
hand.

## Recipes still to be written

Deploying, restoring from a backup and rolling back are written here as soon as they exist. A
recipe that has never been executed is a guess and does not belong on this page.
