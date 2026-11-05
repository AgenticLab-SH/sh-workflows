# Changelog

## 0.9.0 - 2026-11-05 (main; existing release ZIP unchanged)

- Integrated unpublished local method/evidence/learner-explanation workflows, synthetic trace, UTF-8 CLI fix, optional locked property checks and original dependency licenses with the latest web-authored Workroom.
- Added a preparation index, refreshed Notion coverage and linked all 14 existing research references without publishing private originals or claiming new paper validation.
- Added an end-to-end development guide: stakeholder/data discovery, goals/spec/environment/plan, bounded delegation, session handoffs, milestone conversations, actual verification/root-cause repair, concrete code/architecture review and final operational handoff.
- Workroom init creates missing DEVELOPMENT_PLAN, MILESTONE_REVIEW, QUALITY_REVIEW and HANDOFF records; existing documents and task source remain preserved. Connected startup and existing build/orchestration/handoff Skills.
- Current integration checks and explicit NOT_RUN are recorded in docs/INTEGRATION_20261105.md. Earlier local-only entries below describe their original dates, not today's publication state.

## 0.8.0 - 2026-11-05 (main; release ZIP unchanged)

- High-contrast Workroom 3000 UI: black text on light sidebar/panels, labeled L0–L4 levels, agent/status/level filters and visual evidence hierarchy. No change to independent service port 3001.
- Workroom events v2 add `level`, `priority`, `basis`, `role`, `source_ref`, `decision_by`; old v1 events remain readable.
- Confirmed design decisions require named human/stakeholder/official owner; PASS requires observed basis and test evidence, not an agent completion claim.
- Published public reporting and color contract plus updated starter and skills. Isolated synthetic Workroom test suite: 17 passed. GitHub content verification is not equivalent to Cofa Browser usability proof.
- All workroom files remain within the explicit project root; no monitored exam data, Push, screenshot or external transport.


## 0.7.0 - 2026-11-05 (main only; no old release overwritten)

- Default workflow now confirms the actual VS Code project root and records a metadata-only pre-Clone baseline before importing the reference kit; no home-wide search.
- Introduced one protected `.cofa-workbench` directory for reference kit, requirement/data profiles, stakeholder Q&A, design decisions, ownership, validation and independent agent reports.
- Added `safe-workroom-bootstrap` Skill (42 -> 43), `tools/workroom.py`, and prebuilt responsive report UI in `tools/workroom_ui.html`. Default read-only report port **3000**; actual project service port **3001** remains independently owned by the task.
- Existing v1 explainability viewer remains available as a compatibility tool, but is no longer the default. No project-root override is created automatically.
- Synthetic isolated tests: **13/13 PASS** (including preventing unverified PASS claims); UI embedded JS syntax: PASS. Synthetic HTTP/API responses: PASS; real Cofa/Windows runtime: NOT_RUN. Browser screenshot rendering timed out, so actual UI visual QA: NOT_RUN.
- GitHub contains generic code and examples only; no live assessment data, participant answers, credential material, or externally uploaded execution logs.


## 0.6.0 - 2026-11-05 (main only, no release ZIP update)

- Added explainable-workbench Skill (41 -> 42) and a local-only append-only two-tab report/results viewer, plus a human decision/architecture verification guide and a small evidence-card template.
- One independent local event file per agent, local-only HTTP read endpoints, optional loopback app preview, and fixed public SK CI accent used only as an opt-in visual theme (not an official internal UI library).
- New synthetic-only unit tests: 11 passed with Python 3.13.5; all existing repository tests and browser rendering in the owner's/Cofa environment remain NOT_RUN. Separate container Chromium screenshot QA was BLOCKED_BY_ADMINISTRATOR and was not bypassed.
- Real assessment questions/data, staff identities, private CSV records, authentication, screenshots, and exam solutions were not published. Local note files are explicitly not guaranteed to be excluded from submission.


## Unreleased - 2026-11-03 (optional OSS, local installation)

