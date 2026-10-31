# Concise prompts for a terminal-only coding agent

Use only **inside an authorized runtime** and only when the environment allows public instructions. If the toolkit is cloned into a subfolder, have the agent identify both the actual task root and the imported toolkit path. Reading a nested SKILL.md does not imply automatic skill discovery. Replace examples with task facts already visible to the agent. Never send restricted task material to a separate AI or remote MCP.

## A. Unknown project, no editor vision

```text
You may not be able to see my web editor UI. Use only saved files under the current authorized project root and permitted terminal commands. Inspect pwd, README, saved file paths and runtime. Identify user goal, required files, unclear constraints, and acceptance tests. Do not claim to see unsaved editor buffers or the Browser. Do not change code yet; report facts versus assumptions and next smallest implementation step.
```

## B. Confirm a candidate edit actually saved

```text
Before changing files, re-read the saved version of [relative path]. Compare it with your previous observed version using size/hash or the actual text. If the editor has unsaved changes or reports an external change conflict, stop and tell me how to resolve it using the provided editor UI. Do not overwrite either version without comparing them.
```

## C. Implement one slice with evidence

```text
The requirement I confirmed is [A]. Modify only the minimal project files needed for [B]. Keep project-specific input and output [C]. Run one normal test and one failure/boundary test. Report which commands you executed, observed outputs, files changed and any unverified result. No unrelated tooling, upgrades, hosted servers, GUI automation or external transfers.
```

## D. Browser check without screenshots

```text
Check the server command and actual port, then test an allowed loopback endpoint if available. I will open the platform's built-in Browser and manually verify the UI. Describe the exact expected visible behavior for normal input [A] and invalid input [B], but do not claim a visual pass until I report the result. Do not take screenshots, automate the browser or create tunnels.
```

## E. Recover from a blank preview

```text
The built-in Browser did not load. Inspect only the authorized project: dev-server process, actual port, local bind address and requested URL path, in that order. Confirm the exact failing step. Do not rewrite unrelated files or install tools. Ask me to refresh/test the built-in Browser manually after the narrow fix.
```

## F. Prepare for a no-AI explanation (before that phase)

```text
Summarize only actual completed work: goal, decision, file/function map, run commands, test evidence, limitations. Mark tests not executed as NOT_RUN. I will explain these from memory myself later; do not write or transmit answers during a no-AI phase.
```


The prompts below are short Korean versions for the field-tested paths. Use them only when the official rules allow; the participant still owns every business decision and every message sent.

## G. 오버라이드 반영 확인 (새 세션 첫 메시지)

```text
과제 루트의 AGENTS.override.md(원본 AGENTS.md 전문을 맨 위에 붙였다면 그 부분 포함)와 제공 원본 AGENTS.md를 읽었는지 먼저 알려줘. 이 세션에서 지킬 작업 방식을 3줄로 요약하고, 원본·공식 규칙과 충돌하는 줄이 있으면 그 사실만 적어라. 원본이 우선이다. 아직 코드는 바꾸지 마라.
```

## H. 담당자 질문 멘트 작성

```text
담당자가 구체 질문에만 답하고 질문 수 제한이 없다. 애매·경계·예외·문서와 데이터의 차이를 질문 원장에 올리고(결과를 바꾸지 않는 질문은 빼고 P3는 가정으로 기록), 내가 복사해 보낼 멘트를 P0부터 이번 한 턴에 묶어 써라. 멘트 하나는 맥락 한 줄 + 사실 하나이고 예/아니오·수치·선택지로 답할 수 있어야 한다. 몇 개씩 보낼지와 업무 판단은 내가 정한다.
```

## I. 역할 매트릭스 작성

```text
사용자 역할이 둘 이상이다. templates/ROLE_MATRIX.md 형식으로 역할별 화면·데이터·권한·흐름을 표로 정리해라. 권한은 화면이 아니라 처리 함수에서 막는 위치를 함께 적어라. 확정되지 않은 권한은 질문 원장 후보로 따로 표시해라.
```

## J. 정식화 카드 작성

```text
구현 전에 정식화 카드만 써라: 결정 변수, 반드시 지킬 제약, 가능하면 지킬 선호, 목표 지표, 입력 정제 로그의 근거. 담당자 확인이 없는 제약은 가정으로 표시해라. 코드는 아직 쓰지 마라.
```

## K. 기준선 대비 비교

```text
같은 입력으로 단순 기준선과 현재 개선안을 실행하고 목표 지표·제약 위반 수·실행 시간을 표로 비교해라. 값은 코드로 계산하고 실제 실행한 명령을 적어라. 작은 입력에서 정확해와 비교가 가능하면 함께 보이고, 실행하지 못한 비교는 NOT_RUN으로 적어라.
```

## L. 비용 점검

```text
방금 끝낸 기능의 비용을 한 줄로 기록해라: 읽은 파일 수, 재시도 횟수, 큰 출력이나 전체 파일 재생성 여부. 같은 실패가 2번 있었다면 바꿀 방법을 제안해라. 필수 검증은 줄이지 마라.
```
