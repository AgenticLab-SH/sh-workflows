# Local deterministic tools

All commands are offline-first Python 3 standard library with no external model calls.

| Tool | Input | Output | Safety |
| --- | --- | --- | --- |
| `audit_csv.py` | Local CSV, required/unique fields | Counts, missing values, duplicates, malformed rows | No raw row content |
| `validate_json.py` | Local JSON and required top-level keys | Key metadata, validity | No values |
| `compare_json.py` | Two local JSON files | Changed paths and counts | Values suppressed |
| `metrics.py` | Synthetic classification labels CSV | TP/FP/FN/TN, precision, recall, F1 | No record content |
| `smoke_http.py` | Local running server port/path | HTTP status | Forced 127.0.0.1, no external network, no GUI |
| `report_workbench.py` | Explicit local decision/test notes, optional local server | Append-only individual events and a read-only Reports/Results dashboard | No external I/O, no screenshots, no remote push; project-local files must be checked against submission rules |
| `workspace_probe.py` | Authorized saved worktree | Bounded file inventory and metadata/hash | No file content, no GUI or network |
| `instruction_chain.py` | Project root and working folder | Which AGENTS.override.md / AGENTS.md files Codex would load, shadowing, byte limit, empty files; `original_embedded` = override starts with the whole same-folder AGENTS.md (after line-ending/line-end space normalization; only blank lines, the template guide line and HTML comments may precede it; null if not compared or the original is empty) | Metadata only, global Codex home not read |
| `question_candidates.py` | Local CSV files, optional `--key file:col` and `--ref src:cols=dst:col` | Draft question-ledger rows for data-visible decision points: blanks, sparse optional columns, zero/negative numbers, mixed units, IDs differing only by spaces/case, repeated IDs, timestamp ties, few-valued text columns (combination rules), missing references | Read-only, stdout only; `--examples 0` omits sample values |
| `question_ledger.py` | Question ledger CSV (`templates/QUESTION_LEDGER.csv`, optional `ask_count` column) | `lint` question quality and `retry_limit` (partial/unclear rows asked 3+ times), `next` copy-ready messages with `needs_rewrite` rows (partial/unclear: rewrite first, no resend of the same wording) and `ask_count`, `summary` open P0/P1 | No answer text in summary, no writes |
| `opt_kit.py` | Cost matrices or Python lists (importable) | Hungarian; capacity assignment (`hungarian_with_capacity`, greedy + swap) with `allow_unassigned` (requires explicit `unassigned_cost`) and `forbidden` cells; `min_cost_flow`; `assignment_flow` (several picks per row, one per group, capacities, unassigned value, `forbidden`, `fixed` pre-assignments with a `conflicts` list); `constraint_report` (capacity, row limits, groups, repeated columns); knapsack DP, FFD, `first_fit_multi` (several capacity dimensions and label conflicts, given order) with `bins_lower_bound` and `pack_report` (capacity/conflict/missing/repeated violations, split groups), 2-opt, Dijkstra, annealing; `demo` | Generic building blocks, deterministic seeds |
| `context_budget.py` | Files/folders under a root | Bytes, lines, rough token estimate, budget warning | No file content, rough estimate only |
| `mcp_stdio_server.py` | MCP JSON-RPC stdio | Six read-only data tools | Allowed root, no network, no writes |

These are **generic building blocks**, not finished business logic or a ready-made answer.
Some operations return nonzero exit when quality checks fail, by design. Treat a failed status as evidence to inspect, not a reason to bypass restrictions.