- Adopted Hypothesis 6.170.14 + sortedcontainers 2.4.0 for bounded synthetic generation and counterexample shrinking, without replacing the existing algorithms or stdlib-only mode.
- Added `examples/method_trace.py --property-checks`, exact Windows CPython 3.13 x64 wheel hashes, an offline-by-default local-venv installer, original license notices and an adoption/install/rollback ledger in `docs/OSS_ADOPTION.md`.
- Installed and read back both dependencies in two independent local venvs; 60 generated cases checked three properties and a shrunk greedy counterexample. Targeted integration 4, existing trace 3 and kit consistency 6 tests passed. Missing/wrong dependencies, observability, external-input options, socket/subprocess attempts and a corrupt wheel were rejected.
- Full suite, other platforms, real assessment use and learner Q&A are NOT_RUN for this unit. No new push/release, global install or prior package regeneration.
## Unreleased - 2026-11-02 (local preparation only)

- Preserved the 41 Skills and existing research/defense additions; connected information gaps, single-fact questions, authored assumptions, formalization, baseline/method selection, implementation evidence and learner explanation.
- Added a small synthetic budget-selection trace using existing `opt_kit.py` functions, a 10-row assumed question ledger, independent subset checks and a solo-practice starting prompt. No real stakeholder/user Q&A was performed.
- Read official MIT OCW knapsack notes and Google OR-Tools documentation; recorded scope, sections, dates, adoption decisions and licenses in `docs/RESEARCH_METHODS.md`. No new paper, copied third-party code or dependency was adopted.
- Fixed the existing question-candidate CLI's Windows redirected-output encoding to UTF-8, with a CP949 regression case.
- Local Python 3.13.15 full suite: 172 tests OK after the encoding fix. Skill-creator validation could not run its checks because PyYAML is absent; existing kit structure/link checks passed. Detailed evidence and NOT_RUN are in `docs/METHOD_TRACE_VALIDATION.md`.
- Local packages include Skill references and LICENSE; local source/archive receipts are separate from GitHub publication. No new push/release, installation, actual assessment use or learner-understanding claim.
## 0.5.0 - 2026-11-01 (main, local commits; release ZIP not regenerated)

- Added general work patterns for time-boxed AI hackathon tasks. No task scenario, data, wording, scoring text or candidate information is included.
- Override instructions as a first-class path: `docs/OVERRIDE_INSTRUCTIONS.md` (decision order: keep an existing override, path A without an original, path A2 that pastes the provided AGENTS.md verbatim at the top, first-message block B, fallback C), `templates/AGENTS.override.template.md`, `templates/PROMPT_OVERRIDE_BLOCK.md`, and read-only `tools/instruction_chain.py` (load order, shadowing, byte limit, `original_embedded`, empty-file warning).
- New Skills (37 → 41): `stakeholder-agent-questioning` (single-fact questions and copy-ready messages for a stakeholder that answers only concrete questions; question vs message send-unit trial; re-ask and stop rules), `role-separated-design` (role matrix, derived views, function-level permission and row-ownership checks), `optimization-modeling`, `cost-aware-execution`.
- New templates and tools: `templates/QUESTION_LEDGER.csv` and `QUESTION_MESSAGES.md` with `tools/question_ledger.py` (`lint`, `next` with rewrite-needed rows, `summary`; optional `ask_count` retry limit), `templates/ROLE_MATRIX.md`, `templates/COST_LOG.md` with `tools/context_budget.py`, and standard-library `tools/opt_kit.py` (Hungarian, capacitated assignment with `allow_unassigned`/`forbidden`, greedy + swap, `min_cost_flow`, `assignment_flow` with per-row limits, groups and `fixed` pairs, `constraint_report`, knapsack DP, FFD, interval scheduling, 2-opt, Dijkstra, annealing, Pareto front, `demo`).
- New synthetic mock D `exercises/session-allocation/` (community-centre weekly class allocation) with a facilitator card that answers only specific questions, plus fixture tests.
- New synthetic mock E `exercises/donation-packing/` (flea-market donation storage boxes: bin packing with two limits, a no-mix rule and set splits); its fixture test recomputes the facilitator numbers and checks the optimum by exhaustive search.
- New read-only `tools/question_candidates.py`: drafts question-ledger rows from data-visible decision points (blanks, sparse columns, zero/negative values, mixed units, IDs that differ by spaces/case, repeated IDs, timestamp ties, few-valued text columns that may carry combination rules, missing references).
- `opt_kit.py` packing helpers for several capacity dimensions and label conflicts: `first_fit_multi` (baseline in a given order), `bins_lower_bound`, `pack_report` (violations and split groups). They give a baseline and checks, not an optimum.
- Connected the paths in README, START_PROMPT (section 0 override check, question mode, cost rule), hackathon-task-driver, SKILLS_INDEX, EXAM_DAY_FAST_PATH, HACKATHON_RUNBOOK, DECISION_CARD, CLI_READY_PROMPTS, DELEGATION_PROMPTS, LEARNING_PATH, PRACTICE_COFA, MOCK_EXAMS and IMPORT_AND_SELECT_SKILLS. stakeholder-interview and requirements-discovery switch to the new questioning Skill when questions are unlimited.
- Local verification: `python -B -m unittest discover -s tests -v` on Windows Python 3.13 → 168 tests OK. Live Codex override loading, real stakeholder agents and Cofa runtime remain NOT_RUN.
- `question_ledger.py lint` bounds near-duplicate work to 200,000 comparison pairs in total (largest categories skipped first); 4 categories × 500 similar rows measured 7.4 s → 1.5 s locally.
- Release packaging for v0.5.0 (source ZIP, 41 individual Skill ZIPs and the bundle) prepared and checked locally; GitHub release not created.
## 0.4.2 - 2026-10-31 (main, no release ZIP regenerated)

