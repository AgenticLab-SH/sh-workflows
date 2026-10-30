# Local, read-only MCP tool adapter

`tools/mcp_stdio_server.py` implements a small subset of the MCP JSON-RPC-over-stdio transport and is designed for **local, explicit use**. It is not a hosted service, not an AI model, and does not auto-install anything. Standard library only, no logging to stdout except protocol frames.

Available tools (6): `audit_csv`, `validate_json`, `compare_json`, `classification_metrics`, `workspace_inventory`, `file_fingerprint`. Paths are constrained under `MCP_ALLOWED_ROOT`, with max file size and record limits. Only JSON summary data is returned; row-level personal information is never emitted by design. The workspace tools return file names/sizes or hashes only: no file values, editor buffer, screen, GUI or command execution. Sensitive filenames/symlinks and dependency directories are omitted. The CLI fallback is `tools/workspace_probe.py`.

A **generic** MCP host configuration example, not an instruction to modify a restricted IDE:

```json
{
  "mcpServers": {
    "ai-workflow-open-kit": {
      "command": "python3",
      "args": ["/absolute/path/to/ai-workflow-open-kit/tools/mcp_stdio_server.py"],
      "env": {"MCP_ALLOWED_ROOT": "/absolute/path/to/safe/workspace"}
    }
  }
}
```

Host schema and runtime vary; see the host's official documentation. Configure only within an explicitly permitted environment. The repository is useful **without** MCP via ordinary CLI scripts and SKILL.md guidance. **Do not change restricted MCP settings to force registration.**

Security notes: no remote endpoints, no credentials, no network, no write operations; run server as a user with access only to sanitized local files. Symlink escapes are checked on each read. File paths are always resolved inside root. The server is bounded, not a hardened shared service; do not expose it on a network.
