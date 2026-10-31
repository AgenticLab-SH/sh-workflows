# 1회·15분 사전 체험 점검표

체험은 참가자가 개인 링크에서 직접 시작합니다. 이 저장소나 에이전트가 체험을 시작하거나 감독 UI를 조작하지 않습니다. 체험 전에 공개 키트 주소, 충전·Wi-Fi·Chrome·웹캠·유선 입력기기·독립 공간을 준비합니다. 개인 링크는 키트·로그·공유 문서에 적지 않습니다.

아래 분배는 자체 제안입니다. 실제 연결과 운영팀 지시가 우선이며, 이미 체험을 소진했다면 반복 시도하지 않습니다.

| 시간 | 직접 할 일 | 남길 관측 |
| --- | --- | --- |
| 0~3분 | 웹캠·전체 화면 공유·휴대폰 Proctor 연결 | 연결 성공/오류, 촬영 요구사항 |
| 3~5분 | README·탐색기·저장 파일·터미널 확인 | 실제 작업 루트, 저장 반영 여부 |
| 5~8분 | 제공 codex, /status, 허용 모델 메뉴 확인 | 표시 버전·모델·권한, 짧은 요청의 실제 결과 |
| 8~11분 | 합성 연습 파일 저장·허용 실행·내부 Browser | 실제 명령·포트·경로, 수동 화면 결과 |
| 11~13분 | 업무 담당자와 Helper 역할 확인, 여유가 있을 때만 Skill/MCP 메뉴 | 지원·허용·사용 가능을 각각 기록 |
| 13~15분 | 안내에 따른 제출 미리보기·확정·종료 동선 | 어디서 파일이 고정되는지, 완료 표시 |

## One-command environment scan (optional)

If Python 3 is available and local inspection is permitted, the public kit now contains a **read-only** [quick preflight](QUICK_PREFLIGHT.md): `python3 .hackathon-kit/tools/quick_preflight.py --root .` after an allowed Clone. Public GitHub reachability is an explicit option; no output is ever uploaded. This does not inspect the Proctor, unsaved editor buffers, Browser or hidden settings. Skip it if the official trial is short or restrictions are unclear.

## 남은 시간이 부족하면

고급 기능·외부 패키지·MCP 설치 탐색을 먼저 생략합니다. 감독 연결, 저장 파일, 제공 Codex, 제출 동선을 우선합니다. Codex 업데이트·숨은 기능 활성화·개인 파일 반입을 시도하지 않습니다.

## 체험 후 작성

[기능 기록 양식](../templates/TOOL_CAPABILITIES.md)에 OBSERVED / UNSUPPORTED / NOT_RUN과 관측 시각을 씁니다. 예: '메뉴를 봄'은 실행 성공이 아니며, 'Clone 성공'은 Skill 자동 등록 성공이 아닙니다. 오류는 증상과 시각을 공식 문의 경로에 남깁니다. 비밀 URL·문제 전문·스크린샷은 기록하지 않습니다.

이 문서를 읽었다는 사실을 체험 완료로 체크하지 않습니다.

## Notion 17·09에서 보강한 점

앱 설치 QR과 응시 연결 QR은 다른 용도입니다. 안내된 공식 설치와 연결 절차를 참가자가 직접 따릅니다. 메뉴를 봄·허용됨·짧은 요청이 실제 성공함을 다른 상태로 기록합니다. 감독 연결이 지연되면 고급 기능 탐색을 먼저 포기하고 기본 동선에 집중합니다. 체험 버튼을 읽거나 시작을 요청했다는 사실만으로 체험 완료를 체크하지 않습니다.

## 복사해서 쓰는 터미널 명령표
Linux 계열 제공 터미널 기준이다. 명령이 없거나 차단되면 설치·우회하지 않는다.
첫 명령은 현재 과제 위치에서 실행한다. 개인 경로 등 출력은 외부에 복사하지 않는다.

    pwd
    ls
    git status --short

Git 저장소가 아니면 상태 조회 실패만 기록한다. README는 탐색기 또는 허용된 터미널에서 읽는다.
공개 반입이 허용되고 동일 폴더가 아직 없을 때만:

    git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .hackathon-kit
    python3 -B .hackathon-kit/tools/quick_preflight.py --root .
    cat .hackathon-kit/.agents/skills/hackathon-task-driver/SKILL.md
    codex

제공 Codex가 이미 열려 있으면 새로 시작하지 않는다. /status와 /model이 제공되면 직접 확인한다.
안내상 권장 6.1 Sol·5.6 Terra·6.0 Luna의 실제 표시를 확인하고 버전 업데이트는 하지 않는다.
Skill 자동 설치를 가정하지 말고 다음처럼 지시한다:

    .hackathon-kit/.agents/skills/hackathon-task-driver/SKILL.md를 읽고 따르라.
    실제 과제 루트는 현재 폴더이며 .hackathon-kit는 공개 참고용이다.
    업무 조건이 불명확하면 같은 skills 폴더의 stakeholder-interview/SKILL.md를
    추가로 읽고 중요한 질문 2~3개를 제시하라. 답변을 결정에 반영하라.
    저장 파일과 허용된 터미널 결과만 근거로 하고 UI는 내가 직접 확인한다.

필요할 때만 같은 skills 폴더의 workflow-automation/SKILL.md를 읽힌다.
편집 전후 저장 확인은 허용된 특정 파일에만 아래 명령을 반복해 해시 변화를 비교한다.
해시 변화는 저장 파일 변화이며 올바른 동작 또는 미저장 버퍼 일치의 증거가 아니다.

    python3 -B .hackathon-kit/tools/quick_preflight.py --root . --fingerprint README.md

README.md는 실제 수정한 비민감 파일 경로로 바꾼다.
과제 README의 실행·테스트 명령만 수행하고 서버가 실제 시작됐을 때 표시된 포트/경로를 공식 Browser에서 본인이 연다.
정상 입력·오류 안내·저장/새로고침을 직접 확인한다. AI는 화면 관측을 주장하지 않는다.
제출 미리보기에서 .hackathon-kit가 포함되는지 확인하고 공식 제외 방법을 따른다.
키트나 과제 파일을 임의로 삭제하지 않는다. 체험 종료/제출 완료 버튼도 본인이 직접 확인한다.
