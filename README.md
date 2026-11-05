# SH Workflows

## 실제 맥락을 먼저 전달한 뒤 시작하기

**새 권장 시작점: [START_PROMPT.md — 실제 과제와 사전 키트를 결합하는 시작 프롬프트](START_PROMPT.md)**

공식 안내·과제 내용·이미 받은 담당자 답변을 평가 환경 안의 **제공 Codex**에 먼저 전달하세요.
외부 ChatGPT나 이 GitHub에는 실제 시험 자료를 보내지 않습니다.
전달을 마친 뒤 제공 Codex에 아래 한 문장으로 요청하면 됩니다.

    내가 지금까지 준 맥락을 바탕으로 .hackathon-kit/START_PROMPT.md를 읽고 적용해라. 승인된 과제 범위 안에서 구현과 허용된 테스트까지 진행해라.

아직 구현을 원하지 않고 맥락만 정리할 때는 마지막 문장을 '지금은 작업 흐름과 첫 단계만 제안해라'로 바꾸세요.
Codex가 이미 받은 내용을 다시 묻지 않고, 실제 규칙·파일·남은 시간에 맞춰 필요한 Skill만 선택하도록 구성했습니다.
키트 전체를 읽거나 원본 지침을 덮어쓰는 방식이 아닙니다. 아래의 개별 첫 지시는 이 시작 파일을 못 읽을 때의 대안입니다.
이 파일이 없는 이전 Clone을 사용 중이면 자동으로 갱신되지 않습니다. 업데이트는 해당 환경의 공식 공개자료 반입 규칙을 따릅니다.

## 여러 Codex 작업을 이해하고 검증하는 새 경로

**[Explainable Workbench](docs/REPORT_WORKBENCH.md)**: 작업별 이유·대안·실제 검사·남은 한계가 누적되는 로컬 보고 화면. 두 탭(보고/판단, 결과/검증), 에이전트별 상태 필터와 독립 기록을 제공한다. 실제 과제와 평가자료를 GitHub에 올리는 기능은 없다.

- **먼저 이해:** [Human-led decision workflow](docs/HUMAN_DECISION_WORKFLOW.md) · [선택 근거 카드](templates/DECISION_EXPLANATION.md)
- **선택 Skill:** [explainable-workbench](.agents/skills/explainable-workbench/SKILL.md) — 설명이 어렵거나 여러 Codex가 병렬 작업할 때만 읽기
- **로컬 실행:** `python3 .hackathon-kit/tools/report_workbench.py --root . serve --port 8765` (사용 환경에서 허용한 경우만)
- **주의:** 파일 기록을 만드는 것은 명시적 `note` 명령뿐이다. 보고 내용은 안전하게 요약하고, 실제 Browser/제출 검증은 사용자가 한다. 프레임 미리보기는 Cofa 등 관리형 IDE에서 정상 작동한다고 보장하지 않는다.

## 고도화 경로: 다음 회차 빠른 경로

여러 AI 해커톤 형식에 공통으로 쓸 수 있는 작업 패턴을 정리했습니다. 특정 과제의 내용·데이터·평가 기준은 이 저장소에 없습니다. 공식 규칙이 항상 우선합니다.

