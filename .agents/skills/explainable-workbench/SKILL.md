---
name: explainable-workbench
description: Maintain a human-understandable local decision and evidence trail while several authorized coding agents build a workflow. Use when the user needs cumulative agent reports, stakeholder-answer-to-implementation traceability, architecture choices and alternatives, test evidence, failure-handling rationale, or a read-only report/results dashboard before a later independent explanation.
---

# Explainable workbench

Use this Skill only where local file writes, an optional local viewer, and AI assistance are permitted. Follow the current host rules and original task instructions. This workflow is not a license to inspect hidden controls, automate a monitored UI, or transmit confidential data. A no-AI phase ends agent assistance completely.

## 1. Collect understanding before implementation

1. Identify the authorized project root and the current README. Keep the public reference kit separate.
2. Record the goal, actor, raw input, output, hard constraints, soft preferences, missing values, evaluation method, time budget and submit boundary.
3. Inventory safe schema metadata only. Treat every inferred missing-record policy, missing-edge policy, timeout fallback, tie-break, and state owner as **undecided** until a documented rule or stakeholder answer confirms it.
4. Read an existing question ledger rather than duplicate questions. Ask the user which unresolved high-impact question to send to the authorized stakeholder. The participant owns sending and interpreting answers.
5. For each answer, update **source -> rule -> module -> test -> user-visible effect**; distinguish stakeholder statement, explicit task rule, assumption and code-observed fact. After a meaningful answer, propose a follow-up question only if it would change implementation or validation.

## 2. Make design decisions inspectable

Before the first optimizer or workflow engine, compare two viable approaches, such as baseline vs heuristic or exact vs approximate. Include expected complexity, time bound, determinism, explainability, hard-constraint handling, an observable fallback and the limits knowingly accepted. Do **not** fabricate runtime or quality measurements.

Make a module and state ownership map: input parsing -> validation -> normalized data -> candidate creation -> independent scoring -> comparison -> accepted state -> UI. Each state transition must have one writer/owner. Propose a simpler alternative whenever a new DB, service, agent, dependency or persistence layer is not demanded by the task.

## 3. Parallel Codex working agreement

- Select one coordinator for final architecture and integrating changes. Assign one writer per affected file; give other agents read-only reviews or separate files.
- Each agent records a short local event after a meaningful decision, implementation, test, mismatch or handoff. Record **what/why/which alternative/evidence/limitations/next action** rather than merely saying "done".
- Existing test scripts and outcomes take precedence over agent success prose. If a tool could not run, status is `not_run` or `blocked`; UI confirmation remains a separate participant observation.
- User decisions (business rules, algorithm selection, policy exceptions, output commitments) are not silently delegated to an agent.
- Keep reports concise but accumulative. Important reasoning may be detailed, but do not log raw customer/participant rows, secrets, personal links or exam text.

## 4. Optional workbench dashboard

The full public repository contains `tools/report_workbench.py` and `docs/REPORT_WORKBENCH.md`. It uses Python standard library, stores one atomic JSON event per operation under `.review-workbench/events`, and serves only sanitized event summaries.

Within an authorized local project root:

```sh
python3 .hackathon-kit/tools/report_workbench.py --root . note --agent coordinator --kind decision --status confirmed --title 'Choose a small baseline first' --why 'Explains the behavior before optimization' --alternatives 'Immediate complex search' --evidence 'Decision only; actual tests NOT_RUN'
python3 .hackathon-kit/tools/report_workbench.py --root . list
python3 .hackathon-kit/tools/report_workbench.py --root . serve --port 8765
```

If the provided IDE requires a different binding address, first confirm that this is permitted. A port may be inaccessible through the provided Browser even if the local server starts. The dashboard has a **Reports/decisions** tab and **Results/verification** tab; the latter shows recorded evidence and optionally a specified **loopback-only** preview. The candidate must inspect actual UI behavior in the officially provided Browser.

Notes are **local artifacts**, not automatically excluded from submission. Inspect official submission selection before saving or committing them. No Git Push, no uploads, no capture, no remote MCP.

## 5. A brief human explanation after every milestone

Ask the learner to restate in their own words:

- What did we decide and why, compared to one alternative?
- Which files/functions own validation, generation, verification, persistence and comparison?
- Which normal, boundary and failure paths actually ran?
- Which facts are confirmed, assumed, unimplemented, or blocked?
- What did an agent propose that we accepted, corrected or rejected, and why?

Explain unfamiliar concepts once in ordinary language. Never draft or coach while an actual no-AI stage is in progress.

## 6. Final evidence gate

Confirm the required outputs exist in the actual task root, the permitted tests were run, evidence status is truthful, the participant manually checked the UI, and the report/reference folder is not unintentionally submitted. Never mark a local report note as an officially submitted artifact or claim a screenshot was observed without direct evidence.

See [field guide](references/field-guide.md) for the generic event schema, statuses and data-protection boundary.

## Current workroom integration (v3)

For newly prepared projects, prefer `tools/workroom.py` and `docs/WORKROOM_REPORTING_STANDARD.md` on report port 3000 over the legacy `report_workbench.py` viewer at 8765. Do not run both viewers. Report L1 requirements, L2 human decisions, L3 implementation, L4 verified outcomes, with L0 baseline separately. Only recorded observer evidence may be labelled PASS. Keep the actual service independently on 3001.
