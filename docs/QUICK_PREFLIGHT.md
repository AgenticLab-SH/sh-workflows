# One-command authorized workspace preflight

Use only where the current operator rules permit Python and a read of the saved project directory. The script has no GUI, capture, account, upload, Git Push, secret collection, filesystem write or Codex-update functionality.

From the authorized project root **after** a permitted public Clone into `.hackathon-kit`:

```sh
python3 .hackathon-kit/tools/quick_preflight.py --root .
```

Only with explicit permission to contact the public GitHub repository:

```sh
python3 .hackathon-kit/tools/quick_preflight.py --root . --check-public-github
```

Optional hash of a specifically permitted non-sensitive saved file (not the unsaved editor buffer):

```sh
python3 .hackathon-kit/tools/quick_preflight.py --root . --fingerprint README.md
```

Results are printed **locally to terminal**; `--format json` prints machine-readable metadata. No automatic file saving or external upload. A public GitHub PASS proves only read connectivity, **not** Clone permission, Skill registration or task validity.

Independent personal practice only: a user may redirect JSON stdout to a local file after checking that the destination and its contents are safe. Never push results, problem details, diagnostic output, screenshots or private environment data from a monitored assessment to GitHub.

UI/manual-only checks: Codex `/status` and `/model`, shared save state, Proctor, provided Browser, assignment rules and submission preview. If a check is blocked or unavailable, record `NOT_RUN`; do not retry through other accounts or tooling.
