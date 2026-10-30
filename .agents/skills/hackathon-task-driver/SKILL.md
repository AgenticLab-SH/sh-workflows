---
name: hackathon-task-driver
description: Run a time-boxed AI hackathon task from ambiguous brief to minimal deliverable, evidence and submission preparation in the provided IDE; use for task execution, not live no-AI follow-up answers.
---

# 해커톤 과제 진행

제공된 환경의 작은 실행 가능한 결과물과 참가자의 이해를 연결한다. 대회·과제 규칙과 현재 모델 정책이 우선이며, 일반 채용이나 다른 평가의 규칙을 섞지 않는다.

## 시작

- 실제 과제 루트와 이 키트 폴더를 구분하고 README·허용된 저장 파일·필수 산출물을 읽는다.
- 사용자, 업무 문제, 입력, 규칙, 출력, 완료 예시를 나눈다. 미확정 규칙을 추측하지 않는다.
- 업무 판단은 업무 담당자에게, 환경·제출 문제는 Helper/공식 문의에 묻도록 구분한다.
- 지원되는 단일 Codex로 시작한다. 키트 전체를 읽히거나 전역 AGENTS/config를 덮어쓰지 않는다.

## 진행

1. 결과를 바꿀 모호함부터 질문하고 확인된 규칙·남은 질문을 짧게 기록한다.
2. 입력→처리→출력의 첫 작은 기능을 고른다. 과제가 요구하지 않는 화면·서버·DB는 추가하지 않는다.
3. 배경·목표·자료·제약·출력·판단 기준을 묶어 현재 필요한 기능만 구현한다.
4. 저장 파일과 허용된 실제 명령 결과를 근거로 상태를 기록한다. 에디터 미저장 버퍼나 Browser 화면을 봤다고 추정하지 않는다.
5. 현재 정책이 허용한 검사만 수행한다. 금지된 검사를 다른 도구/에이전트에 넘기지 않고 NOT_RUN으로 표시한다. 코드상 예상·실행 결과·참가자의 수동 Browser 관측을 구분한다.
6. 남은 시간에 맞춰 새 기능을 멈추고 필수 파일·실행법·근거·차용 자료·한계를 정리한다. 제출 화면과 확정은 참가자가 직접 수행한다.

오류가 나면 기대값, 실제 오류, 관련 파일과 수정 범위만 추가한다. 이미 전달됐는지 모르는 요청을 반복 보내지 않는다. 지원되지 않는 선택 도구 때문에 허용된 다른 작업까지 중단하지 않는다.

## 도구 선택과 중지

- /goal·subagent·plugin·MCP는 실제 제공·허용될 때만 선택한다. 기본 제공이 아니면 일반 지시와 CLI를 쓴다.
- 병렬 기능을 사용할 수 있어도 같은 파일의 작성자는 한 명으로 유지한다.
- 숨은 설정 변경, Codex 업데이트, 별도 AI 연결, 캡처·GUI 자동화, 제한 우회나 과제 데이터 외부 전송을 수행하지 않는다.
- 실제 AI 금지 후속 단계가 시작되면 답변·메모 생성·도구 사용을 중단한다. 설명 리허설은 그 전에만 한다.

## 필요할 때만 읽기

- 전체 흐름·시간 배분: ../../../docs/HACKATHON_RUNBOOK.md
- 처음 배우는 참가자: ../../../docs/LEARNING_PATH.md
- Skill 선택: ../../../docs/IMPORT_AND_SELECT_SKILLS.md
- 웹 IDE 저장 문제: 기존 web-ide-terminal-bridge 또는 saved-file-reconciliation Skill
- 현재 규칙과 근거 수준: ../../../docs/COFA_2026_BRIEF.md
- 사전 설명 연습: ../../../docs/NO_AI_REHEARSAL.md

## 보고

구현한 필수 기능, 실제 수정 파일, 관측한 근거, NOT_RUN, 미완료와 다음 행동을 짧게 적는다. 소스 작성·실행·제출 완료를 같은 상태로 보고하지 않는다.

## Notion 심화 자료 선택

전체 소스 안에서만 아래 문서 경로를 사용한다. 개별 Skill ZIP만 있을 때는 이 본문의 독립 흐름으로 진행하고 없는 참고 문서를 찾느라 멈추지 않는다.

- 처음 배우는 참가자: ../../../docs/EXAM_CORE.md
- 담당자 답이 구현을 바꿔야 할 때: ../../../docs/STAKEHOLDER_QUESTIONS.md
- 단계별 작은 지시: ../../../docs/DELEGATION_PROMPTS.md
- 근거 수준·저장·오류: ../../../docs/EVIDENCE_AND_RECOVERY.md
- 제출과 최종 완료 구분: ../../../docs/SUBMISSION_AND_INCIDENTS.md
