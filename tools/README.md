# Local deterministic tools

All commands are offline-first Python 3 standard library with no external model calls.

| Tool | Input | Output | Safety |
| --- | --- | --- | --- |
| `audit_csv.py` | Local CSV, required/unique fields | Counts, missing values, duplicates, malformed rows | No raw row content |
| `validate_json.py` | Local JSON and required top-level keys | Key metadata, validity | No values |
| `compare_json.py` | Two local JSON files | Changed paths and counts | Values suppressed |
| `metrics.py` | Synthetic classification labels CSV | TP/FP/FN/TN, precision, recall, F1 | No record content |
| `smoke_http.py` | Local running server port/path | HTTP status | Forced 127.0.0.1, no external network, no GUI |
| `workspace_probe.py` | Authorized saved worktree | Bounded file inventory and metadata/hash | No file content, no GUI or network |
| `mcp_stdio_server.py` | MCP JSON-RPC stdio | Six read-only data tools | Allowed root, no network, no writes |

These are **generic building blocks**, not finished business logic or a ready-made answer.
Some operations return nonzero exit when quality checks fail, by design. Treat a failed status as evidence to inspect, not a reason to bypass restrictions.

