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

## 상태와 범위
PASS / FAIL / NOT_RUN / BLOCKED / MANUAL_REQUIRED를 검사 상태로 사용한다.
바이너리 PASS는 PATH에서 발견됐다는 뜻이며 실행·버전·권한이 검증된 것은 아니다.
Python 버전은 현재 인터프리터에서 확인한다. 다른 바이너리의 버전과 과제 테스트는 NOT_RUN으로 남긴다.
기본 동작은 네트워크·하위 명령 실행 없이 알려진 파일명만 확인한다.
--fingerprint는 지정한 저장 파일만 제한 크기로 읽는다. 숨김 경로·인증 파일은 거절한다.
차단은 BLOCKED이며 우회하지 않는다. UI는 MANUAL_REQUIRED다.
