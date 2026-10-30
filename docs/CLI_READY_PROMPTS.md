# Concise prompts for a terminal-only coding agent

Use only **inside an authorized runtime** and only when the environment allows public instructions. If the toolkit is cloned into a subfolder, have the agent identify both the actual task root and the imported toolkit path. Reading a nested SKILL.md does not imply automatic skill discovery. Replace examples with task facts already visible to the agent. Never send restricted task material to a separate AI or remote MCP.

## A. Unknown project, no editor vision

```text
You may not be able to see my web editor UI. Use only saved files under the current authorized project root and permitted terminal commands. Inspect pwd, README, saved file paths and runtime. Identify user goal, required files, unclear constraints, and acceptance tests. Do not claim to see unsaved editor buffers or the Browser. Do not change code yet; report facts versus assumptions and next smallest implementation step.
```

## B. Confirm a candidate edit actually saved

```text
Before changing files, re-read the saved version of [relative path]. Compare it with your previous observed version using size/hash or the actual text. If the editor has unsaved changes or reports an external change conflict, stop and tell me how to resolve it using the provided editor UI. Do not overwrite either version without comparing them.
```

## C. Implement one slice with evidence

```text
The requirement I confirmed is [A]. Modify only the minimal project files needed for [B]. Keep project-specific input and output [C]. Run one normal test and one failure/boundary test. Report which commands you executed, observed outputs, files changed and any unverified result. No unrelated tooling, upgrades, hosted servers, GUI automation or external transfers.
```

## D. Browser check without screenshots

```text
Check the server command and actual port, then test an allowed loopback endpoint if available. I will open the platform's built-in Browser and manually verify the UI. Describe the exact expected visible behavior for normal input [A] and invalid input [B], but do not claim a visual pass until I report the result. Do not take screenshots, automate the browser or create tunnels.
```

## E. Recover from a blank preview

```text
The built-in Browser did not load. Inspect only the authorized project: dev-server process, actual port, local bind address and requested URL path, in that order. Confirm the exact failing step. Do not rewrite unrelated files or install tools. Ask me to refresh/test the built-in Browser manually after the narrow fix.
```

## F. Prepare for a no-AI explanation (before that phase)

```text
Summarize only actual completed work: goal, decision, file/function map, run commands, test evidence, limitations. Mark tests not executed as NOT_RUN. I will explain these from memory myself later; do not write or transmit answers during a no-AI phase.
```

