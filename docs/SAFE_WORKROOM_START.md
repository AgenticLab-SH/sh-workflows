# 작업공간 시작 절차 v2 — 최초 기록 → 격리 → 보고 3000 / 서비스 3001

이 문서는 공개 재사용 가능한 운영 가이드다. 실제 과제의 원본 README·제공 지침·현재 호스트 정책이 더 높은 우선순위다. 공개 GitHub에는 실제 응시 문항, 소스 산출물, 사용자/구성원 데이터 및 계정 정보를 올리지 않는다. 실제 AI 금지 구간에서는 모든 AI 도움을 중단한다.

## 0. 가장 중요한 원칙

**과제 루트는 모델이 자동으로 찾는 위치가 아니라 참가자가 확인한 VS Code 파일 탐색기의 정확한 폴더다.**

터미널 `pwd -P`와 VS Code 탐색기에서 보이는 과제 폴더를 대조한다. `cd ~`, `/home` 전체 찾기, 상위 폴더의 파일 이동, 전역 Codex 설정 교체, 원본 AGENTS.md 덮어쓰기는 하지 않는다. 루트가 불확실하면 실행하지 말고 공식 환경 안내를 확인한다.

### 목적 구조 (Clone 후)

```text
[사용자가 확인한 과제 루트]/
  README.md                     # 예시: 제공 원본은 손대지 않음
  [공식 제공 파일과 데이터]        # 원위치 보존
  [실제 과제 코드·산출물]         # 과제에서 요구한 위치에만 작성
  .cofa-workbench/             # AI 협업과 사람 이해를 위한 유일한 격리 폴더
    ROOT_PATH.txt              # 수동 확인한 정확한 시작 루트
    INITIAL_STATE.md           # Clone 전 파일 탐색기/최초 상태
    FILES_AT_START.tsv         # Clone 전 원본 파일명/크기 목록, 내용 없음
    kit/                       # Clone된 Public SH Workflows; 수정 대신 참조
      tools/workroom.py
      tools/workroom_ui.html
    docs/                      # 담당자 질문·답, 결론, 역할, 알고리즘, 테스트
      REQUIREMENTS_MAP.md
      DATA_PROFILE.md
      HR_QUESTIONS.md
      HR_ANSWERS.md
      DECISIONS.md
      MODULE_MAP.md
      VERIFICATION.md
      AGENT_ASSIGNMENTS.md
      FINAL_EXPLANATION.md
    events/                    # 에이전트별 독립 JSON 기록(누적·덮어쓰기 없음)
```

`INITIAL_STATE.md`와 `FILES_AT_START.tsv`는 **원본 상태 메타데이터 기록이지 파일 원본 전체 백업이 아니다.** 실제 원본을 수정·삭제하지 말고 필요한 경우 별도의 공식 허용 복구 절차를 사용한다.

## 1. 반드시 Clone 이전에: 초기 상태 기록

VS Code 탐색기에서 과제 루트를 찾고, **그 폴더에서 터미널을 열어** 아래 첫 줄을 실행한 뒤 화면의 경로가 맞는지 사람이 확인한다.

```sh
pwd -P
ls -la
```

정확히 확인했으면 다음 블록을 **한 번만** 실행한다. 프로젝트 루트가 홈 자체이거나 `/`이면 실행하지 않는다. 코드가 이미 기록된 폴더를 덮어쓰지 않도록 분기한다.

```sh
if [ "$(pwd -P)" = "$HOME" ] || [ "$(pwd -P)" = / ] || [ -L .cofa-workbench ] || [ -e .cofa-workbench/ROOT_PATH.txt ]; then
  echo 'STOP: 루트가 너무 넓거나 기존 작업공간 기록이 있습니다. 경로를 확인하세요.'
else
  mkdir -p .cofa-workbench &&
  pwd -P > .cofa-workbench/ROOT_PATH.txt &&
  {
    printf '# 최초 작업공간 상태 (Clone 이전)\n\n'
    printf 'Recorded UTC: '; date -u '+%Y-%m-%dT%H:%M:%SZ'
    printf '\nConfirmed root (LOCAL ONLY): '; pwd -P
    printf '\nTop-level entries (metadata only):\n'
    ls -la | head -80
  } > .cofa-workbench/INITIAL_STATE.md &&
  find . -maxdepth 4 -path './.cofa-workbench' -prune -o -type f -printf '%P\t%s bytes\n' | LC_ALL=C sort | head -400 > .cofa-workbench/FILES_AT_START.tsv &&
  echo '초기 상태 기록 완료: .cofa-workbench/INITIAL_STATE.md'
fi
```

