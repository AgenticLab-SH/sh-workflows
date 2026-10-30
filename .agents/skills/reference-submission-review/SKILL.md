---
name: reference-submission-review
description: Review the boundary between a public reference toolkit and real task deliverables in a shared web IDE or terminal-only coding environment. Use when a repository is cloned under the task folder, submitted files are uncertain, or a candidate must verify the final submission set.
---

# Reference vs. submission review

## Goal

Prevent an optional public toolkit or synthetic practice files from being mistaken for the actual assignment, silently modifying the task, or entering a submission unintentionally. Use this workflow only while agent assistance is allowed.

## Inspect the authorized task root

1. Read the real task's current README and explicit submission instructions. The task's instructions and current model/host policy override this skill.
2. Confirm the actual task root using the provided terminal (`pwd`, `ls -la`). Treat any cloned `.hackathon-kit` (or other toolkit name) as **reference material**, not the task root.
3. Compare required files and output paths with saved, on-disk files. Use bounded listing only if authorized, e.g. `find . -maxdepth 2 -type f | head -80`. Do not inspect hidden platform files, unrelated folders, secrets, or other users' data.
4. List the source category for each relevant path: `TASK_INPUT`, `TASK_OUTPUT`, `REFERENCE_KIT`, `GENERATED_TEMP`, or `UNDECIDED`. Avoid exposing private file content in the summary.
5. Verify whether the official submission preview includes only intended deliverables. A hidden folder name or a Git ignore entry does **not** prove the platform will exclude that folder. The participant must inspect the official preview manually; do not claim to see the screen.
6. If a reference kit appears inside a submission candidate, first ask the participant to inspect the platform's supported selection/exclusion behavior. Preserve all existing files and content. Do not delete, relocate, rename or overwrite the kit or assignment files without explicit authorization and an established safe method.
7. Before submitting, match each required output to a saved path and concrete evidence (test/command result or participant-observed official preview). Mark unclear membership `UNCONFIRMED`; do not pretend the toolkit was excluded.

## Fast result format

- Task root (observed):
- Required outputs (source instructions):
- Saved output paths (observed):
- Reference and synthetic files present:
- Preview membership (participant observed / NOT_RUN):
- Risks or unknowns:
- Next safe action:

## Boundaries

- Use only the provided terminal, authorized saved worktree and official user-operated preview.
- Never capture screens, scrape the page, automate mouse/keyboard, install extra agents, change monitored settings or update the provided coding agent.
- No outbound transmission of challenge data, candidate links, credentials or output files. `git push` from a restricted assessment is prohibited unless an explicit official rule says otherwise.
- If a monitored assessment has reached its no-AI phase, stop entirely: no drafting, verification or assistance.
