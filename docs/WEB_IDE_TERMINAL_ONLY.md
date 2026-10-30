# Browser IDE + terminal-only coding agent

This is a generic, offline-first checklist for a **restricted browser-hosted IDE**, not a screen capture or computer-control recipe. Read the platform's current rules first; they override this document. In some environments the editor and CLI share saved files, but **the agent may not see the editor window**.

## The actual bridge: saved files, not pixels

```text
Human (official browser editor UI)      CLI agent (terminal)
      |                                        |
      | save                                reads real files
      v                                        v
       [authorized shared worktree on disk]
                  |              |
               commands       tests/logs
                  |              |
                  +---- local service -------+
                               |
                 human in built-in Browser preview
```

- The agent can read a file after it has **actually been saved** on the shared worktree. It cannot read text that exists only in an unsaved editor buffer.
- The candidate can always inspect the official app preview manually, even if the CLI agent has no browser control. Never claim the agent saw it.
- A server process, an HTTP 200 response and a functional UI are three different levels of evidence.
- Do not capture restricted task screens, use screenshot automation, drive GUI controls, install alternative AI, or change runtime permission settings. Do not route challenge content into external services.

## Phase A: identify project files without touching platform internals

Use the commands supported by the terminal in the **authorized project folder**:

```sh
pwd
ls -la
find . -maxdepth 2 -type f | head -80
sed -n '1,150p' README.md
# If this is a Git repository:
git status --short
```

If Python 3.10+ and this public toolkit are already present and permitted:

```sh
python3 tools/workspace_probe.py --root . inventory --depth 2 --limit 80
python3 tools/workspace_probe.py --root . fingerprint README.md
```

If cloned as a nested `ai-hackathon-prep-kit/` folder, invoke `python3 ai-hackathon-prep-kit/tools/workspace_probe.py --root . inventory --depth 2 --limit 80` from the **task root**. The script path and the root to inspect are two different concepts.

`workspace_probe.py` scans names/sizes in bounded depth and can hash one saved file. It never reads editor pixels, executes project code, modifies files or calls an outbound API. It skips hidden credentials, symlinks and heavy dependency directories. It is optional; do not install Python if the restricted environment does not provide it.

## Phase B: implement with a specific acceptance check

Use a short bounded instruction:

> Read the existing README and saved project files. State the exact worktree, required outputs, and unanswered questions. Do not change system settings or create external connections. Implement only the confirmed first feature. Run its smallest meaningful test and report the real command, exit status, expected/observed output, changed file paths, and unverified areas.

Compare a disk file before and after the write, if useful:

```sh
python3 tools/workspace_probe.py --root . fingerprint src/app.js
# without Python, if available:
sha256sum src/app.js
```

A changed hash means saved file bytes changed. **It does not prove correct functionality or detect unsaved editor text.**

## Phase C: if editor and agent disagree

| Symptom | What to check | Safe next step |
| --- | --- | --- |
| Editor shows new text, CLI sees old text | Editor saved/unsaved indicator | Save using the official UI, then re-read disk |
| CLI changed file, editor shows older version | "External change" or stale buffer warning | Compare versions before loading or overwriting |
| `git diff` shows nothing | Is it an untracked new file? | `git status --short`, `ls`, then inspect saved file |
| Browser shows older app | Dev-server running? Port? Rebuild/refresh? | Verify process and port, refresh in official Browser |
| No shared files found | Different roots, not necessarily missing permissions | Locate the *authorized* shared root; stop at platform boundaries |
| GUI state only | CLI cannot see pixels | Candidate manually tests and records pass/fail; no screenshot |

Never force overwrite a candidate's unsaved changes. Never infer file contents from a claimed screenshot if the interface does not actually expose it.

## Phase D: verify real behavior

1. Run permitted unit or integration tests; report executed cases, not proposed cases.
2. Start the app with the project's documented command. Inspect the actual port and keep the server terminal open.
3. If the platform's internal Browser requires `0.0.0.0`, use the documented bind option for the project runtime; this is a local preview bind, not permission to host externally.
4. Check a loopback HTTP endpoint if useful: `python3 tools/smoke_http.py --port 8000 --path /` (replace with actual port).
5. Have the candidate test the built-in Browser *manually*: button/input, normal case, invalid case, visible error feedback.
6. Record human observation as `MANUAL_PASS`, `MANUAL_FAIL`, or `NOT_RUN`. Do not fabricate screenshots, automated GUI checks or test status.

## Skill routing (do not load everything)

- Unknown project, no agent view: `.agents/skills/web-ide-terminal-bridge/SKILL.md`
- Unsaved buffer, conflict or stale file: `.agents/skills/saved-file-reconciliation/SKILL.md`
- Local server / Browser preview: `.agents/skills/manual-preview-validation/SKILL.md`
- Build and test: `.agents/skills/codex-build-loop/SKILL.md`
- Error reproduction: `.agents/skills/debugging-verification/SKILL.md`
- Requirements not yet clear: `.agents/skills/requirements-discovery/SKILL.md`

A Git clone does not necessarily activate local skills automatically. Use the platform's permitted skill discovery/load method. **Never edit hidden settings or install a new agent version to force support.**

## Offline MCP is optional

The local stdio MCP adapter offers six read-only methods: CSV audit, JSON validation, JSON structural comparison, classification metrics, workspace inventory, and saved-file fingerprint. It does not capture UI or run commands. It must be explicitly permitted and loaded by the official host; otherwise use the shell/standalone Python tools. See `docs/MCP_SETUP.md`.

## Do not confuse with an allowed screenshot

A platform may capture a candidate's screen for supervision while separately prohibiting the candidate from taking screenshots of prompts or results. **That does not give the agent or the candidate permission to retrieve those recordings.** Use the official preview UI and disk evidence, not captures or screenshot detection workarounds.

