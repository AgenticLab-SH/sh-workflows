# 해커톤 터미널 명령표

이 표는 준비용입니다. 제공 셸·프로젝트·현재 검사 정책에 맞는 명령만 사용합니다. Linux 계열 예시이며 개인 Windows/AICC 명령을 시험 환경에 그대로 가져오지 않습니다.

## 세 종류를 구분

| 입력 위치 | 예 | 의미 |
| --- | --- | --- |
| 셸 프롬프트 | pwd, cat README.md | 저장 파일·프로그램 작업 |
| Codex 대화 안 | /status, /model | 제공판이 보여주는 세션·모델 메뉴 |
| 플랫폼 UI | Browser, 업무 담당자, 문의 | 참가자가 직접 조작하는 공식 화면 |

/goal·/skills·MCP·plugin·subagent는 제공판의 도움말/메뉴에서 지원·허용을 확인한 경우에만 사용합니다. 보이지 않는 메뉴를 버전 업데이트나 설정 변경으로 만들지 않습니다.

## 읽기와 위치 파악

    pwd
    ls -la
    cat README.md
    find . -maxdepth 2 -type f
    sed -n '1,100p' README.md
    rg -n 'TODO|FIXME' src

rg가 없으면 설치부터 하지 말고 제공된 grep 등으로 필요한 범위만 읽습니다. node --version, npm --version, python3 --version은 필요할 때 기존 런타임을 알아보는 명령입니다. .env·인증 저장소·개인 링크를 출력하지 않습니다.

## 프로젝트가 실제 제공하는 실행법

    cat package.json
    npm run
    git status --short
    git diff

npm test, npm run build, python3 -m unittest 등은 **해당 프로젝트에 정의되어 있고 검사 실행이 허용될 때만** 사용합니다. 이 저장소를 게시한 작업에서는 이러한 사후 검사를 실행하지 않았습니다.

## 웹앱이 요구될 때

기존 README의 서버 실행 명령을 사용하고 실제 포트를 읽습니다. 내부 Browser가 0.0.0.0 바인딩을 요구하면 그 제공 환경의 문서에 따른 옵션만 사용합니다. 일반 로컬 제어 서버를 공개 노출하라는 뜻이 아닙니다.

    curl -I http://127.0.0.1:3000/
    python3 .hackathon-kit/tools/smoke_http.py --port 3000 --path /

3000은 예시입니다. 실제 서버가 실행된 포트·경로로 바꾸고 서버 터미널을 유지합니다. HTTP 응답만으로 버튼·입력·모바일 화면이 정상이라고 말하지 않습니다. 참가자가 내장 Browser에서 직접 확인합니다.

## 공개 키트 반입

    git clone --depth 1 https://github.com/AgenticLab-SH/sh-workflows.git .hackathon-kit

과제 환경에서 Git Push, private 저장소 접근, 개인 인증 반입을 위한 로그인은 하지 않습니다. 공개 Clone 실패를 다른 계정·프록시·터널로 우회하지 말고 제공 도움말과 공식 문의를 사용합니다. 비파괴적인 오타·경로 수정은 정상 작업으로 처리합니다.

## 명령을 외울 때의 기준

'어디에 있는가 → 무엇이 저장됐는가 → 무엇을 실행하는가 → 어디서 실패했는가 → 결과를 어떻게 확인하는가'의 순서로 기억합니다. 실제 오류를 보기도 전에 런타임 재설치·업데이트·대규모 삭제를 시작하지 않습니다.

## Git 표시와 에디터 저장을 혼동하지 않기

Git의 U는 미추적, M은 수정 표시일 수 있습니다. 그 표시만으로 에디터의 미저장 상태를 확정하지 않습니다. git diff가 비어 있어도 미추적 파일이나 다른 작업 루트가 있을 수 있습니다. 실제 디스크 파일과 제공 에디터의 저장 상태를 구분합니다. 필요한 복구 순서는 [근거·복구](EVIDENCE_AND_RECOVERY.md)를 참고합니다.
