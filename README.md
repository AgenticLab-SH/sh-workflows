# AI Workflow Open Kit

A **general-purpose, offline-first** collection of AI-agent skills and deterministic engineering tools, focused on problem discovery, Korean/English writing and speaking, coding, data, validation, and clear handoffs.

**Independent open-source toolkit.** Not endorsed by SK hynix, Krafton, Cofa, OpenAI, or any assessment operator. These are **not exam solutions** or hidden platform access methods.

## Start here / 시작하기

1. Read [`docs/SAFE_USE.md`](docs/SAFE_USE.md) first. The rules of any assessment or workplace **always override** this repository.
2. Pick **one or two** of the **35** independent skills from `.agents/skills/<name>/SKILL.md` relevant to the task. Do not load every skill into the prompt.
3. Read the project's actual instructions and required outputs; identify facts, assumptions, questions, acceptance tests.
4. Use deterministic `tools/*.py` if useful. Everything runs with **Python 3.10+ standard library only**. If Python is not available, use the provided terminal and documented shell fallback; never install new runtimes solely for this kit.
5. Verify real results. A claimed test is not a passed test until executed.

### Quick examples (synthetic data only)

```bash
python tools/audit_csv.py examples/applications.csv --required id,date,people --unique id
python tools/validate_json.py examples/config.json --required version,name
python tools/compare_json.py examples/before.json examples/after.json
python tools/metrics.py examples/classification.csv --actual actual --pred predicted --positive yes
python tools/smoke_http.py --port 8000 --path /  # only when you intentionally start a local server
python tools/workspace_probe.py --root . inventory --depth 2 --limit 80
python tools/workspace_probe.py --root . fingerprint README.md
python -m unittest discover -s tests -v
```

### When the agent cannot see a browser IDE editor

Treat **saved project files** as the CLI agent's observable state, not screenshots. First read [`docs/WEB_IDE_TERMINAL_ONLY.md`](docs/WEB_IDE_TERMINAL_ONLY.md) and [`docs/CLI_READY_PROMPTS.md`](docs/CLI_READY_PROMPTS.md). Three focused skills cover the common failure modes:

- `web-ide-terminal-bridge`: read saved project files and find entry points through an authorized terminal.
- `saved-file-reconciliation`: detect unsaved browser buffers and external-change conflicts; preserve both versions.
- `manual-preview-validation`: use local tests/port checks and **candidate-operated** built-in Browser, not screenshot/GUI automation.

A coding agent **cannot see unsaved text, a hidden browser DOM or a restricted screen merely by loading a Skill**. Candidate screenshot shortcuts, recording retrieval, computer use, browser automation and external transmission are not part of this kit. The candidate checks preview UI manually where permitted.

### Optional, local-only MCP server

The stdio MCP server exposes bounded, **read-only** tools for CSV profile, JSON validation, JSON comparison, classification metrics, saved workspace inventory and file fingerprinting. It has **no remote transport, no HTTP outbound, no browser automation, no file writes**. It reads only files within `MCP_ALLOWED_ROOT` (defaults to current directory). It does not preload any skills.

```bash
MCP_ALLOWED_ROOT=. python tools/mcp_stdio_server.py
```

See [`docs/MCP_SETUP.md`](docs/MCP_SETUP.md) for a *generic example only*. **Connecting MCP in a monitored or restricted environment requires the operator's explicit permission; do not use configuration changes to bypass restrictions.**

## Skill index

| Area | Skills |
| --- | --- |
| Prompt & scope | `prompt-engineering`, `requirements-discovery`, `stakeholder-interview`, `research-evidence`, `work-breakdown`, `project-time-budget`, `decision-analysis`, `goal-driven-iteration`, `agent-orchestration` |
| Korean/English writing & speaking | `korean-writing`, `english-writing`, `korean-speaking`, `english-speaking`, `bilingual-localization`, `business-correspondence` |
| Software development | `codex-build-loop`, `frontend-mvp`, `backend-api`, `workflow-automation`, `debugging-verification`, `test-design`, `accessibility-ux-review`, `system-design-explanation`, `web-ide-terminal-bridge`, `saved-file-reconciliation`, `manual-preview-validation` |
| Data, rules & safety | `data-profiling`, `data-analysis`, `document-rule-reconciliation`, `security-privacy-review`, `documentation-handoff`, `short-answer-defense`, `structured-extraction`, `arithmetic-sanity-check`, `chart-and-report-design` |

**All skill names use standard `SKILL.md` with description-based triggers and `agents/openai.yaml` UI metadata.** Multi-skill folder is a Codex-compatible source layout; do not upload the entire source ZIP as a single ChatGPT skill. A separately packaged `skill.zip` contains one validated skill.

## Reuse without hidden behavior

- Reuse **methods**, not ready-made answers to an unseen challenge.
- No sample is claimed to be a real hackathon task.
- No secrets, private prompts, credentials, actual candidate data or workplace datasets are included.
- No external model/API keys, proprietary tools, hosting accounts, telemetry, trackers or GUI automation.
- No automatic feature unlocking, file exfiltration, screenshot capture, browser/desktop driving, or attempts to bypass restricted systems.
- An offline tool's presence does **not** prove the target environment permits importing or executing it.

## Status

- Source skills and scripts: 35 validated skills; offline tests included.
- Public GitHub repository: **not created by these source files**; only a verified remote commit demonstrates publication.
- An examination system's Codex version, token limits, skill discovery, filesystem access, and MCP support: **unknown until legitimately verified**.

MIT License; see [LICENSE](LICENSE). Contributions must use synthetic fixtures and preserve test coverage.

## This recovered copy

Read RECOVERY.md first. Verification: NOT_RUN. Earlier version/test claims describe historical preparation only. Remote publication is not established by these files.
