# AGENTS.md - Public engineering kit contributor guidance

- Follow README and docs/SAFE_USE.md; do not add anything that transmits data or bypasses platform restrictions.
- Work with synthetic fixtures only; do not ingest real exam/workplace/confidential data.
- Use a single code-writing owner; other reviews may be read-only.
- Prefer Python stdlib and deterministic, bounded scripts; verify concrete behavior with tests.
- For browser IDEs, observe only saved project files through the authorized terminal. The agent does not see unsaved buffers or the screen; when needed, the candidate checks the built-in Browser manually.
- Never take screenshots, retrieve supervision recordings, automate a GUI, or use hidden platform settings as a visibility workaround.
- See docs/WEB_IDE_TERMINAL_ONLY.md and docs/RESTRICTED_ENV_BOUNDARIES.md before restricted-environment work.
- Never claim a CLI feature, Skill or MCP is active in a separate restricted environment until actually verified and permitted.
- Keep docs short; make skills progressively loadable by descriptive frontmatter rather than loading every skill at once.
