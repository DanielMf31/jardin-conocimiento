---
type: log
status: open
created: 2026-08-01
updated: 2026-08-01
owner: DanielMf31
links: [{{MN}}]
---

# Metrics — Jardin Conocimiento

Readable view of `metrics.json`, which is the machine-readable source. Never edit numbers here by
hand: update the JSON, then regenerate this file. If the two disagree, the JSON wins.

Reporting period: 2026-08-01 to 2026-08-01 · Generated at: {{YYYY-MM-DDTHH:MM}}

## Definitions

Measure the same way every period or the trend means nothing.

| Metric | Definition | Clock starts | Clock stops |
|---|---|---|---|
| Lead time | Time from a need being recorded to it running in production | Issue created | Change deployed |
| Cycle time | Time actually spent building it | Issue moves to `in-progress` | Issue moves to `done` |
| Throughput | Units finished per period | — | — |
| First-pass approval rate | Share of reviews approved without a second pass | — | — |
| Rework after review | Share of issues that needed changes after a review verdict | — | — |

## Delivery

| Metric | Value | Unit | Previous period | Trend |
|---|---|---|---|---|
| Lead time (median) | {{N}} | days | {{N}} | {{UP_DOWN_FLAT}} |
| Lead time (p85) | {{N}} | days | {{N}} | {{UP_DOWN_FLAT}} |
| Cycle time (median) | {{N}} | hours | {{N}} | {{UP_DOWN_FLAT}} |
| Cycle time (p85) | {{N}} | hours | {{N}} | {{UP_DOWN_FLAT}} |
| Throughput | {{N}} | issues per week | {{N}} | {{UP_DOWN_FLAT}} |
| Work in progress (avg) | {{N}} | issues | {{N}} | {{UP_DOWN_FLAT}} |

## Quality of the review loop

| Metric | Value | Unit | Previous period | Trend |
|---|---|---|---|---|
| First-pass approval rate | {{PCT}} | percent | {{PCT}} | {{UP_DOWN_FLAT}} |
| Rework rate after review | {{PCT}} | percent | {{PCT}} | {{UP_DOWN_FLAT}} |
| Review passes per issue (median) | {{N}} | passes | {{N}} | {{UP_DOWN_FLAT}} |
| Reports rejected for missing transcripts | {{N}} | reports | {{N}} | {{UP_DOWN_FLAT}} |
| Whitelist violations | {{N}} | issues | {{N}} | {{UP_DOWN_FLAT}} |
| Contracts broken mid-epic | {{N}} | contracts | {{N}} | {{UP_DOWN_FLAT}} |

A first-pass approval rate near 100 percent is not automatically good news: check whether review is
actually re-running commands, or whether the work is being split too small to fail.

## DORA

| Metric | Value | Unit | Band | Previous period |
|---|---|---|---|---|
| Deployment frequency | {{N}} | deploys per week | {{ELITE_HIGH_MEDIUM_LOW}} | {{N}} |
| Lead time for changes | {{N}} | hours from commit to production | {{ELITE_HIGH_MEDIUM_LOW}} | {{N}} |
| Change failure rate | {{PCT}} | percent of deploys needing remediation | {{ELITE_HIGH_MEDIUM_LOW}} | {{PCT}} |
| Failed deployment recovery time | {{N}} | hours to restore service | {{ELITE_HIGH_MEDIUM_LOW}} | {{N}} |

Speed metrics without the two stability metrics are misleading. Report all four or none.

## Per milestone

| Milestone | Issues closed | Median cycle time | First-pass approval | Status |
|---|---|---|---|---|
| {{MN}} | {{N}} | {{N}} hours | {{PCT}} | {{MILESTONE_STATUS}} |

## Agent and human split

| Actor kind | Issues closed | Median cycle time | First-pass approval |
|---|---|---|---|
| Agents | {{N}} | {{N}} hours | {{PCT}} |
| Humans | {{N}} | {{N}} hours | {{PCT}} |

## Reading of this period

{{THREE_TO_FIVE_LINES_INTERPRETING_THE_NUMBERS_AND_NAMING_ONE_ACTION}}

## How these numbers are produced

- Source of truth: `metrics.json` in this directory.
- Collection command: `{{COMMAND_THAT_REGENERATES_THE_JSON}}`
- Inputs: issue front matter timestamps, review reports, deployment records.
- Known gaps: {{WHAT_IS_NOT_MEASURED_YET_AND_WHY}}
