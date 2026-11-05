# Workroom V3 · 자료 계층, 색상, 에이전트 보고 규약

> 공개·범용 준비 자료. 실제 과제 원문, CSV 행, 직원 정보, 응시 링크, 답안·실행 로그를 이 공개 GitHub에 올리지 않는다. 실제 제공 환경·평가 규칙이 우선한다.

## 1. 하나의 작업공간과 두 서비스

1. 사용자가 VS Code 탐색기의 **실제 과제 루트**와 터미널 `pwd -P`를 대조한다. 홈/상위 폴더 전수 검색 금지.
2. **Clone 전에** 과제 루트의 `.cofa-workbench/ROOT_PATH.txt`, `INITIAL_STATE.md`, `FILES_AT_START.tsv`를 남긴다. 원본 README·CSV·소스를 변경하지 않는다.
3. 허용된 경우에만 `git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .cofa-workbench/kit`.
4. `python3 .cofa-workbench/kit/tools/workroom.py --root . init`.
5. **3000**: `python3 .cofa-workbench/kit/tools/workroom.py --root . serve --port 3000` → 보고/판단/초기 상태를 보는 읽기 전용 UI.
6. **3001**: 실제 과제에서 요구하는 앱. Workroom은 이 서비스를 자동 생성·검증하지 않는다.
7. `.cofa-workbench/docs/`는 과제 내 비공개 기록, `.cofa-workbench/events/`는 각 에이전트의 독립 JSON 기록이다. 원본·실제 제출물은 과제 지시의 경로를 그대로 따른다.

## 2. 자료 계층 L0~L4 (결과로 연결하는 순서)

| 레벨 | 정보의 성격 | 책임 | 기본 문서/기록 | 표시선 |
| --- | --- | --- | --- | --- |
| **L0 원본** | 과제 루트, 최초 파일 상태, 원문·출처 보존 | 사용자 | `ROOT_PATH.txt`, `INITIAL_STATE.md`, `FILES_AT_START.tsv` | 중립 회색 `#565F68` |
| **L1 요구·질문** | 요구·데이터 품질, 미확정 사항, 담당자 답변 | 요구/데이터 담당 | `REQUIREMENTS_MAP.md`, `DATA_PROFILE.md`, `HR_QUESTIONS.md`, `HR_ANSWERS.md` | 파랑 `#2463A6` |
| **L2 인간 결정** | 목표·범위·알고리즘·대안·결정 근거·승인 | 사용자 + 조정자 | `DECISIONS.md`, `MODULE_MAP.md` | 보라 `#7649AA` |
| **L3 구현·인계** | 변경 파일·함수·담당자·실행 설명·작업 인계 | 작성자 한 명/파일 | `AGENT_ASSIGNMENTS.md`, `implementation`/ `handoff` 이벤트 | 청록 `#137C83` |
| **L4 검증·설명** | 기대/실제, 실행 테스트, 실패·한계, 재현/독립 설명 | QA + 사용자 | `VERIFICATION.md`, `FINAL_EXPLANATION.md` | 녹색 `#23764C` |

레벨은 **정보가 쌓이는 흐름**이며 중요도·완료 상태·확신도를 뜻하지 않는다. `P0~P3`는 별도의 **질문/조치 우선순위**로 P0가 가장 급하다. `kind`에 따른 기본 단계는 `question/risk=L1`, `decision=L2`, `implementation/handoff=L3`, `verification/result=L4`다. 별도 근거가 있으면 `--level L0~L4`로 지정한다.

## 3. 화면의 가독성과 상태 색상

- **글자:** 제목·본문·표·필터·사이드바 모두 거의 검정색 `#111111`. 배경은 흰색/밝은 회색. 작은 회색 글씨로 핵심을 숨기지 않는다.
- **레벨 색:** 카드 왼쪽 5px 선과 작은 단계 표식에만 사용. 색만으로 구분하지 않고 L0~L4 텍스트를 항상 함께 표시한다.
- **상태:** `proposed`(제안), `confirmed`(근거 있는 확정), `implemented`(파일 작성), `pass`(실제 관측 성공), `fail`(관측 실패), `not_run`(미실행), `blocked`(제약으로 중단).
- **상태 배경:** PASS 연녹 `#EAF5EE`, FAIL 연빨강 `#FFE8EA`, BLOCKED 연노랑 `#FFF2DE`, NOT_RUN 연회색 `#F5F5F5`, CONFIRMED/IMPLEMENTED 연파랑 `#ECF3FF`. 모든 상태 글씨는 검정이다.
- 색은 정보 식별용이며 실제 기업 내부 디자인 시스템이나 공식 점수 색상이 아니다.

## 4. 에이전트 역할과 파일 책임

