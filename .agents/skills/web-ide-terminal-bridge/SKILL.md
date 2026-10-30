---
name: web-ide-terminal-bridge
description: Inspect a browser-hosted development workspace from an authorized terminal when a coding agent cannot see the editor UI. Use for web IDEs, terminal-only agents, unclear project roots, file discovery, and read-only environment verification before making changes.
---

# Web IDE terminal bridge

## Operating principle

Treat the **saved files on the shared worktree** as the source of truth for the CLI agent. A browser-hosted editor, a terminal, and an agent may share a filesystem, but do not assume this until verified in the provided environment. The agent does **not** gain screen vision from this skill, and it cannot inspect unsaved editor buffers.

## Minimal observation workflow

1. Confirm the authorized project root and read its README before acting. Avoid scanning unrelated user directories, hidden configuration, secrets or platform control files.
2. In the project's supported shell, use bounded commands to map **saved** files:

   ```sh
   pwd
   ls -la
   find . -maxdepth 2 -type f | head -80
   git status --short
   sed -n '1,140p' README.md
   ```

   Run only commands available in the provided shell. `git status` is useful if a repository exists; untracked files may not appear in `git diff`.
3. When Python 3.10+ is available and toolkit files are present, prefer the offline inspection helper:

   ```sh
   python3 tools/workspace_probe.py --root . inventory --depth 2 --limit 80
   python3 tools/workspace_probe.py --root . fingerprint README.md
   ```

   If the public kit is a **nested** folder under a separate task workspace, run `python3 ai-hackathon-prep-kit/tools/workspace_probe.py --root . inventory --depth 2 --limit 80` from the **task root**. Do not accidentally inspect the toolkit folder instead of the task files.

   Its default output has only file names, sizes and hashes; there is **no screenshot, desktop control, network upload, or file modification**.
4. Identify task entry points from actual README/package metadata. Ask the agent for a concise mapping: requirement -> file/function -> proposed test. Stop if the workspace is not shared or permissions are unclear; ask the candidate to check the official UI rather than inventing access.
5. After a code change, repeat bounded file listing and the actual tests. Have the candidate manually verify GUI-only behavior in the environment's permitted preview.

## Failure modes

- **Saved editor content not reflected in terminal:** verify the editor shows "saved". Follow `saved-file-reconciliation`; never silently overwrite unsaved changes.
- **Terminal and editor point to different folders:** use actual `pwd` and file tree; find the authorized shared project root. Do not use host/admin paths or hidden mounts to bypass the boundary.
- **No Python:** use shell built-ins and `sha256sum` if installed. Do not install a runtime solely for this helper.
- **Visible UI not observable by agent:** ask for a human pass/fail check, not screenshots or automated mouse/keyboard control where prohibited.

## Required output

Report confirmed project root, saved files inspected, evidence, modifications (if authorized), observed tests, unverified visual behavior, and next safe action. Label any assumption explicitly.

## Boundary

The task or operator's rules take precedence over this generic skill. In monitored environments, never capture a screen, use browser/desktop automation, send prompts/files out, modify approval or runtime settings, install extra AI, or update the provided agent to circumvent restrictions. Prefer the official built-in preview and human observation.