메타데이터는 **프로젝트 내부에서만** 저장되며 어떤 파일 내용도 GitHub로 전송하지 않는다. 400개보다 많은 파일이나 4단계보다 깊은 경로는 상단 요약만 기록될 수 있다. 이 경우 전체 파일 검증이 완료된 것으로 보지 않는다.

## 2. 초기 기록을 확인한 뒤 Public GitHub를 격리 폴더에 Clone

이번 사용자 환경에서 공개 자료 반입이 실제로 허용되어 있을 때만 아래를 실행한다. 이미 kit 폴더가 있다면 강제로 덮어쓰거나 삭제하지 않는다.

```sh
git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .cofa-workbench/kit
python3 .cofa-workbench/kit/tools/workroom.py --root . init
python3 .cofa-workbench/kit/tools/workroom.py --root . status
```

Clone 실패 시 제한을 우회하지 않는다. 제공 Codex만으로 진행하면서 원본 README를 읽고 질문·설계·검증을 계속한다. `init`은 초기 루트와 기록을 검사하고 `.cofa-workbench/docs/` 안에 필요한 빈 양식을 **없을 때만 생성**한다. 같은 이름의 기존 문서는 절대 덮어쓰지 않는다.

## 3. Codex에게 첫 요청 (과제와 별개인 준비 작업만)

```text
현재 pwd가 VS Code 파일 탐색기의 실제 과제 루트인지 먼저 확인하자.
.cofa-workbench라는 별칭/다른 폴더를 만들지 말고 정확히 .cofa-workbench만 사용해.
.cofa-workbench가 아니라 .cofa-workbench/INITIAL_STATE.md와 FILES_AT_START.tsv가 먼저 생성됐는지 확인해.
제공된 README·데이터의 기본 구조를 읽되 모든 원본을 수정하지 마.
처음에는 요구사항 근거와 데이터 품질 통계만 .cofa-workbench/docs에 기록해.
보고가 필요한 사항은 .cofa-workbench/events에 개별 기록으로 남겨.
HR에게 보내기 전, 실제 결과를 바꾸는 질문을 우선순위와 함께 써 주고 내 확인을 받아.
과제 루트 밖, 사용자 홈의 다른 폴더, Codex 전역 설정은 읽거나 수정하지 마.
```

위 프롬프트의 `.cofa-workbench`만 실제 폴더명이다. 이 메시지는 **허용된 업무 준비 단계**에서만 사용한다. 실제 요구·개인 정보는 Cofa 제공 Codex 내부에서만 다룬다.

## 4. 사람이 확인한 선택을 기록하며 구현하기

1. `docs/REQUIREMENTS_MAP.md`에 README에 명시된 출력·제약·파일 위치를 정리한다. 원문과 AI 추정을 분리한다.
2. `docs/DATA_PROFILE.md`에 CSV의 행 단위·열 타입·결측·중복·관계 및 이상 케이스 **건수만** 기록한다. 원본 데이터 복사 금지.
3. `docs/HR_QUESTIONS.md`에 담당자에게 물을 질문을 우선순위별로 작성한다. 참가자가 검토해 공식 채팅으로 질문한다.
4. 참가자가 허용된 공식 HR 답변을 `docs/HR_ANSWERS.md`에 로컬 저장하면, Codex가 이를 읽고 근거·결정·테스트를 갱신한다.
5. `docs/DECISIONS.md`에서 알고리즘 2개 이상을 목적·규칙·속도·설명 가능성·한계로 비교한 후 **사람이 선택**한다.
6. `docs/MODULE_MAP.md`에는 데이터 검증·생성·결과 검증·보관·후보 비교의 소유 파일/함수와 `현재 채택안`의 상태 소유자를 구분한다.
7. 여러 Codex는 `docs/AGENT_ASSIGNMENTS.md`에서 **파일별 단독 작성자**를 정한다. 공용 로그 파일을 동시에 편집하지 않고, 각자의 `events/*.json`에 독립 기록한다.
8. `docs/VERIFICATION.md`에 정상·누락·교차참조 없음·시간 초과·후보 비교·상태 보존 테스트의 기대/관측/미실행을 구분한다.
9. `docs/FINAL_EXPLANATION.md`를 참고해 실제 구현된 것·가정·포기한 것과 AI 제안을 받아들인 이유를 설명할 수 있는지 확인한다. AI 금지 단계에 들어간 뒤에는 이 도움을 사용하지 않는다.