- Added bounded offline-by-default `quick_preflight.py`: project markers, local tool presence, optional read-only fixed-public GitHub access, optional protected saved-file hash.
- Added seven isolated synthetic tests and a provenance-bounded test result; full historical suite and Cofa runtime remain NOT_RUN.
- Added guidance against copying private Codex home and against uploading monitored exam diagnostics or outputs. No Git Push or screenshot functionality included.

## 0.4.1 - 2026-10-31 (main branch; release ZIP not yet regenerated)

- Added reference-submission-review Skill to detect accidental inclusion of cloned public reference files in an assignment submission.
- Added an exam-day one-page operating card and a reference-versus-submission checklist.
- Corrected tool documentation for the existing six read-only MCP methods and workspace inspector.
- Static content review and standalone Skill packaging performed; full repository tests and live Cofa integration remain NOT_RUN.

## 0.4.0 - 2026-10-31

- Read the current returned Notion study corpus: two hubs, 18 lessons, research notes and the related planning item.
- Added a core study handbook, stakeholder question ladder, delegation prompts, architecture/evidence/submission guides and research interpretation.
- Added three synthetic practice dossiers for visitor review, support triage and summary repair; the repair script is intentionally incorrect training code.
- Added requirement-to-evidence, incident and submission-state worksheets; linked existing Skills without increasing the 36-Skill count.
- Distinguished historical GitHub/test claims, Git modification markers and actual saved-file evidence.
- Verification NOT_RUN. No real assessment data, original attachment copies, automatic CI, live Cofa use or Notion mutation.

## 0.3.0 - 2026-10-31

- Renamed the repository and MCP identity to ai-hackathon-prep-kit.
- Added a hackathon task-driver Skill; retained the original 35 Skill bodies.
- Added Cofa rule provenance, 15-minute trial, 180-minute task workflow, terminal and import guides.
- Added an 18-topic learning path, six synthetic drills, a mock brief and working templates.
- Added source reconciliation and independent Skill download packages.
- Removed stale validated/current-test claims; verification NOT_RUN. No automatic CI or live Cofa use.

## 0.2.0 - recovered historical preparation

- Added terminal-only workspace, saved-file reconciliation and manual preview Skills to the original 32.
- Historical test claims were not reproduced by this recovered copy.

## 0.1.0 - 2026-10-27

- Created a public-ready offline-first multi-domain skills collection (32 independent SKILL.md packages).
- Added Korean and English writing, speaking, translation, prompt design, requirements analysis, full engineering/QA handoff workflows.
- Added local CSV/JSON analysis tools, binary classification metrics, loopback-only HTTP smoke check and local read-only MCP over stdio.
- Added bounded file access, synthetic fixtures, safe-use and publication guidance, scenario playbooks and unit tests.
- No external services, secrets, hosted endpoints, public repository creation, or exam-platform integrations are bundled.


## 2026-10-31 final preparation
- Public repository address renamed to sh-workflows; historical names and release artifacts retained.
- Reused 37 skills; improved adaptive stakeholder questions, workflow choice/ROI and task-driver reminders.
- Added decision card, six synthetic business workflows, source index and concrete trial commands.
- Standardized preflight statuses, redacted unavailable-root errors and blocked hidden/auth fingerprint targets.
- Local synthetic suite: 35 passed. Cofa and real assessment use: NOT_RUN.