| 상황 | 쓰는 자료 | 핵심 |
| --- | --- | --- |
| 작업 방식을 처음부터 고정하고 싶음 | [오버라이드 운영서](docs/OVERRIDE_INSTRUCTIONS.md) · [AGENTS.override 템플릿](templates/AGENTS.override.template.md) · [첫 메시지 블록](templates/PROMPT_OVERRIDE_BLOCK.md) | 허용될 때만 첫 작업 세션 전에 과제 루트에 AGENTS.override.md를 둔다. 제공 원본 AGENTS.md가 있으면 override 맨 위에 원본 전문을 그대로 붙이고(원본 파일은 그대로), override가 이미 있거나 복사가 애매하면 첫 메시지 블록을 쓴다 |
| 담당자가 구체적인 질문에만 답함 | [stakeholder-agent-questioning](.agents/skills/stakeholder-agent-questioning/SKILL.md) · [멘트 템플릿](templates/QUESTION_MESSAGES.md) · [질문 원장](templates/QUESTION_LEDGER.csv) | 애매·경계·예외·차이를 한 사실짜리 질문으로 바꾼다(결과를 바꾸지 않는 질문은 빼고 P3는 가정으로 기록). 멘트는 Codex가 쓰고 나는 검토·복사·전송만 한다 |
| 이용자와 운영자를 나눠야 함 | [role-separated-design](.agents/skills/role-separated-design/SKILL.md) · [역할 분리 패턴](docs/ROLE_SEPARATION.md) · [역할 매트릭스](templates/ROLE_MATRIX.md) | 역할별 화면·데이터·권한·흐름을 나누고 권한은 처리 함수에서 강제한다 |
| 데이터를 가공하고 최적화 알고리즘을 골라야 함 | [optimization-modeling](.agents/skills/optimization-modeling/SKILL.md) · [최적화 운영서](docs/OPTIMIZATION_PLAYBOOK.md) · `tools/opt_kit.py` | 정제 로그→정식화 카드→기준선→개선→소규모 정확해 비교. 표준 라이브러리만으로 가능 |
| 여러 Codex의 판단·변경·테스트를 누적해서 설명해야 함 | [explainable-workbench](.agents/skills/explainable-workbench/SKILL.md) · [로컬 대시보드](docs/REPORT_WORKBENCH.md) | 1파일 1작성자, 각 에이전트가 이유·대안·근거를 별도 이벤트로 기록해 두 탭에서 확인. 실제 과제/응시자료 외부 업로드 없음 |
| 한도는 없지만 비용이 평가될 수 있음 | [cost-aware-execution](.agents/skills/cost-aware-execution/SKILL.md) · [비용 운영서](docs/COST_OPTIMIZATION.md) · [비용 기록](templates/COST_LOG.md) | 필요한 파일·Skill만 읽고 같은 실패를 반복하지 않는다. 필수 검증은 줄이지 않는다 |
| 위 요소를 미리 연습 | [합성 모의 D: 문화센터 강좌 배정](exercises/session-allocation/BRIEF.md) · [합성 모의 E: 기부 물품 보관 상자 정리](exercises/donation-packing/BRIEF.md) | 진행자가 역할 카드로 구체 질문에만 답한다. D는 배정·역할 분리, E는 적재·묶음과 하한 비교 |

공식 규칙이 참가자 지침 파일을 허용한다면, 맥락을 전달한 뒤 제공 Codex에 이렇게 요청할 수 있습니다.

    .hackathon-kit/START_PROMPT.md를 읽고 적용해라. 0번 오버라이드 확인부터 한다.
    담당자가 구체 질문에만 답하므로 애매한 점은 질문 원장에 올리고(결과를 바꾸지 않는 질문은 빼고 P3는 가정으로 기록) 복사용 멘트를 P0부터 써라.
    역할이 둘 이상이면 역할 매트릭스, 최적화가 필요하면 정식화 카드를 먼저 보여라.
    필요한 파일과 Skill만 읽고 기능마다 비용을 한 줄 기록해라.

표의 용어 풀이: **P0~P3**는 질문 우선순위(P0 = 설계·데이터 모델을 바꿈, P3 = 표시 문구만 바꿈)입니다. **정식화 카드**는 무엇을 정하고(결정 변수), 무엇을 좋게 하며(목적), 무엇을 꼭 지키는지(제약)를 한 장에 적은 표입니다. **기준선**은 가장 단순한 방법의 결과, **정확해**는 작은 입력에서 모든 경우를 따져 구한 최선의 답, **gap**은 내 결과와 정확해의 차이입니다. **헝가리안**과 **최소비용 유량**은 배정 문제의 최선의 답을 구하는 표준 알고리즘입니다.

## 처음 사용하는 사람을 위한 기본 설명서

**이 문서 하나를 위에서부터 읽으면 접속 후 준비부터 Codex 사용, 저장 확인, 제출 전 점검까지 따라갈 수 있습니다.** 아래 명령은 제공된 Linux 계열 터미널을 기준으로 합니다. 실제 시험 안내와 제공 환경이 항상 우선합니다.

이 저장소는 공개된 업무 절차·Skill·연습 도구입니다. 시험 답안이나 자동으로 과제를 풀어 주는 완제품이 아닙니다.

### 1. 지금 무엇부터 해야 하나요?

**공식 접속 → 감독 준비 → 과제/체험 안내 확인 → 작업 폴더 확인 → 허용될 때 Clone → 제공 Codex에 지시** 순서입니다.

