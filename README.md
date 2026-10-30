# AI 해커톤 실전 준비 키트
# AI Hackathon Prep Kit

AI와 함께 **문제 정의 → 구현 → 근거 확인 → 제출 → 직접 설명**을 연습하고 수행하기 위한 해커톤 준비 저장소입니다. SK하이닉스 AI 해커톤 2026의 Cofa Probe 2차 준비 내용을 출발점으로 삼았습니다. 일반 채용전형 준비와는 별개이며, 특정 대회의 답안이나 공식 배포물이 아닙니다.

**독립 준비 자료 / 36개 선택형 스킬 / Python 표준 라이브러리 도구 / 선택형 로컬 MCP 6개 도구.** 이 복원·보강본의 테스트, 빌드, 실행 및 Cofa 환경 검증은 **미실행(NOT_RUN)**입니다.

## 지금 필요한 것부터

| 상황 | 읽을 자료 |
| --- | --- |
| 처음이며 무엇을 준비해야 할지 모름 | [학습 순서](docs/LEARNING_PATH.md) → [2026 Cofa 준비 기준](docs/COFA_2026_BRIEF.md) |
| 15분 사전 체험 직전 | [15분 점검표](docs/TRIAL_15_MINUTES.md) |
| 허용된 과제 작업 시작 | [180분 실전 운영](docs/HACKATHON_RUNBOOK.md) → [첫 지시문](docs/CLI_READY_PROMPTS.md) |
| 웹 IDE 화면을 AI가 못 봄 | [저장 파일·터미널 연결](docs/WEB_IDE_TERMINAL_ONLY.md) |
| 터미널 명령이 낯섦 | [명령표](docs/TERMINAL_CHEATSHEET.md) |
| Skill을 어떻게 가져오는지 모름 | [가져오기·선택](docs/IMPORT_AND_SELECT_SKILLS.md) |
| 직접 문제를 풀며 연습하고 싶음 | [6개 실전 훈련](docs/PRACTICE_COFA.md) |
| 마지막 설명을 준비함 | [후속 설명 연습](docs/NO_AI_REHEARSAL.md) — 실제 AI 금지 단계에서는 사용하지 않음 |
| 다운로드가 필요함 | [릴리스](https://github.com/AgenticLab-SH/ai-hackathon-prep-kit/releases) — 전체 소스·개별 Skill ZIP |
| 무엇을 읽고 보강했는지 알고 싶음 | [요구사항 반영표](docs/SOURCE_RECONCILIATION.md), [복원 한계](RECOVERY.md) |

## 가져온 뒤 첫 지시

공개 자료 반입이 허용된 작업 환경에서만 실행합니다. 실제 과제 폴더를 공개 저장소로 바꾸거나 이 저장소에 답안을 작성하지 않습니다.

    git clone --depth 1 https://github.com/AgenticLab-SH/ai-hackathon-prep-kit.git .hackathon-kit

제공 Codex에 다음처럼 요청합니다.

    .hackathon-kit/.agents/skills/hackathon-task-driver/SKILL.md를 읽어라.
    이 폴더는 참고용 키트이며 실제 과제 루트는 현재 작업 폴더다.
    README와 실제 저장 파일에서 목표·자료·필수 산출물을 파악하고,
    내가 결정해야 할 질문과 가장 작은 첫 구현을 제시해라.
    작업·검사 범위는 현재 환경과 모델 정책을 따르고,
    미실행 검사는 NOT_RUN으로 기록해라.
    화면·미저장 버퍼를 봤다고 추정하지 말고, Browser는 내가 직접 확인한다.

하위 폴더를 Clone했다고 Skill이 자동 발견·등록되지는 않습니다. 경로를 지정해 필요한 본문만 읽히면 됩니다. 전역 설정·기존 AGENTS.md 덮어쓰기·버전 업데이트는 필요하지 않습니다.

## 제공하는 도구와 선택 기준

Python 3.10+가 이미 제공될 때 표준 라이브러리만 사용합니다. 이 키트를 위해 런타임을 새로 설치하지 않습니다.

    python3 .hackathon-kit/tools/audit_csv.py .hackathon-kit/examples/applications.csv --required id,date,people --unique id
    python3 .hackathon-kit/tools/validate_json.py .hackathon-kit/examples/config.json --required version,name
    python3 .hackathon-kit/tools/compare_json.py .hackathon-kit/examples/before.json .hackathon-kit/examples/after.json
    python3 .hackathon-kit/tools/metrics.py .hackathon-kit/examples/classification.csv --actual actual --pred predicted --positive yes
    python3 .hackathon-kit/tools/workspace_probe.py --root . inventory --depth 2 --limit 80

위 examples 경로는 예시입니다. 키트의 합성 예제를 쓰려면 .hackathon-kit/examples/...로, 실제 과제에는 허용된 해당 파일 경로로 바꿉니다. 서버를 실제로 시작한 경우에만 smoke_http.py에 **실제 포트와 경로**를 전달합니다.

[기존 Skill 전체 목록](docs/SKILLS_INDEX.md)에서 과제에 필요한 1~2개만 추가로 선택합니다. 프롬프트 설계, 한영 글쓰기·말하기, 요구사항, 개발, 데이터, 테스트 설계와 설명 Skill을 유지했습니다. MCP는 CLI만으로 부족하고 공식 설정 경로가 허용될 때만 선택합니다. 원격 모델·호스팅·추적 기능은 없습니다.

## 규칙과 현재 상태

- 해당 과제의 최신 공지·제공 환경이 이 자료보다 우선합니다. [사용 범위](docs/SAFE_USE.md)를 확인합니다.
- 2026 안내의 공개 저장소 사용 조건에는 **2차 결과 통지 전까지 Public 유지**가 포함됩니다. 세부 근거와 적용 범위는 [기준표](docs/COFA_2026_BRIEF.md)에 분리했습니다.
- 실제 과제·개인 접속 링크·인증정보·감독 자료를 외부 AI, GitHub 또는 원격 MCP로 보내지 않습니다. 시험장 Git Push, 캡처·GUI 자동화, Codex 업데이트를 제공하지 않습니다.
- 준비 자료 작성·패키징·GitHub 게시와 실제 학습·체험·시험 환경 작동은 별개입니다.
- 과거 대화의 18/18·25/25 통과 주장이나 원 Git 커밋은 이 복원본의 검증 결과가 아닙니다. [RECOVERY.md](RECOVERY.md)를 참고합니다.

MIT License. SK하이닉스·크래프톤·Cofa·OpenAI가 보증하거나 운영하는 저장소가 아닙니다.