| 역할(`--role`) | 맡는 일 | 보고할 핵심 근거 | 금지할 것 |
| --- | --- | --- | --- |
| `coordinator` | 목표·우선순위·작업 배분·결정 대안 제시 | 선택 근거·누가 승인하는지·다음 체크포인트 | 승인 없이 정책 확정 |
| `requirements` | README·제약·HR 질문 | 질문 ID·문서 근거·설계에 미치는 영향 | 추측을 담당자 답변으로 둔갑 |
| `data` | CSV 스키마·행 단위·중복·결측 건수 | 관측 건수·불일치·누락 처리 질문 | 직원 원본 행 복제/외부 전송 |
| `stakeholder` | 답변 정리·출처 구분 | 질문 ID → 답변 출처 → 영향을 받는 요구 | 담당자에게 자동 전송 |
| `algorithm` | 기준선·대안·제약·복잡도·한계 | 목적함수·평가지표·설계 비교·독립 검사 | 검증 없는 최적해 주장 |
| `implementation` | 승인 범위의 코드·설정 작성 | 파일/함수·실제 변경·테스트 결과 | 다른 작성자 파일 동시 수정 |
| `ui` | 결과를 누구나 이해·확인할 화면 | 사용자 동선·입력/오류/빈 상태·수동 확인 요청 | 화면을 보지 않고 UI PASS 주장 |
| `qa` | 정상/경계/예외·재현 가능 검증 | 명령·기대·관측·FAIL/NOT_RUN | 실행 없이 PASS |
| `integration` | 모듈·상태 소유·최종 통합 | 의존성·통합 테스트·미완료·인계 | 기존 작업 덮어쓰기 |

동시에 여러 코덱스를 실행해도 **코드 파일 하나의 작성자는 한 명**이다. 각 에이전트의 보고 이벤트는 별도 파일에 자동 생성되어 충돌하지 않는다. 조정자만 변경 범위와 상태 소유권을 최종 통합한다.

## 5. 에이전트 보고 시점과 필수 필드

**시점:** (1) 결과를 바꾸는 요구/질문 발견 (2) 사용자 결정 필요 (3) 실제 코드 변경 (4) 실제 검증/실패 (5) 다른 에이전트에 인계. 매 명령마다 기록하지 않는다.

**보고 항목:** `agent` / `role` / `kind` / `state` / `level` / `priority` / `basis` / `source_ref` / `decision_by` / `title` / `summary` / `reason` / `alternative` / `evidence` / `module` / `limitation` / `next_action`.

**근거 유형 `--basis`:** `official`, `stakeholder`, `human`, `observed`, `assumption`, `agent`, `unspecified`. 미확정 가정은 확정 사실로 올리지 않는다. **`decision + confirmed`는 `--decision-by human|stakeholder|official`이 필요하다. `pass`는 `verification|result`와 `--basis observed`, 실제 실행 근거가 필요하다.** 참고: 프로그램은 증거 문자열의 존재와 유형만 검사하며 실제 진실 여부를 독립 인증하지 못한다.

### 실제 실행 예시 (합성·공개 정보로만)

```sh
# 명시적 미확정 질문: 실제 전송은 사용자가 한다.
python3 .cofa-workbench/kit/tools/workroom.py --root . note \
  --agent analyst --role requirements --kind question --state proposed \
  --priority P0 --basis official --source-ref R-001 \
  --title "결과에 영향을 주는 미확정 조건" --summary "현재 처리 방식은 확인 전"

# 사람의 확정 결정: 사용자가 승인한 경우에만.
python3 .cofa-workbench/kit/tools/workroom.py --root . note \
  --agent coordinator --role coordinator --kind decision --state confirmed \
  --level L2 --basis human --decision-by human --source-ref D-001 \
  --title "작은 기준선 먼저 구현" --reason "설명·검증에 유리함" \
  --alternative "먼저 복잡한 탐색을 구현"

# 실제 실행 근거가 있는 합성 테스트 예시.
python3 .cofa-workbench/kit/tools/workroom.py --root . note \
  --agent qa --role qa --kind verification --state pass --level L4 \
  --basis observed --source-ref T-001 --title "합성 파일 기본 검사" \
  --evidence "command: python -m unittest; observed: 1 test passed"
```

실제 과제 파일명·HR 응답·개인 기록은 이 공개 문서에 복사하지 않는다. 보고 서버는 로컬에서 읽기 전용으로 제공하고, 출력을 GitHub로 Push하지 않는다. 보고 UI의 `3000` 포트와 실제 서비스 `3001` 포트는 서로 다른 책임이다.

## 6. 사용자가 최종적으로 설명할 내용

**왜 선택했나(대안·한계) / 데이터가 어떤 모듈을 흐르나(상태 소유) / 무엇이 구현·가정·제외인가 / 정상·오류 동작 / 실제 개선 지표와 검증 / AI 제안 중 채택·수정·거절의 근거**.

AI 지원을 허용하는 개발 단계에서 이해도를 점검하되, 실제 AI 금지 서술형 단계에 들어가면 자동 보고·질문 생성·AI 코칭을 중단한다.