- 2026-10-31 안내 기준 **09:40까지 접속·감독 준비**, 시험은 10:00~14:00이었습니다. 다음 회차는 그 회차의 최신 공식 공지 시각을 따르세요.
- 접속과 체험 시작, 본시험 시작은 서로 다릅니다. 개인 링크와 시작 버튼은 본인이 공식 안내에 따라 조작합니다.
- Clone은 우선순위가 감독 연결보다 낮습니다. 자료가 없어도 제공 Codex로 작업할 수 있습니다.
- 본시험을 미리 시작하거나 15분 체험을 임의로 시작하지 마세요. 이미 체험을 사용했다면 반복하지 않습니다.
- 감독 준비가 끝나기 전에는 이 문서를 다 읽으려 하지 않아도 됩니다.

### 2. 화면과 용어를 이렇게 이해하세요

| 이름 | 쉬운 뜻 | 내가 할 일 |
| --- | --- | --- |
| 파일 탐색기 | 작업 파일을 모아 보여주는 목록 | 과제 README와 제공 파일 찾기 |
| 에디터 | 파일 내용을 읽고 고치는 화면 | 수정 후 저장 표시 확인 |
| 터미널 | 짧은 명령을 입력하고 결과를 받는 창 | 아래 명령을 한 줄씩 입력 |
| Codex | 제공 환경에서 코드를 도와주는 AI | 한국어로 목표·조건·할 일을 전달 |
| 공식 Browser | 만든 화면을 직접 확인하는 미리보기 | 실제 버튼·입력·오류 동작 확인 |
| 업무 담당자 채팅 | 업무 기준을 확인하는 통로 | 규정·예외·우선순위 질문 |
| Cofa Helper / 공식 문의 | 환경과 운영 방법을 확인하는 통로 | 접속·저장·제출·허용 범위 문의 |
| Clone | GitHub 자료를 내 작업 공간에 내려받기 | 아래 Clone 명령은 한 번만 실행 |
| Skill | Codex가 읽고 따르는 작업 설명서 | 필요한 파일 경로를 알려 주기 |
| 루트 | 해당 작업의 맨 위 폴더 | 과제 폴더와 참고 키트 폴더 구분 |

터미널 명령과 Codex에게 하는 한국어 요청은 **입력하는 곳이 다릅니다.**
명령은 일반 터미널에, 한국어 요청은 Codex 대화 입력칸에 넣습니다.
명령 앞에 보이는 $ 또는 > 같은 화면 표시까지 복사하지 않습니다.

### 3. 과제 작업 폴더부터 확인하세요

제공된 터미널에서 한 줄씩 입력하고 Enter를 누르세요.

    pwd
    ls

- pwd: 현재 어느 폴더에 있는지 보여줍니다.
- ls: 현재 폴더의 파일 이름을 보여줍니다.
- 탐색기에서 과제의 README와 문제 안내를 읽으세요. 이 GitHub의 README와 과제 README는 다릅니다.
- 과제 폴더가 맞는지 모르겠다면 제공 Codex나 Helper에 확인합니다. 임의로 시스템 폴더를 탐색하지 않습니다.

Git 상태는 필요할 때만 확인합니다.

    git status --short

아무것도 출력되지 않으면 Git이 추적하는 변경이 없다는 뜻일 수 있습니다. 저장·테스트·제출 완료라는 뜻은 아닙니다.
'not a git repository'는 현재 폴더가 Git 저장소가 아니라는 뜻입니다. 임의로 git init을 하지 말고 과제 안내를 따릅니다.

### 4. 공개 자료 반입이 허용되면 Clone하세요

**GitHub 로그인이나 개인 토큰을 넣을 필요가 없는 Public 저장소입니다.**
먼저 탐색기에서 .hackathon-kit 폴더가 이미 있는지 확인하세요. 숨김 폴더라 보이지 않을 수도 있습니다. 기존 다운로드가 있다면 중복 Clone하지 않습니다.

현재 과제 폴더에서 다음 한 줄을 실행합니다.

    git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .hackathon-kit

- sh-workflows: GitHub 저장소 이름입니다.
- .hackathon-kit: 내려받을 참고 폴더 이름입니다. 앞의 점 때문에 숨김으로 보일 수 있습니다.
- --depth 1: 최신 상태 중심으로 내려받아 다운로드를 줄이는 옵션입니다.
- 이 안내대로라면 **cd .hackathon-kit를 하지 않고 과제 폴더에 그대로 머무릅니다.** 과제 코드는 키트 안에 만들지 않습니다.
- Clone은 다운로드이며 Push는 업로드입니다. 시험 중에는 Git Push와 외부 업로드를 하지 않습니다.
- 로그인 요구·접근 거절·네트워크 차단이 나오면 개인 인증정보를 넣거나 우회하지 말고 공식 문의를 이용합니다.

