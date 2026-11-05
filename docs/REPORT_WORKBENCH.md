# Local explainability workbench: reports + results

> **Compatibility note (2026-11-05):** This describes the older v1 viewer (default 8765 and `.review-workbench`). The user's current default is **V2: [safe project start](SAFE_WORKROOM_START.md)**, `tools/workroom.py` on **3000**, and a separate deliverable on **3001**, all agent notes in one `.cofa-workbench` folder. Do not run both viewers or move the project root to the kit.


This is a **general-purpose, local-first development aid**. It is not a solved examination task or a recording of an assessment. Use only if the current task and host permit a local Python server and project-local writing. Do not send confidential source data, challenge statements, answers, logs or candidate links to any external service or GitHub.

## 1. What problem does it solve?

A coding agent can create many files quickly but leave the participant unable to explain what it did. With several agents, this gets worse because updates are scattered between terminals. The workbench records **one small, cumulative, inspectable rationale** per significant decision, implementation, test, risk or handoff. Agents create independent files; the browser merges them without a shared append bottleneck.

The server has two views:

- **Reports / decisions:** All events, ordered newest first, filterable by agent and status. Fields: rationale, alternatives, module path, test evidence, limitations and next action.
- **Results / verification:** Only `result` and `test` events, with the same evidence detail. Optionally display a separate **already-running local** project app in an iframe. Frame/port forwarding may fail in some IDEs, in which case use the provided Browser directly.

The viewer is read-only. It never edits the task, runs a solver, captures screenshots, calls external APIs, or pushes Git content.

## 2. Safe use in a project

Use a locally authorized project root. The public kit is a **reference**, not an assignment root. After a permitted Clone into `.hackathon-kit`, run the tool only if allowed:

```sh
python3 .hackathon-kit/tools/report_workbench.py --root . note --agent coordinator --kind decision --status confirmed --title 'Select baseline-first workflow' --why 'Simple logic is easier to validate' --alternatives 'Immediate full search' --evidence 'Decision only; actual test NOT_RUN'
python3 .hackathon-kit/tools/report_workbench.py --root . list
python3 .hackathon-kit/tools/report_workbench.py --root . serve --port 8765
```

**Default network binding is 127.0.0.1.** If a trusted and authorized browser IDE requires a container-facing listener, the operator may choose `--host 0.0.0.0`. This may expose reports to additional reachable clients; do not use with confidential content unless the current environment explicitly permits it.

To opt into a **local** existing application preview:

```sh
python3 .hackathon-kit/tools/report_workbench.py --root . serve --port 8765 --preview-url http://127.0.0.1:3000
```

If an iframe is blocked, a manually opened official Browser port is the source of UI verification, not the dashboard iframe.

The report port is arbitrary: 8765 is the default to avoid competing with an existing app at 3000. Do not terminate or replace a running app just to start the workbench.

## 3. Appended agent notes

Each agent owns its work. Call `note` after a meaningful decision, actual file change, executed check, or blocker. Example:

```sh
python3 .hackathon-kit/tools/report_workbench.py --root . note \
  --agent reviewer --kind test --status verified \
  --title 'Synthetic boundary check passed' \
  --summary 'Validated one edge case on fictional inputs' \
  --why 'The outcome differs at the configured threshold' \
  --alternatives 'Assume success without execution' \
  --evidence 'unittest test_boundary: PASS on synthetic data' \
  --files 'logic.py:check_boundary' \
  --risks 'Real UI behavior not reviewed' \
  --next-action 'User checks app through the official preview'
```

`status` is one of `proposed`, `confirmed`, `implemented`, `verified`, `blocked`, `not_run`.

`kind` is one of `question`, `decision`, `implementation`, `test`, `result`, `risk`, `handoff`.

- **Proposed** = plan, not fact. **Confirmed** = established rule or human choice. **Implemented** = files changed. **Verified** = a relevant test was actually executed. **Blocked / not_run** = not verified.
- Do not create dummy PASS notes. Test status must match real evidence.
- Do not paste CSV rows, individual names, IDs, private documents, screenshots, test questions, login URLs or secrets. The built-in pattern check is only a limited safety aid, not a full DLP scanner.
- Each `note` atomically creates its own event file at `.review-workbench/events/`; no two workers write the same file. The local project owner decides whether such files should be retained or included in a delivery. Hidden folders are not automatically excluded from submission.

## 4. Multi-agent operating contract

Assign one coordinator. Each change file has one writer, other agents deliver read-only reviews or separate files. Worker notes do not substitute for an integration test.

| Actor | Ownership | Evidence in report |
| --- | --- | --- |
| Coordinator | Scope, file ownership, decision checkpoints | User choices, alternatives, reasons, unresolved rules |
| Data reviewer | Safe schema/quality characterization | Missingness/duplicates as counts, unresolved interpretation, no row-level data |
| Algorithm designer | Baseline, candidate comparison, feasibility | Assumptions, constraints, runtime/quality observations and limits |
| Implementation writer | One non-overlapping module | Changed files, expected behavior, verification status |
| Independent verifier | Tests and failure-path analysis | Expected/observed and human-check items |
| UI owner | Role-specific views and local preview | Screens needing manual confirmation, unknowns |

Use **source -> confirmed rule -> module -> test -> output** as the explainability chain. If stakeholder answers change a rule, update the decision and the affected test before treating a related feature as finished.

## 5. Suggested decision cards (generic)

At a candidate selection point compare a baseline, a bounded heuristic and an exact approach only if plausible. Discuss objective, hard constraints, capacity, data shape, deterministic tie-break, runtime budget, explainability and the fallback. A decision is only `confirmed` when the responsible human decides; measurements must be real observations.

Before any final handoff, summarize in ordinary language: goal, modules/data flow/state owner, implemented vs assumed vs excluded, normal and error paths, evidence and test status, candidate metrics, AI proposals accepted/revised/rejected. This is a preparation mechanism, **not** an answer generator for an actual no-AI follow-up stage.

## 6. Public visual identity guardrails

Default is a neutral, accessible internal-tool layout. Optional `--theme sk-public` uses **only the publicly documented SK Group CI Red #EA002C** as the main accent; Orange #F47725 is a publicly documented complementary primary color but is not used for small white-on-orange text because of contrast concerns. Source: https://www.sk.co.kr/ko/about/brand.jsp (official SK brand colors). SK hynix's public brand-identity overview: https://www.skhynix.com/company/UI-FR-CP0401/ .

**This is not the official SK hynix internal design system**. No corporate logo/CI artwork is bundled, no permission to represent the company is implied. Use an official supplied design system and approved logo assets if the actual authorized project provides them. Prioritize legible fonts, responsive layouts, clear input labels, visible error/empty/loading states, keyboard accessibility, simple workflows and concise evidence.

## 7. Limits

- The workbench is local to the project and **does not** control the monitored platform, examiner chat, clipboard or screen capture.
- Browser display and content frame availability have not been verified in any particular managed assessment IDE.
- Local event notes may become submission candidates in some systems; the participant must check the actual submission preview.
- Full project integration tests are separate from the workbench's own synthetic unit tests. See `tests/test_report_workbench.py`.
- When a supervised assessment forbids AI during a later section, stop using all agent assistance for that section.
