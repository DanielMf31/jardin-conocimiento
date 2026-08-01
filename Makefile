# Jardin Conocimiento — the command contract (spec/structure_v1.md §5)
#
# Agents invoke `make <target>` and nothing else. They never type `pytest`, `npm test` or `go test`.
# That indirection is the whole point: changing the test runner must not touch a single agent
# definition, and a reviewer on a machine that knows nothing about this project can still verify it.
#
# HOW TO ADAPT THIS FILE TO A LANGUAGE
#   Do not edit the targets. Edit the *_CMD variables below, which are the only language-specific
#   part. Every command is overridable from the environment (`?=`), so CI can substitute one without
#   editing the file.
#
# A TARGET IS NEVER DELETED
#   A target that does not apply to this project stays as an explicit no-op (`echo "n/a"`), because
#   review always calls the full set and a missing target is indistinguishable from a broken one.
#   `sds.project.json` declares which targets are `real`, `planned` or `n/a`, so a reviewer can tell
#   a legitimate no-op from an unimplemented one. Keep the two in step.
#
# `make verify` is the only definition of done.

SHELL := /bin/bash

# Fail on the first error instead of half-running a pipeline.
.SHELLFLAGS := -eu -o pipefail -c

.DEFAULT_GOAL := help

# `verify` chains five gates whose order carries meaning: formatting before linting, linting before
# tests, tests before build. Running them in parallel would surface the last failure instead of the
# first, so this Makefile is serial on purpose.
.NOTPARALLEL:

# ---------------------------------------------------------------------------
# The only part to edit — one command per target
# ---------------------------------------------------------------------------

SETUP_CMD             ?= npm ci
FMT_CMD               ?= npx prettier . --write
FMT_CHECK_CMD         ?= npx prettier . --check
LINT_CMD              ?= echo "n/a"
TYPECHECK_CMD         ?= npx tsc --noEmit
TEST_UNIT_CMD         ?= npx tsx --test
TEST_INTEGRATION_CMD  ?= echo "n/a"
E2E_CMD               ?= echo "n/a"
BUILD_CMD             ?= npx quartz build
RUN_CMD               ?= npx quartz build --serve
CONTRACTS_CHECK_CMD   ?= echo "n/a"
CLEAN_CMD             ?= rm -rf public .quartz-cache

# Where the code lives; keep in step with `paths` in sds.project.json.
SRC_DIR   ?= content
TESTS_DIR ?= tests
DOCS_DIR  ?= docs

# ---------------------------------------------------------------------------
# The one tool that does not live in this repository
# ---------------------------------------------------------------------------
#
# The structure linter judges this project against `spec/structure_v1.md`, which is owned by the SDS
# meta-repository — copying it in would fork it, and a forked linter stops being a shared rule. So
# the target reaches out, and `SDS_HOME` says where. The default assumes the layout the generator
# produces: the project is a sibling of the meta-repository. Override it from the environment
# (`.env.example` carries the value the generator recorded) or inline on the command line.
SDS_HOME   ?= $(abspath $(CURDIR)/../software-development-system)
SDS_LINTER := $(SDS_HOME)/scripts/structure_lint.py
SDS_SYNC   := $(SDS_HOME)/scripts/sync_content.py

# The slug this repo is registered under in the SDS registry (config/projects.json). `make sync`
# only does anything if that entry has a `contentSync` block; a project with no authored content in
# the vault leaves it out and the target is a helpful no-op.
SYNC_SLUG  ?= jardin-conocimiento

# ---------------------------------------------------------------------------
# Targets — the contract. Do not rename, do not delete.
# ---------------------------------------------------------------------------

.PHONY: help setup fmt fmt-check lint typecheck test-unit test-integration test e2e \
        build run contracts-check verify clean lint-structure sync

help: ## List the targets of the command contract
	@echo "Jardin Conocimiento — make targets (spec/structure_v1.md §5)"
	@echo
	@grep -hE '^[a-z][a-z0-9-]*:.*?## ' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'
	@echo
	@echo "  Behind each target sits a *_CMD variable at the top of the Makefile."

setup: ## Install dependencies and prepare the environment
	@$(SETUP_CMD)

fmt: ## Format the code in place
	@$(FMT_CMD)

fmt-check: ## Verify formatting without writing anything
	@$(FMT_CHECK_CMD)

lint: ## Static analysis
	@$(LINT_CMD)

typecheck: ## Type checking
	@$(TYPECHECK_CMD)

test-unit: ## Unit tests
	@$(TEST_UNIT_CMD)

test-integration: ## Integration tests
	@$(TEST_INTEGRATION_CMD)

test: test-unit test-integration ## Unit plus integration tests

e2e: ## End-to-end run over the critical path
	@$(E2E_CMD)

build: ## Produce the deployable artifact
	@$(BUILD_CMD)

run: ## Run the project locally
	@$(RUN_CMD)

contracts-check: ## Validate implementations against the frozen contracts
	@$(CONTRACTS_CHECK_CMD)

# Deliberately outside `verify`: it depends on a checkout that is not this repository, and a
# definition of done that fails on a machine where the meta-repository is missing would be a
# definition of done nobody can trust.
lint-structure: ## Check the documentation tree against spec/structure_v1.md (needs SDS_HOME)
	@if [ ! -f "$(SDS_LINTER)" ]; then \
		echo "lint-structure: no SDS installation found."; \
		echo ""; \
		echo "  SDS_HOME  = $(SDS_HOME)"; \
		echo "  expected  = $(SDS_LINTER)   (missing)"; \
		echo ""; \
		echo "  SDS_HOME must point at a clone of the software-development-system meta-repository,"; \
		echo "  which owns spec/structure_v1.md and the linter that enforces it. Pick one:"; \
		echo "    make lint-structure SDS_HOME=/path/to/software-development-system"; \
		echo "    cp .env.example .env  &&  set SDS_HOME there, then: set -a; . ./.env; set +a"; \
		echo "    export SDS_HOME=/path/to/software-development-system"; \
		echo ""; \
		echo "  The default assumes the meta-repository is a sibling of this project."; \
		exit 1; \
	fi
	@python3 "$(SDS_LINTER)" .

# Also outside `verify`, and for the same reason as lint-structure: it needs the meta-repository and
# the Obsidian vault, neither of which exists on a CI runner. Content is authored in the vault and
# synced here on the laptop; CI builds from what was committed. See spec/structure_v1.md §6.
sync: ## Sync authored content from the vault into this repo (laptop only, needs SDS_HOME + vault)
	@if [ ! -f "$(SDS_SYNC)" ]; then \
		echo "sync: no SDS installation found at SDS_HOME=$(SDS_HOME)"; \
		echo "  Point SDS_HOME at a clone of the software-development-system meta-repository."; \
		exit 1; \
	fi
	@python3 "$(SDS_SYNC)" --project "$(SYNC_SLUG)"

verify: fmt-check lint typecheck test build ## The definition of done: fmt-check, lint, typecheck, test, build
	@echo "verify: every gate exited 0"

clean: ## Remove generated output
	@$(CLEAN_CMD)
