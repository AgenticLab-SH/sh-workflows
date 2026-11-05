# Human-led workflow before, during and after an AI implementation

Reusable public development guidance only. This document contains no confidential employer rules, employee records, actual examination questions or answers.

## Stage A: Discover evidence and ask the right stakeholder

1. Read the task root README and the available data dictionary. Identify row grain, expected fields, relationships, units, and required outputs. Do not publish real rows.
2. Distinguish explicit specification, observed schema, domain assumption, stakeholder statement, and conflict. For data anomalies, report a count/percentage and generic type; no personal values.
3. Identify unknown decisions affecting the result: inclusion policy, missing record policy, missing travel/cost matrix entries, duplicate keys, tie rules, timeout, exact-vs-approximate requirement, approval and audit behavior. These are **examples of generic planning problems**, not official challenge rules.
4. Turn unknowns into **one-fact questions**, ranked by potential to change output, state, permissions, algorithm or test. Use the existing `stakeholder-agent-questioning` Skill, `tools/question_candidates.py`, `templates/QUESTION_LEDGER.csv`, and `docs/STAKEHOLDER_QUESTIONS.md` instead of building a second question system.
5. The authorized user manually sends the questions through the authorized stakeholder channel, pastes answers only into permitted local files, and reviews every proposed decision. Codex then reads the new answer, points to the affected requirements and tests, and raises only valuable follow-ups.

## Stage B: Choose the simplest defensible optimization or workflow architecture

Present alternatives before implementation, with the following decision card:

| Field | Required explanation |
| --- | --- |
| Objective | What improves, in units, with stakeholder-approved weight if several objectives? |
| Hard constraints | What must never be violated? Independent constraint checker needed? |
| Baseline | Simplest runnable deterministic feasible method and measured outcome |
| Alternatives | Exact/bounded/heuristic/hybrid, complexity and expected trade-offs |
| Selected design | Human choice, not just the agent's suggestion |
| Time/runtime | What happens if a budget is reached or an upstream input is invalid? |
| State owner | Which module owns accepted/current candidate vs temporary proposals? |
| Verification | Small exact checks, independent scoring, boundary and failure cases |
| Honest limits | No optimality claim if none was proved; estimate versus observation labeled |

Algorithm labels do not imply a particular problem. Only select an approach after confirming the actual task type, size and limits. Favor a feasible baseline, a separate validator and an explainable candidate comparison over an unverified 'optimal' claim.

## Stage C: Name owners and data flow

A small, maintainable arrangement often looks like:

```text
input/source -> schema checks -> normalized records -> candidate builder
             -> independent feasibility checks -> scoring/metrics
             -> candidate comparison -> accepted-state owner -> user views
```

State ownership must be explicit. Candidate generation must not silently replace the accepted/current operating plan. A human approval step is part of the state transition only when required by the actual task. Original inputs remain unchanged. File-based storage is enough for a small local task unless the requirements demand concurrency, persistence or accounts.

## Stage D: Test actual and unexpected inputs

| Area | Generic questions to verify |
| --- | --- |
| Normal | Does a well-formed input yield valid, reproducible output? |
| Missing records | Does the tool report uncertainty rather than invent a value? |
| Missing cross-reference | Is the missing relation surfaced and safely handled? |
| Invalid type/unit | Is the error explainable and independent of UI? |
| Runtime limit | Does a bounded fallback return a clearly labeled best-known feasible candidate or a safe failure? |
| Infeasibility | Are violated hard constraints listed; no false success? |
| Multiple candidates | Are scores calculated independently and displayed with same rules? |
| State mutation | Does proposing a candidate preserve the previously accepted state until authorized? |
| UI | Can a user verify who/what/why from the delivered interface? |

**Do not assert these cases were executed.** Test templates become `verified` only after actual local test output is observed.

## Stage E: Human decision & multi-agent explainability

Every meaningful agent milestone reports: problem, decision, alternatives, file/function, real test evidence, risk and next question. Keep an append-only local report per agent via `tools/report_workbench.py`; a read-only browser merges the notes. The human should be able to explain the latest result without learning the entire codebase.

Six categories worth understanding *before* a later independent explanation are:

- Approach and why one feasible alternative was not chosen
- Architecture/module ownership and data-flow responsibilities
- Implemented versus confirmed assumption versus intentionally excluded
- Normal flow and failure/recovery behavior
- Quality evaluation, independent validation and next improvement
- AI collaboration history: which proposals were accepted, revised or rejected, and on what evidence

These are **generic study categories**, not quotations or reconstructions of any assessment questions. Never prepare AI-authored answers during a monitored no-AI stage.

## Stage F: User experience and visual design

Build the shortest path from task entry to interpretable result; include a visible explanation of the chosen approach, selectable candidates only if required, error/busy/empty states, comparison metrics with units and sources, and reproducible test guidance. Keep sensitive raw data out of the reporting pane. A synthetic-only demo may use public SK CI color tokens if identity rules permit, but must never claim to be an official internal SK design system; see `docs/REPORT_WORKBENCH.md`.

## Integration gate

Use the official README and actual required deliverables to verify the result. User-controlled accepted state is separate from generated candidates. The workbench is a preparation aid and not a substitute for actual functional testing or final submission confirmation.
