---
type: log
status: open
created: 2026-08-01
updated: 2026-08-01
owner: DanielMf31
links: []
---

# Discrepancies

Append-only ledger of **systemic** failures of the system itself, and of the improvement each one
produced. This is the feedback loop that keeps the templates, the agents and the specification
honest: entries here are folded back into `spec/` and `templates/` periodically.

Never rewrite or delete an entry. A correction is a new entry.

## What belongs here

Admit an observation only when all three hold.

1. **The system caused it, not the code.** The template was ambiguous, the agent definition was
   missing an instruction, the specification did not cover the case, a gate let bad work through.
2. **It would happen again** to a different unit of work, in a different project, with the same
   templates. Recurrence is the test — one unlucky bug is not systemic.
3. **An improvement was applied**, or is written down as the next change. An observation with no
   applied improvement is a complaint, not a discrepancy.

## What does not belong here

- A single failing test, a typo, a wrong variable name. Those go in the review report for that issue.
- A design disagreement. That is an ADR.
- Work still in progress. Log it in the issue's implementation log.

Rule of thumb: if the fix touches only this project's code, it is not systemic. If the fix touches a
template, an agent definition or the specification, it is.

## Format

One line per entry, exactly this shape, newest at the bottom:

```
- [DATE · unit] observed discrepancy → applied improvement
```

- `DATE` is `YYYY-MM-DD`.
- `unit` is the identifier of the work where it surfaced: `{{MN-ENN-INNN}}`, `{{MN-ENN}}`, `{{MN}}`,
  or the agent name when it surfaced outside an issue.
- The arrow is mandatory and separates observation from improvement. No arrow, no entry.
- One line. If it needs a paragraph, the entry is not distilled enough yet.

## Log

- [2026-08-01 · {{MN-ENN-INNN}}] {{OBSERVED_SYSTEMIC_DISCREPANCY}} → {{APPLIED_IMPROVEMENT}}
- [2026-08-01 · {{MN-ENN}}] {{OBSERVED_SYSTEMIC_DISCREPANCY}} → {{APPLIED_IMPROVEMENT}}
- [2026-08-01 · {{AGENT_NAME}}] {{OBSERVED_SYSTEMIC_DISCREPANCY}} → {{APPLIED_IMPROVEMENT}}

## Folding back

Review this file at every milestone close. For each entry, decide one of:

| Outcome | Action |
|---|---|
| Template defect | Edit the template in `templates/`, note the change in the commit message |
| Agent defect | Edit the agent definition, refresh the manifest hashes |
| Specification gap | Open a pull request against `spec/structure_v1.md` per its change policy |
| Already fixed elsewhere | Leave the entry, add a follow-up line pointing at the fix |

Entries are never removed after folding back. The history of what the system got wrong is the reason
it stops getting it wrong.
