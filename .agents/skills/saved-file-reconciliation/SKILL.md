---
name: saved-file-reconciliation
description: Diagnose disagreement between a browser editor, terminal, and coding agent after files are edited or saved. Use when a file does not appear, an external-change warning appears, an unsaved buffer is suspected, or an agent's edit seems missing.
---

# Saved file reconciliation

## First establish what each surface knows

- **Browser editor:** can display unsaved text that is *not* yet on the shared disk.
- **Terminal and CLI agent:** ordinarily read files saved on disk in the current worktree, not the editor's in-memory buffer.
- **Agent success message:** is not proof that the disk changed or the editor reloaded.
- **Preview:** can show a running app with stale assets even after a file changes; a restart/refresh may be necessary.

## Safe conflict procedure

1. Ask the candidate to confirm the active filename and the editor's saved/unsaved state using the **official editor UI**. Do not request a screenshot of restricted content.
2. Inspect the authorized worktree path from the terminal (`pwd`, `ls`, `git status --short`); confirm the same relative filename exists. If needed, compare the last saved version by size/hash:

   ```sh
   python3 tools/workspace_probe.py --root . fingerprint src/app.js
   # Or, if installed: sha256sum src/app.js
   ```

   Substitute the **actual** file path. Hashes cannot reveal whether an unsaved buffer differs from disk.
3. If the editor offers an external-change conflict, distinguish **load external disk change** from **overwrite disk with editor buffer**. Review both versions before choosing; if the two differ and both are needed, reconcile them manually using allowed editor controls.
4. Save in the official UI (`Ctrl+S` if supported), then ask the terminal to **re-read the saved file**. Never assume the save succeeded without the editor's saved indicator or an observed file update.
5. Run the smallest affected test; refresh the official preview manually. Report any unreconciled buffer or missing file as unresolved.

## Decision rules

- Editor saved, terminal sees file: continue with bounded edits and tests.
- Editor unsaved, terminal sees old version: save via the editor; do not make the agent hallucinate unseen content.
- Agent changed disk and editor shows stale buffer: compare before reloading/overwriting.
- Different project roots: locate the authorized shared folder; do not escalate into protected platform directories.
- No shared file access: state the limitation and rely on user-mediated, allowed edits; do **not** invent a screenshot pipeline or hidden access path.

## Required output

State the exact confirmed file path, saved-state evidence, which version was preserved, tests rerun, and remaining manual checks. Do not echo private file content into any external service.

