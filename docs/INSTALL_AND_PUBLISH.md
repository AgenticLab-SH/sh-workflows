# Install and publish this independent repository

## Local testing (outside a restricted exam)

```bash
python3 --version
python3 -m unittest discover -s tests -v
python3 tools/audit_csv.py examples/applications.csv --required id,date,people --unique id
```

Use individual skills from `.agents/skills/<skill-name>/SKILL.md`. For a browser-hosted IDE, see `docs/WEB_IDE_TERMINAL_ONLY.md` and prefer one relevant Skill at a time. Some Codex versions discover repository-local `.agents/skills` automatically, but that behavior depends on the host and its policy. A Git clone **does not guarantee** automatic activation.

## Publish a **new empty public repository** (only if the owner approves)

1. In your GitHub account, create **one new public repository** named `ai-workflow-open-kit`, with **no README/license/gitignore added by GitHub** (already bundled here).
2. Outside any monitored test environment, extract the full source archive and run:

```bash
git init -b main
git add README.md LICENSE AGENTS.md CONTRIBUTING.md .gitignore .agents docs examples tests tools
git commit -m "Add offline-first public workflow skills and validation tools"
git remote add origin https://github.com/YOUR_ACCOUNT/ai-workflow-open-kit.git
git push -u origin main
```

3. Verify the repository is marked **Public**, and that the `.agents/skills` folder, `tools/` files and tests are visible to a signed-out visitor. Keep your authentication private. When used under a particular contest policy, maintain public visibility for the entire operator-required period.

### Alternative: Git bundle

If a `.bundle` file is available, clone it to recover the original initial commit and point `origin` to the *empty* new repository. Do not push a bundle into an existing unrelated project.

## What is not automatic

- No integration with private ChatGPT or personal Codex skills.
- No guarantee the test runner or exam Cofa environment permits cloning, MCP setup, or advanced Codex commands.
- No hosted MCP endpoint, tokens or external service.
- No publication until a verified GitHub repository and commit exist.