**참고 폴더가 자동으로 제출에서 제외되는 것은 아닙니다.** 별도 참고 경로를 공식적으로 지정했다면 그 경로를 우선합니다. 아래 예시는 과제 폴더 안에 내려받는 방식이므로 제출 전 제외 여부를 반드시 확인해야 합니다.

### 5. 안전 점검은 선택 사항입니다

Python 3.10 이상이 제공되고 해당 작업 폴더 읽기가 허용될 때만 실행합니다.

    python3 -B .hackathon-kit/tools/quick_preflight.py --root .

이 명령은 터미널에 결과를 보여줍니다. 기본 네트워크 접근, 결과 파일 저장, 업로드, 화면 촬영, Codex 업데이트를 하지 않습니다.
-B는 Python 임시 바이트코드 파일 생성을 막는 옵션이며 --root .은 현재 폴더를 점검 대상으로 삼는다는 뜻입니다.

| 표시 | 뜻 | 다음 행동 |
| --- | --- | --- |
| PASS | 그 항목에서 확인한 조건 충족 | 도구 존재 PASS를 실제 실행 성공으로 확대하지 않기 |
| FAIL | 필요한 항목을 찾지 못했거나 검사 실패 | 과제에 꼭 필요한지 판단하고 공식 안내 확인 |
| NOT_RUN | 실행하지 않음 | 통과로 해석하지 않기 |
| BLOCKED | 허용 범위·접근·시간 등의 이유로 진행 못 함 | 우회하지 않고 중단·문의 |
| MANUAL_REQUIRED | 사람이 화면에서 확인해야 함 | 공식 UI에서 직접 확인 |

Python 외 프로그램 버전과 실제 과제 테스트는 이 도구가 실행하지 않습니다.
'python3: command not found'라면 이 선택 점검을 생략하세요. 이 키트를 위해 Python·Node·Codex를 새로 설치하지 않습니다.

### 6. 제공 Codex를 열고 첫 지시를 넣으세요

Codex가 이미 열려 있으면 그 창을 사용합니다. 공식 안내에서 터미널 실행을 지시했다면 다음을 입력합니다.

    codex

/status와 /model 메뉴가 제공되면 현재 상태와 모델을 확인합니다. 안내상 권장 목록은 6.1 Sol·5.6 Terra·6.0 Luna이지만 실제 제공 목록을 따릅니다. **Codex 버전을 업데이트하지 않습니다.**

Codex 대화 입력칸에 아래 내용을 넣으세요.

    .hackathon-kit/.agents/skills/hackathon-task-driver/SKILL.md를 읽고 따르라.
    현재 폴더가 실제 과제 루트이며 .hackathon-kit는 공개 참고용이다.
    과제 README와 허용된 저장 파일에서 목표, 필수 산출물, 제약을 파악해라.
    내가 결정해야 하는 핵심 질문 2~3개와 가장 작은 첫 구현을 제안해라.
    현업 정보가 부족하면 같은 skills 폴더의 stakeholder-interview/SKILL.md를 읽어라.
    담당자가 구체 질문에만 답하면 stakeholder-agent-questioning/SKILL.md를 읽고 복사용 질문 멘트를 써라.
    자동화 흐름을 선택해야 하면 workflow-automation/SKILL.md를 읽어라.
    전체 키트를 읽거나 전역 설정과 기존 AGENTS.md를 덮어쓰지 마라.
    실제 저장 파일과 허용된 실행 결과만 근거로 보고해라.
    미실행은 NOT_RUN으로 남기고 Browser 화면은 내가 직접 확인한다.

Clone했다고 Skill이 자동 등록되는 것은 아닙니다. 위처럼 경로를 알려 읽히면 됩니다.
모든 41개 Skill을 한꺼번에 읽힐 필요는 없습니다.

### 7. 과제는 작은 단위로 진행하세요

**문제 이해 → 담당자 질문 → 답변 반영 → 작은 구현 → 실제 검사 → 내가 판단**을 반복합니다.

