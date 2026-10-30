# Restricted environment decision gate

This toolkit supports offline, local development workflows. It is not an access expansion or screen capture toolkit.

## Before using a tool

1. Is the exact tool/version provided or permitted by the operator?
2. Is the data source a saved file under the authorized worktree, or does it require restricted screen/host access?
3. Will input data, prompts, outputs, credentials or screenshots leave the authorized environment?
4. Could this action alter supervision, hidden settings, runtime approvals, or the provided agent's version?
5. Is there a simpler built-in method with lower time/verification cost?

If the answer is unclear and the action carries access or outbound-transfer risk, stop and use the official help channel. Do not try alternate hosts, shells, accounts or wrappers to achieve a blocked action.

## Allowed generic pattern (subject to operator rules)

- Read allowed README and saved files with CLI.
- Use a task-specific subset of public instructions/skills when permitted.
- Implement in the provided workspace with the provided agent.
- Run local tests and check outputs.
- Ask the candidate to inspect the official preview manually.
- Keep all sensitive task inputs and results within the authorized environment.

## Not authorized by this repository

- Screen recording retrieval, hidden browser tab access, screenshot automation, OCR of restricted screens, GUI remote driving.
- Remote or externally hosted AI/MCP that sends challenge material outside the environment.
- Personal file upload if the test forbids it; publishing or exporting challenge solutions.
- Installing a newer agent, overriding permissions or enabling blocked features.
- Prefabricated answers to unseen challenge tasks.

An operator may permit some generic features in another context; this repo **never** overrides the current operator's narrower rules.

