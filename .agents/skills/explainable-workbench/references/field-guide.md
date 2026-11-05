# Report event and human review field guide

Events are append-only and created with unique IDs. No agent edits another agent's event file. The local viewer merges events by timestamp and supports filtering by agent/status.

| Field | Meaning | Example type |
| --- | --- | --- |
| `agent` | Current work owner | `coordinator`, `frontend`, `reviewer` |
| `kind` | Question, decision, implementation, test, result, risk, handoff | `decision` |
| `status` | `proposed`, `confirmed`, `implemented`, `verified`, `blocked`, `not_run` | `confirmed` |
| `title` | Short title without raw personal data | `Boundary handling selected` |
| `summary` | Work scope and observable change | `Validated required keys before planning` |
| `why` | Business or technical rationale | `Avoid processing undefined inputs` |
| `alternatives` | One feasible rejected option and trade-off | `Silently filling blanks risks wrong outcomes` |
| `evidence` | Specific command/test outcome, or `NOT_RUN` | `Synthetic test T2 PASS` |
| `files` | Relevant module/function names | `validators.py:validate` |
| `risks` | Accepted limits and unconfirmed rules | `Actual UI not yet checked` |
| `next_action` | User decision or next bounded work | `Confirm missing-value policy` |

## Questions and answers

Question entries are **drafts** unless the participant manually sends them in the authorized stakeholder UI. Do not write speculative answers as confirmed. After an answer, record the changed requirement, the code/test it influences, and the follow-up question if needed. Use the existing `stakeholder-agent-questioning` Skill and `QUESTION_LEDGER.csv` pattern rather than building a parallel question database.

## Data limits

No source CSV rows, exam questions, individual names, IDs, passwords, URLs containing tokens, or secrets belong in these notes. Sanitization rules catch some obvious credentials but cannot guarantee that all sensitive content is excluded. Keep report content high-level. Workbench server is local only by default. `0.0.0.0` binding is opt-in and only for explicitly authorized trusted IDEs.

## Proof hierarchy

`proposed`: idea only; `confirmed`: participant or authorized source agreed; `implemented`: file change exists; `verified`: a relevant check actually ran and passed; `blocked`: permission/tool restriction; `not_run`: test not attempted. Do not convert `implemented` into `verified` by reading an agent summary.

The output tab is a view of recorded test/result events. It is not itself a complete application smoke test. A local iframe preview may fail because of port forwarding, CSP or frame restrictions; open the application through the provided Browser if required.