1. 누구를 위한 결과인지, 필수 출력과 완료 기준을 정합니다.
2. 이미 안내된 내용은 다시 묻지 않습니다. 결과를 바꿀 질문 2~3개만 담당자에게 묻습니다.
3. 답변을 사실·경험·공식 규정·가설·충돌·미확정으로 구분합니다.
4. 기존 흐름 유지, 일부 수정, 여러 흐름 조합, 새 설계 중 가장 단순한 것을 선택합니다.
5. Codex에게 다음 작은 작업을 맡깁니다.

    방금 확인한 규칙을 반영해 필수 기능 하나부터 구현해라.
    바꿀 파일과 완료 기준을 짧게 설명하고, 기존 작업을 보존해라.
    현재 정책이 허용하는 범위에서 이 기능의 정상·경계·누락/충돌 사례를
    실제 테스트해라. 실행 명령과 실제 결과, 미실행을 구분해라.
    불필요한 서버·DB·외부 API·다중 Agent는 추가하지 마라.

점검 도구는 과제 코드의 정답 여부를 검사하지 않습니다. 과제 README에 맞는 실행·테스트가 별도로 필요합니다.
과제에 필요한 권한·입력 검증·사람 승인은 간단하게 만든다는 이유로 제거하지 않습니다.

반복업무는 다음 정도로 비용을 비교하면 충분합니다.
순절감 시간 = 반복횟수 × (기존 시간 - 자동 처리 - 사람 검토) - 개발·검증 - 운영.
추정한 값과 실제 측정한 값은 구분합니다.

### 8. 저장·실행·화면 확인은 서로 다릅니다

- 에디터에서 글자를 바꿔도 아직 저장되지 않았을 수 있습니다. 공식 저장 버튼·표시를 확인합니다.
- Codex가 읽는 것은 보통 저장된 파일입니다. 내가 편집 중인데 Codex도 같은 파일을 바꾸려 하면 먼저 멈추고 어느 내용이 최신인지 맞춥니다.
- 파일이 저장됐다고 실행에 성공한 것은 아닙니다.
- 테스트 통과가 화면의 모든 동작을 보장하지는 않습니다.
- 실제 서버 실행 명령과 포트는 과제 README·터미널 결과를 따릅니다. 임의의 포트나 URL을 정답으로 가정하지 않습니다.
- 서버가 실행된 뒤 공식 Browser에서 정상 입력, 잘못된 입력의 안내, 버튼, 새로고침·저장 결과를 직접 확인합니다.
- 서버가 실행 중인 터미널은 계속 사용 중일 수 있습니다. 안내된 다른 터미널을 사용하고, 종료 의미를 모르는 상태에서 Ctrl+C를 누르지 않습니다.

내가 직접 본 결과는 제공 Codex에 이렇게 전달할 수 있습니다.

    공식 Browser에서 내가 직접 확인했다.
    기대한 동작은 ○○이고, 실제로는 △△였다.
    관련 파일과 오류 범위만 좁혀 수정해라.

실제 평가 자료를 이 저장소나 외부 ChatGPT·다른 AI에 보내지 않습니다.

### 9. 오류가 나면 이렇게 하세요

| 상황 | 먼저 할 일 |
| --- | --- |
| destination path ... already exists | 이미 폴더가 있음. 삭제·중복 Clone하지 말고 기존 파일 확인 |
| No such file or directory | 현재 위치와 파일 경로 확인. 과제 폴더에서 실행했는지 확인 |
| command not found | 프로그램이 없거나 명령이 다름. 임의 설치하지 말고 제공 방법 확인 |
| Permission denied / 차단 안내 | 우회하지 말고 공식 문의 |
| Codex가 Skill을 못 찾음 | Clone 성공 여부와 정확한 SKILL.md 경로를 제공 Codex에 확인 요청 |
| 화면이 안 열림 | 서버가 실제 실행됐는지, 포트·경로가 맞는지 확인 후 공식 Browser에서 수동 재시도 |
| 저장 내용이 다름 | 사람과 AI의 동시 편집 중단. 양쪽 내용을 보존하고 저장 상태 확인 |
| 감독·AI·플랫폼 장애 | 발생 시각·증상을 공식 문의에 전달. 시간 연장·타이머 정지를 추정하지 않기 |

같은 실패 명령을 계속 반복하지 않습니다. 전체 폴더 삭제·설정 초기화·계정 변경으로 해결하려 하지 않습니다.

