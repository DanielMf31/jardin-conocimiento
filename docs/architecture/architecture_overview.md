---
type: artifact
status: draft
created: 2026-08-01
updated: 2026-08-01
owner: DanielMf31
links: [{{FR-NNN}}, {{ADR-NNNN}}]
---

# Architecture overview — Jardin Conocimiento

Front page of the architecture. Read this first, then follow the links. Keep it short: this file
explains how the pieces fit, never how a piece works — that belongs in its component file.

## Purpose in one paragraph

{{ONE_PARAGRAPH_DESCRIBING_WHAT_THE_SYSTEM_DOES_AND_FOR_WHOM}}

## Context view

Describe the system as a single box and everything it talks to. Name every external actor and every
external system, with the direction of the call and what crosses the boundary.

| Actor or external system | Direction | What crosses the boundary | Protocol |
|---|---|---|---|
| {{ACTOR_NAME}} | in | {{DATA_OR_COMMAND}} | {{PROTOCOL}} |
| {{EXTERNAL_SYSTEM}} | out | {{DATA_OR_COMMAND}} | {{PROTOCOL}} |

Assumptions this view makes: {{ASSUMPTIONS}}

Explicitly out of scope: {{NON_GOALS}}

## Diagram

Keep the source in `../multimedia/_src/{{DIAGRAM_SLUG}}.mmd` (or `.dot`) and the rendered image in
`../multimedia/architecture/{{DIAGRAM_SLUG}}.svg`. Render the image from the source; never hand-edit
it. Draw components with `mvp: false` greyed out.

![{{DIAGRAM_CAPTION}}](../multimedia/architecture/{{DIAGRAM_SLUG}}.svg)

If the diagram does not exist yet, keep this section and open an issue to produce it. Do not delete
the placeholder.

## Components

Live index, one row per file in `Components/`. Rebuild it whenever a component is added or its MVP
flag changes; the authoritative list is `Components/Component-index.md`.

| Id | Component | Responsibility (one line) | MVP | Owner |
|---|---|---|---|---|
| {{C-NN}} | [{{COMPONENT_NAME}}](Components/Component-{{NN}}-{{SLUG}}.md) | {{ONE_LINE_RESPONSIBILITY}} | {{TRUE_OR_FALSE}} | DanielMf31 |

MVP cut rationale: {{WHY_THESE_COMPONENTS_ARE_IN_MILESTONE_1}}

## Architecture decisions

Live index of `ADR/`. The authoritative list is `ADR/ADR-index.md`.

| Id | Decision | Status | Affects |
|---|---|---|---|
| {{ADR-NNNN}} | [{{DECISION_TITLE}}](ADR/ADR-{{NNNN}}-{{SLUG}}.md) | {{ADR_STATUS}} | {{C-NN}} |

## Component interaction

Describe the two or three flows that matter. One numbered list per flow, one step per hop.

### Flow: {{FLOW_NAME}}

1. {{C-NN}} receives {{TRIGGER}}.
2. {{C-NN}} calls {{C-NN}} through {{CT-NNNN}}.
3. {{C-NN}} persists {{DATA}} and returns {{RESULT}}.

Failure behaviour: {{WHAT_HAPPENS_WHEN_A_HOP_FAILS}}

## Cross-cutting concerns

| Concern | Approach | Where it is implemented |
|---|---|---|
| Configuration | {{APPROACH}} | {{C-NN}} |
| Logging and tracing | {{APPROACH}} | {{C-NN}} |
| Authentication | {{APPROACH}} | {{C-NN}} |
| Error handling | {{APPROACH}} | {{C-NN}} |
| Persistence and migrations | {{APPROACH}} | {{C-NN}} |

## Quality attributes

Link each non-functional requirement to the structural choice that serves it.

| Id | Attribute | Target | Served by |
|---|---|---|---|
| {{NFR-NNN}} | {{ATTRIBUTE}} | {{MEASURABLE_TARGET}} | {{C-NN_OR_ADR-NNNN}} |

## Known risks and debt

- {{RISK_OR_DEBT}} — mitigation: {{MITIGATION}} — revisit at {{MILESTONE_OR_DATE}}.

## Related documents

- Requirements: `../development/artifacts/ARTIFACT_REQUIREMENTS.md`
- Architecture artifact: `../development/artifacts/ARTIFACT_ARCHITECTURE.md`
- Contracts: `../development/contracts/CONTRACT-index.md`
