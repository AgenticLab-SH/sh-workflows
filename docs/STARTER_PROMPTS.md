# Reusable prompts / 재사용 프롬프트

For terminal-only agents and browser-hosted IDEs, see [CLI-ready prompts](CLI_READY_PROMPTS.md) and [the saved-file bridge](WEB_IDE_TERMINAL_ONLY.md).

All templates are **general study materials**. Replace placeholders with facts from the current authorized task. Never inject exam prompts or confidential data into a separate AI service.

## 1. Requirements-first / 요구 정의

```text
배경: [누가 겪는 어떤 문제]
목표: [필수로 해결할 업무]
자료: [실제로 제공된 파일/문서/README]
제약: [시간, 금지 동작, 입력/출력, 개인정보]
요구: 명시된 조건 / 불명확한 조건 / 충돌하는 규칙을 먼저 분리해라.
내가 담당자에게 질문할 우선순위 높은 3~5개를 제시해라.
마지막에는 최소 기능과 실제 실행 검증 기준을 써라.
``` 

## 2. One thin runnable slice / 작은 첫 구현

```text
현재 README의 필수 산출물과 실제 파일을 확인하라.
선택한 최소 기능 한 개만 구현하라. 원본 자료는 변경하지 않는다.
실행 명령과 정상·누락·경계값 세 사례를 직접 검사하고 실제 출력을 기록해라.
검증되지 않은 경우 완료로 주장하지 않는다.
``` 

## 3. Error → fix → regression / 오류 수정

```text
Expected: [확인한 기대 출력]
Observed: [실제 출력과 오류]
Reproduction: [사용한 파일/명령과 테스트 입력]
Fix scope: [수정해도 되는 파일/모듈]
After fixing: rerun failing input and one previously passing case.
Report concrete evidence, changed files, and remaining limitations.
``` 

## 4. Writing KR / 한국어 실무 보고

```text
대상: [고객/담당자/동료]
목적: [결정 또는 행동 요청]
확인된 사실: [목록]
미확정: [목록]
문체: 자연스럽고 간결한 존댓말.
출력: 결론 먼저, 근거, 한계, 다음 행동 1개.
없는 사실·일정·보상 약속은 추가하지 않는다.
``` 

## 5. English status update / 영어 실무 보고

```text
Audience: [team/customer]
Goal: explain current status and request one action.
Verified facts: [data]
Open questions: [unknown]
Style: direct, professional, concise, speakable English.
Output: result first, evidence, constraint, action.
Do not invent dates, promises, or success claims.
``` 

## 6. Explanation rehearsal without AI / AI 없는 설명 훈련

Practice **before** any restricted examination, not in its no-AI phase:
- What did I actually build?
- Which requirement is implemented in which file?
- What was observed by a real run, and what is unverified?
- Why did I choose this option over a simpler alternative?
- How does failure or missing input propagate?
- What is the next improvement and its tradeoff?

Answer from memory and your actual work notes. Do not memorize invented evidence.