### 10. 제출 전과 AI 금지 단계

1. 과제에서 요구한 파일과 경로가 맞는지 확인합니다.
2. 실제로 저장됐는지, 필수 실행·테스트 결과와 남은 한계를 확인합니다.
3. 공식 제출 미리보기에서 참고 키트·합성 예제·불필요한 임시 파일이 섞이는지 확인합니다.
4. .hackathon-kit와 .gitignore가 자동 제외를 보장한다고 생각하지 않습니다. 제외 방법이 불명확하면 Helper에 문의합니다. 키트나 과제 파일을 임의 삭제하지 않습니다.
5. 실제로 차용한 공개 자료는 과제의 표기 방식에 맞춰 밝힙니다.
6. 파일 확정·제출·최종 완료 표시를 각각 본인이 확인합니다. Git 커밋이나 파일 저장은 공식 제출이 아닙니다.

과제 180분 뒤 후속 서술형 6문항×5분이 안내되어 있습니다. 대기·제출 시간까지 공식 일정 안에서 관리하고, 마지막까지 새 기능을 추가하지 않습니다.
**실제 AI 금지 후속 단계가 시작되면 Codex·Skill·외부 AI로 답변을 만들거나 보조받지 않습니다.**

그 전 작업 중에 스스로 다음 여섯 가지를 설명하는 습관을 가지세요:
무슨 요구인가 / 어떤 파일·함수인가 / 입력이 어떻게 출력이 되나 / 왜 이 설계인가 / 실제 실행한 테스트는 / 한계는 무엇인가.

### 11. 기억할 것은 이 한 줄입니다

**내가 목표를 정하고 → 중요한 질문을 하고 → AI에게 작게 맡기고 → 실제 결과를 확인하고 → 내 말로 설명합니다.**

[10가지 한 페이지 판단 카드](docs/DECISION_CARD.md)를 옆에서 참고하면 됩니다.
실제 작동(Technique), 지휘 의도(Intent), 이해(Cognition)는 일반 평가 관점이지 이번 시험의 공식 세부 배점표가 아닙니다.

### 12. 현재 상태와 더 읽을 자료

- 공개 주소: https://github.com/AgenticLab-SH/sh-workflows
- 41개 선택형 Skill, 로컬 읽기 도구, 합성 연습 자료가 있습니다.
- 로컬 합성 테스트 결과는 [CHANGELOG](CHANGELOG.md)의 최신 항목에 적습니다. **실제 Cofa·감독·제출 환경은 NOT_RUN**입니다.
- 0.5.0에서 오버라이드·구체 질문·역할 분리·최적화·비용 자료와 표준 라이브러리 도구 5개(instruction_chain, question_candidates, question_ledger, opt_kit, context_budget)를 추가했습니다. 설치가 필요한 프로그램은 없습니다.
- 최신 main을 사용하세요. 기존 v0.4.0 ZIP에는 최신 보강이 모두 들어 있지 않습니다.
- 사용한 공개 저장소는 2차 결과 통지 전까지 Public으로 유지합니다.
- 개인 Codex 홈·인증정보·세션·회사 내부자료·개인 시험 링크를 가져오거나 공개하지 않습니다.

아래는 필요할 때만 읽는 기존 상세 자료입니다. 모두 외워야 하는 것은 아닙니다.

---

AI와 함께 **문제 정의 → 구현 → 근거 확인 → 제출 → 직접 설명**을 연습하고 수행하기 위한 해커톤 준비 저장소입니다. SK하이닉스 AI 해커톤 2026의 Cofa Probe 2차 준비 내용을 출발점으로 삼았습니다. 일반 채용전형 준비와는 별개이며, 특정 대회의 답안이나 공식 배포물이 아닙니다.

**독립 준비 자료 / 41개 선택형 스킬 / Python 표준 라이브러리 도구 / 선택형 로컬 MCP 6개 도구.** 검증 범위는 [최종 준비 검증 기록](docs/FINAL_PREP_VALIDATION.md)을 참고하세요. 실제 Cofa 환경은 **NOT_RUN**입니다.

## 시험 핵심 자료

**[10가지 한 페이지 판단 카드](docs/DECISION_CARD.md)** · [업무별 합성 흐름 6종](docs/BUSINESS_WORKFLOWS.md)