보고용 3000은 문제 해결기나 제출 서버가 아니다. 실제 코드는 과제 README가 요구한 위치에서 수정한다. `kit` 안에 실제 산출물을 작성하거나 `kit` 내용을 복제해 답안으로 제출하지 않는다.

## 5. 웹 브라우저 구성

**보고 화면: 포트 3000 (선택 사항)**

```sh
python3 .cofa-workbench/kit/tools/workroom.py --root . serve --port 3000
```

기본 바인딩은 127.0.0.1이며, 허용된 웹 IDE의 공식 Browser가 컨테이너 포트를 보기 위해 필요한 경우에만 `--host 0.0.0.0`을 사용한다. 공유 네트워크에 민감정보를 공개하지 않도록 보고 요약만 기록한다.

**실제 과제 서비스: 포트 3001 (과제 개발 담당)**

이 공개 키트는 3001 서비스를 자동 실행·중지·대체하지 않는다. 과제별 적합한 실행 명령을 Codex가 README에 맞춰 설정한다. 보고 화면의 `서비스 열기`는 3001을 새 탭으로 열 뿐이다. 실제 포트 프록시 정책에 따라 공식 Browser에서 **3001을 직접 선택**해야 할 수 있다. 3001 작동은 사용자 직접 관측이다.

### 보고 UI 구성

- 상단: 초기 파일 수 / 누적 작업 수 / 관측된 테스트 통과 / 미확정·미실행
- **진행·판단**: 에이전트·상태별 필터, 작업 목적·선택 이유·대안·담당 모듈·다음 판단
- **검증·결과**: 실제 수행한 테스트/관측 근거, 결과 서비스 3001 링크
- **초기 상태**: Clone 전 원본 기록·루트 확인·격리 구조 점검
- 우측: 필수 문서 생성 여부와 **설명 가능한 설계·데이터 흐름·범위·예외·성능·AI 협업** 6개 점검 항목

이는 **공개 자료를 기반으로 제작한 일반 내부 도구 UI**이며 회사의 공식 내부 시스템이나 특정 시험의 정답 UI가 아니다. 공개 SK그룹 CI의 대표색 **SK Red #EA002C**를 시각적 강조에만 적용한다(https://www.sk.co.kr/ko/media/ci.jsp). 회사 로고·내부 자산은 포함하지 않는다.

## 6. 명시적 기록 예

```sh
python3 .cofa-workbench/kit/tools/workroom.py --root . note --agent coordinator --kind decision --state confirmed --title '단순 기준선부터 비교' --reason '검증 가능한 첫 결과를 우선 확보' --alternative '검증 전 복잡한 탐색 알고리즘 도입' --evidence '사람의 설계 선택. 실제 품질 테스트는 NOT_RUN'
```

이 기록은 `.cofa-workbench/events/`에 한 번만 추가된다. 정량 지표를 측정하지 않았으면 성능 향상을 주장하지 않는다. 서비스·코드·상태·비용 검증이 실제로 실행된 후에만 `pass`라고 기록한다.

## 7. 복구·중단

- 3000 포트 점유 시 프로세스를 강제 종료하지 말고 충돌 원인을 확인한다. 다른 포트로 바꾸기 전에 공식 Browser 정책·사용자 선택을 확인한다.
- `init`을 재실행해도 이미 존재하는 문서는 유지된다. `INITIAL_STATE.md`는 재생성하지 않는다.
- 보고·참고 자료도 플랫폼의 제출 후보에 포함될 수 있다. 제출 미리보기에서 제외 여부를 사용자 직접 확인한다. `.gitignore`로 자동 제외되는 것은 아니다.
- 참고 폴더를 지우거나 원본 데이터를 삭제하는 자동 정리 기능은 없다.
- 외부 AI 호출·Git Push·스크린샷·감독 설정 변경·실제 시험 데이터 외부 전송 기능은 없다.
- 실제 Cofa 서비스 상태, 사용자 PC의 실제 경로, 오리지널 과제 파일은 이 공개 개발 과정에서 접근하지 않았다. 허용된 사용자가 직접 확인해야 한다.
