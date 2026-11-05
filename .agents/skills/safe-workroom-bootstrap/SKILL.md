---
name: safe-workroom-bootstrap
description: Safely establish a browser IDE project workspace before importing a public reference repository. Use when a terminal-based coding agent must locate the exact VS Code explorer task root, preserve an initial file inventory before Clone, isolate agent notes and stakeholder answers in one folder, run a read-only 3000 report UI alongside a separate 3001 deliverable, and avoid edits outside the confirmed task scope.
---

# Scoped workroom setup for browser IDEs

## 1. Confirm scope before touching a file

Ask the participant to compare the official IDE Explorer folder with `pwd -P` and `ls -la` in the **provided** project terminal. Do not infer a task directory from the user's home, scan ancestors or siblings, or create a replacement project root. Honor a system-defined working directory or higher-priority official instruction. Refuse `/`, the home root, an unrelated folder, and symlinked control folders.

**Before importing the public kit**, create an initial metadata-only record inside the confirmed task root using the exact guarded instructions in [SAFE_WORKROOM_START](https://github.com/AgenticLab-SH/sh-workflows/blob/main/docs/SAFE_WORKROOM_START.md), section 1. The local control folder is `.cofa-workbench/`. Do not claim the record is a full data backup.

## 2. Keep all assistant-facing materials in one folder

Only after the initial record exists and public Clone is allowed, use:

```sh
git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .cofa-workbench/kit
python3 .cofa-workbench/kit/tools/workroom.py --root . init
```

The tool refuses a missing baseline or mismatched recorded root. Its only allowed writes are `.cofa-workbench/docs/` templates and `.cofa-workbench/events/` append-only event files. Existing documents are never overwritten.

Original README/data/code remain in place. **Actual task deliverables** must be implemented only in the locations explicitly required by the task, with an assigned file owner. The public kit itself is reference-only. Do not assume a hidden control folder will be excluded from official submission; use the official submission preview.

## 3. Analyze and ask before architecture

Inside the confirmed root, separate the official README, data facts, assumptions, and conflicts. Record the local analysis in `docs/REQUIREMENTS_MAP.md` and `docs/DATA_PROFILE.md` using schema/count metadata rather than repeating raw personal rows.

Use existing `stakeholder-agent-questioning` and `optimization-modeling` Skills for detailed questioning and algorithm comparison. Prepare specific copy-ready stakeholder questions in `docs/HR_QUESTIONS.md`. The participant sends them in the official channel and pastes allowed responses into **local** `docs/HR_ANSWERS.md`. Re-read the answer and update the affected rule, algorithm choice, module owner and executable test before implementation. Do not silently decide business policies.

## 4. Coordinate agents and explain results

Use one coordinator and one writer per source file; independent agents can report separately. No worker changes another worker's files or all of Git history. Keep `docs/AGENT_ASSIGNMENTS.md`, `docs/DECISIONS.md`, `docs/MODULE_MAP.md`, and `docs/VERIFICATION.md` up to date.

After meaningful milestones, record one event containing **what, why, rejected alternative, changed file/function, observed verification, limitation, and next human decision**. Each event creates an independent JSON file under `.cofa-workbench/events/`, not one contested log.

Example (only if local documentation is permitted):

```sh
python3 .cofa-workbench/kit/tools/workroom.py --root . note --agent coordinator --kind decision --state confirmed --title 'Feasible baseline first' --reason 'Auditable before harder optimization' --alternative 'Unbounded complex search' --evidence 'Decision only; runtime NOT_RUN'
```

Never call a proposed or unexecuted test passed. Distinguish the participant's manual browser observation from CLI evidence.

## 5. Keep report and product servers separate

- `3000`: optional **read-only report dashboard** (`python3 .cofa-workbench/kit/tools/workroom.py --root . serve --port 3000`). No task API, file editing, test runner or remote uploads.
- `3001`: actual **task deliverable**, started independently with the framework/command required by that task, never replaced by a generic sample service.

The dashboard provides *Progress/decisions*, *Verification/results*, and *Initial state* tabs. The app link targets localhost:3001, but the official browser may require opening port 3001 explicitly. Default server binding is loopback; all-interface binding is a separate opt-in for a trusted, authorized IDE only.

## 6. Stop and explain the boundary

Do not crawl the user's home, transplant Codex global config, install hidden plugins, circumvent host policies, push assessment results, capture monitored screens, or send confidential task information outside the provided IDE. In any monitored no-AI response phase, stop all assistance.

Before handoff, use the existing `short-answer-defense` Skill **during permitted preparation only** to confirm the human can explain approach/alternatives, module flow/state ownership, implemented/assumed/excluded, normal/errors, measured evidence, and AI proposals accepted/revised/rejected. These are generic study themes, not answers to live examination questions.

## Reporting schema v3 and UI readability

After confirming the root and completing the pre-Clone baseline, read [the reporting standard](../../../docs/WORKROOM_REPORTING_STANDARD.md) only if multiple agents, user decisions, or test evidence need tracking. Keep all notes inside `.cofa-workbench/` and preserve source-file ownership. The port 3000 UI shows near-black text on white surfaces; L0–L4 is an evidence ladder, while P0–P3 is separate work priority. Colors are borders/pale fills, never the only signal. Record the human decision owner for confirmed decisions and a real observation for PASS. Example:

```sh
python3 .cofa-workbench/kit/tools/workroom.py --root . note --agent analyst --role requirements --kind question --state proposed --priority P0 --basis official --source-ref R-001 --title 'Unconfirmed input rule'
```

The coordinator assigns one writer per source file. Do not copy task files into the public kit or Git Push from a restricted examination. Old v1 events remain readable; new events use v2 schema metadata.
