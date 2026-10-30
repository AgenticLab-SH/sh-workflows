---
name: manual-preview-validation
description: Verify a web application developed in a restricted or browser-hosted IDE when the coding agent cannot inspect or control the preview window. Use for server startup, port and bind troubleshooting, HTTP smoke checks, and candidate-operated visual acceptance tests.
---

# Manual browser preview validation

## Separate three distinct claims

1. **Process running:** the dev-server terminal says it started.
2. **Endpoint responding:** an allowed local HTTP request returns a response.
3. **Feature correct in UI:** a human used the environment's official Browser preview, observed the intended result, and checked an expected case.

None of these proves the next automatically.

## Procedure

1. Inspect the project's actual startup script/README and run only necessary, authorized commands. Do not presume the port, framework, available runtime, or automatic GUI control.
2. Keep the dev-server terminal alive. Record the **actual** port printed by the process. In a browser-hosted proxy environment, a `0.0.0.0` bind may be required; follow the environment's official docs.
3. When appropriate, use a **loopback-only** smoke test for server reachability:

   ```sh
   python3 tools/smoke_http.py --port 8000 --path /
   ```

   Replace 8000 with the actual port. If Python or the tool is unavailable, use an approved local `curl` command only if installed. Never access unapproved remote addresses.
4. Have the candidate open the **built-in Browser** preview and manually enter the documented port/path. Have them check one normal input, one boundary/error input, and the resulting state/feedback; a CLI agent need not see the UI.
5. Record only the human-observed outcome as `MANUAL_PASS`, `MANUAL_FAIL`, or `NOT_RUN`. Do not claim screenshots, automatic visual inspection, accessibility audit, or pixel parity unless genuinely supported and explicitly permitted.
6. If the preview is blank: check server process -> port -> binding -> URL path -> refresh in that order. Do not rewrite app code until a concrete failure is reproduced.

## Restricted environment rules

No screenshot automation, DOM scraping, browser driving, remote proxy/tunnel, computer-use tools, extra authentication, or workaround for restricted visibility. No capture or outbound transfer of challenge screens, prompts or results. If the environment does not permit a preview operation, mark it `NOT_RUN` and use file tests instead.

## Required output

Include startup command, actual process status/port, local HTTP result if tested, human-observed browser behavior, and what remains unverified. Differentiate a rendered screen from correct business logic.

