# 가져오기와 필요한 Skill만 선택하기

## 제공 환경에서 공개 Clone이 허용될 때

    git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .hackathon-kit

**주의:** 이 `.hackathon-kit` 폴더가 플랫폼 제출 후보에 포함되지 않는지 자동 보장되지 않습니다. [참고 키트/제출 경계](REFERENCE_SUBMISSION_BOUNDARY.md)에서 실제 제출 미리보기 확인 절차를 먼저 읽으세요.

목적지는 참고용 하위 폴더입니다. 기존 프로젝트·README·AGENTS.md·.agents 디렉터리를 덮어쓰지 않습니다. 과제 루트와 키트 루트를 각각 알아둡니다.

Codex에 다음과 같이 **정확한 본문 경로를 읽도록** 요청하면 자동 탐색 여부를 추측할 필요가 없습니다.

    .hackathon-kit/.agents/skills/hackathon-task-driver/SKILL.md를 읽고
    현재 과제의 목표·자료·제출물에 맞게 적용해라.
    키트 폴더가 실제 과제라고 착각하지 마라.

| 현재 문제 | 추가로 읽을 Skill |
| --- | --- |
| 업무 규칙이 불분명 | requirements-discovery 또는 stakeholder-interview |
| AI 지시가 길고 모호함 | prompt-engineering |
| 웹 IDE 파일이 안 보임 | web-ide-terminal-bridge |
| 에디터와 저장 파일이 다름 | saved-file-reconciliation |
| 첫 기능을 작게 구현 | codex-build-loop 또는 과제에 맞는 frontend-mvp/backend-api |
| 규정 문서끼리 충돌 | document-rule-reconciliation |
| CSV·JSON 입력 품질 | data-profiling |
| 오류 원인 조사 | debugging-verification |
| Browser를 AI가 볼 수 없음 | manual-preview-validation |
| 제출 구조·실행법 정리 | documentation-handoff |
| Clone한 키트가 제출 대상에 포함될 수 있음 | reference-submission-review |
| 사전 설명 연습 | short-answer-defense — 실제 no-AI 단계에서는 사용 금지 |

처음에는 진행 Skill과 현재 필요한 Skill 1개면 충분합니다. 37개를 전부 읽히거나 설치하는 것은 권장하지 않습니다.

## 개별 ZIP은 언제 사용하는가

[릴리스](https://github.com/AgenticLab-SH/sh-workflows/releases)의 Skill ZIP은 각각 SKILL.md가 ZIP 루트에 오는 독립 패키지입니다. 소스 전체 ZIP은 하나의 Skill이 아닙니다.

개인 연습 환경에서 공식 업로드 UI가 제공하는 경우 해당 ZIP을 사용합니다. **Cofa에서 개인 파일 업로드가 허용된다는 뜻은 아닙니다.** 실제 평가에서는 제공된 공개 Clone 경로와 허용 절차를 우선합니다.

## MCP·plugin은 기본 준비가 아님

이 키트의 로컬 stdio MCP는 6개 읽기 전용 도구를 제공합니다. 허용된 공식 등록 UI와 필요한 도구 호출 기능이 모두 있을 때만 설정합니다. 외부 AI나 원격 MCP를 연결하지 않습니다. plugin manifest를 추가한다고 제공 Codex의 plugin 기능이 생기는 것은 아닙니다.

## 기존 지침과 충돌하면

실제 과제 README와 현재 시스템/모델 정책이 우선입니다. 이 키트는 권한·검사·사용 도구 제한을 덮어쓰지 않습니다. 특정 도구가 안 되면 그 도구에 의존한 작은 단계만 보류하고, 이미 허용된 파일 작업은 계속합니다.