**[시험 핵심 운영서](docs/EXAM_CORE.md)**에서 시작하세요. Notion의 2차 학습 18개와 관련 정본·연구자료까지 총 22개를 읽고 질문·구현·근거·제출·설명으로 다시 연결했습니다. [반영 범위](docs/NOTION_COVERAGE.md)와 [통합 모의 5종](docs/MOCK_EXAMS.md)을 함께 제공합니다.

## 지금 필요한 것부터

| 상황 | 읽을 자료 |
| --- | --- |
| 시험 당일 5분만 읽을 때 | **[당일 한 장 운영표](docs/EXAM_DAY_FAST_PATH.md)** |
| 고도화 경로(오버라이드·구체 질문·역할 분리·최적화·비용) | 위 [다음 회차 빠른 경로](#고도화-경로-다음-회차-빠른-경로) |
| 처음이며 무엇을 준비해야 할지 모름 | [학습 순서](docs/LEARNING_PATH.md) → [2026 Cofa 준비 기준](docs/COFA_2026_BRIEF.md) |
| 15분 사전 체험 직전 | [15분 점검표](docs/TRIAL_15_MINUTES.md) |
| 허용된 저장 작업폴더에서 기본 도구를 한 번에 읽기 전용 확인 | [한 명령 안전 점검](docs/QUICK_PREFLIGHT.md) · `tools/quick_preflight.py` |
| 내 개인 Codex 홈을 그대로 가져오고 싶음 | [안전한 Skill 선별 반입](docs/SAFE_CODEX_HOME_SELECTION.md) (홈 전체 복사 금지) |
| 허용된 과제 작업 시작 | [180분 실전 운영](docs/HACKATHON_RUNBOOK.md) → [첫 지시문](docs/CLI_READY_PROMPTS.md) |
| 웹 IDE 화면을 AI가 못 봄 | [저장 파일·터미널 연결](docs/WEB_IDE_TERMINAL_ONLY.md) |
| 터미널 명령이 낯섦 | [명령표](docs/TERMINAL_CHEATSHEET.md) |
| Skill을 어떻게 가져오는지 모름 | [가져오기·선택](docs/IMPORT_AND_SELECT_SKILLS.md) |
| 공개 참고 키트가 제출에 섞일까 걱정됨 | [참고/제출 경계](docs/REFERENCE_SUBMISSION_BOUNDARY.md) |
| 직접 문제를 풀며 연습하고 싶음 | [통합 모의 5종](docs/MOCK_EXAMS.md) · [짧은 훈련 6묶음](docs/PRACTICE_COFA.md) |
| 마지막 설명을 준비함 | [후속 설명 연습](docs/NO_AI_REHEARSAL.md) — 실제 AI 금지 단계에서는 사용하지 않음 |
| 다운로드가 필요함 | [릴리스](https://github.com/AgenticLab-SH/sh-workflows/releases) — 전체 소스·개별 Skill ZIP |
| 무엇을 읽고 보강했는지 알고 싶음 | [요구사항 반영표](docs/SOURCE_RECONCILIATION.md), [복원 한계](RECOVERY.md) |

## 가져온 뒤 첫 지시

공개 자료 반입이 허용된 작업 환경에서만 실행합니다. 실제 과제 폴더를 공개 저장소로 바꾸거나 이 저장소에 답안을 작성하지 않습니다.

    git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .hackathon-kit

제공 Codex에 다음처럼 요청합니다.

    .hackathon-kit/.agents/skills/hackathon-task-driver/SKILL.md를 읽어라.
    이 폴더는 참고용 키트이며 실제 과제 루트는 현재 작업 폴더다.
    README와 실제 저장 파일에서 목표·자료·필수 산출물을 파악하고,
    내가 결정해야 할 질문과 가장 작은 첫 구현을 제시해라.
    작업·검사 범위는 현재 환경과 모델 정책을 따르고,
    미실행 검사는 NOT_RUN으로 기록해라.
    화면·미저장 버퍼를 봤다고 추정하지 말고, Browser는 내가 직접 확인한다.

**주의:** 일부 제출 환경은 `.hackathon-kit` 같은 숨김 참고 폴더도 후보 파일로 포함할 수 있습니다. [참고 키트와 제출물을 분리하는 방법](docs/REFERENCE_SUBMISSION_BOUNDARY.md)을 먼저 읽고 공식 미리보기에서 확인하세요. 자동 제외를 가정하지 마세요.

하위 폴더를 Clone했다고 Skill이 자동 발견·등록되지는 않습니다. 경로를 지정해 필요한 본문만 읽히면 됩니다. 전역 설정·기존 AGENTS.md 덮어쓰기·버전 업데이트는 필요하지 않습니다.

방문 신청·고객 문의·합계 수리 모의는 모두 합성 자료입니다. 합계 수리 폴더에는 **의도적으로 오류가 있는 연습 코드**가 있으며 실무 도구나 실제 시험 답안으로 사용하지 않습니다.

## 제공하는 도구와 선택 기준

Python 3.10+가 이미 제공될 때 표준 라이브러리만 사용합니다. 이 키트를 위해 런타임을 새로 설치하지 않습니다.

    python3 .hackathon-kit/tools/audit_csv.py .hackathon-kit/examples/applications.csv --required id,date,people --unique id
    python3 .hackathon-kit/tools/validate_json.py .hackathon-kit/examples/config.json --required version,name
    python3 .hackathon-kit/tools/compare_json.py .hackathon-kit/examples/before.json .hackathon-kit/examples/after.json
    python3 .hackathon-kit/tools/metrics.py .hackathon-kit/examples/classification.csv --actual actual --pred predicted --positive yes
    python3 .hackathon-kit/tools/workspace_probe.py --root . inventory --depth 2 --limit 80
    python3 .hackathon-kit/tools/instruction_chain.py --root .
    python3 .hackathon-kit/tools/question_candidates.py data.csv
    python3 .hackathon-kit/tools/question_ledger.py next .hackathon-kit/templates/QUESTION_LEDGER.csv --format text
    python3 .hackathon-kit/tools/opt_kit.py demo
    python3 .hackathon-kit/tools/context_budget.py --root . --limit 10

위 examples 경로는 예시입니다. 키트의 합성 예제를 쓰려면 .hackathon-kit/examples/...로, 실제 과제에는 허용된 해당 파일 경로로 바꿉니다. 서버를 실제로 시작한 경우에만 smoke_http.py에 **실제 포트와 경로**를 전달합니다.

[Skill 전체 목록](docs/SKILLS_INDEX.md)에서 과제에 필요한 1~2개만 추가로 선택합니다. 프롬프트 설계, 한영 글쓰기·말하기, 요구사항, 개발, 데이터, 테스트 설계와 설명 Skill을 유지했습니다. MCP는 CLI만으로 부족하고 공식 설정 경로가 허용될 때만 선택합니다. 원격 모델·호스팅·추적 기능은 없습니다.

## 규칙과 현재 상태

- 해당 과제의 최신 공지·제공 환경이 이 자료보다 우선합니다. [사용 범위](docs/SAFE_USE.md)를 확인합니다.
- 2026 안내의 공개 저장소 사용 조건에는 **2차 결과 통지 전까지 Public 유지**가 포함됩니다. 세부 근거와 적용 범위는 [기준표](docs/COFA_2026_BRIEF.md)에 분리했습니다.
- 실제 과제·개인 접속 링크·인증정보·감독 자료를 외부 AI, GitHub 또는 원격 MCP로 보내지 않습니다. 시험장 Git Push, 캡처·GUI 자동화, Codex 업데이트를 제공하지 않습니다.
- 준비 자료 작성·패키징·GitHub 게시와 실제 학습·체험·시험 환경 작동은 별개입니다.
- 과거 대화의 18/18·25/25 통과 주장이나 원 Git 커밋은 이 복원본의 검증 결과가 아닙니다. [RECOVERY.md](RECOVERY.md)를 참고합니다.

**릴리스 참고:** v0.4.0 ZIP은 36개 Skill 기준입니다. [v0.5.0 릴리스](https://github.com/AgenticLab-SH/sh-workflows/releases/tag/v0.5.0)에 전체 소스 ZIP, 41개 개별 Skill ZIP과 그 묶음, SHA256SUMS.txt를 게시했습니다. 이후 main에 더해진 변경은 릴리스 ZIP에 없으니 최신 내용은 main을 사용하세요. 개별 Skill ZIP은 루트에 SKILL.md와 agents/openai.yaml만 담고, 다른 문서를 참조하는 줄은 전체 소스가 있을 때만 쓰입니다.

MIT License. SK하이닉스·크래프톤·Cofa·OpenAI가 보증하거나 운영하는 저장소가 아닙니다.
