# 준비 자료 전체 길잡이

2026-11-05 통합: 웹에서 개선한 최신 main(`a5ce7a4`)에 기존 로컬의 미게시 준비 소스를 파일별로 합쳤습니다. 기존 로컬 수정본과 설치 환경은 보존했습니다. 이 저장소는 공개 재사용 도구입니다. 실제 평가 자료·개인 원본·응시 링크는 포함하지 않습니다.

## 지금 시작할 곳

1. [안전한 시작](SAFE_WORKROOM_START.md): 정확한 과제 루트 → Clone 전 최초 기록 → 허용된 공개 Clone → 작업실 초기화. 보고 화면 3000 / 과제 서비스 3001.
2. [요구부터 최종 인계까지](DEVELOPMENT_LIFECYCLE.md): 요구·현업 질문·데이터 이해 → 목표·환경·계획 → 위임·세션 인계 → 주요 기능별 대화·보완 → 실제 확인·원인 분석 → 품질 검토·최종 인계.
3. [맥락을 전달한 후 쓰는 시작 프롬프트](../START_PROMPT.md). 현재 필요한 Skill만 선택합니다. 43개를 모두 읽지 않습니다.

## 자료별 반영 위치

| 준비한 것 | 현재 사용할 자료 | 상태·한계 |
| --- | --- | --- |
| 노션 학습 01~18 | [18개 반영표](NOTION_COVERAGE.md), [학습 순서](LEARNING_PATH.md), [핵심 운영서](EXAM_CORE.md) | 기존 공개 재구성본 보존·연결된 노션 반환 내용 대조. 과거 일정은 최신 회차 공지가 아님 |
| 운영진 인터뷰·외부 풀스택 세미나 | [질문법](STAKEHOLDER_QUESTIONS.md), [구조 판단](MVP_DECISIONS.md), [학습 경로](LEARNING_PATH.md) | 개인 전사 전문 복제 없이 원칙·연습에 반영. 공식 규칙·강사 의견·자체 훈련 구분 |
| 논문·공식 근거 13편 + P14 | [연구 목록 14건](RESEARCH_CATALOG.md), [연구를 판단으로 쓰기](RESEARCH_METHODS.md) | 노션의 공개 서지·학습 연결. 이번 통합에서 논문 전문·실험 결과를 새로 검증한 것은 아님 |
| 현업 요구·질문·데이터 분석 | [질문 운영서](STAKEHOLDER_QUESTIONS.md), [질문 멘트](../templates/QUESTION_MESSAGES.md), [요구 연결표](../templates/REQUIREMENT_TRACEABILITY.md), `tools/question_candidates.py` | 가정과 실제 답변을 분리. Windows 한글 출력 수정 포함 |
| 로컬 방법 선택·직접 설명 연습 | [합성 연결 연습](METHOD_TO_EXPLANATION.md), `examples/method_trace.py`, [질문 원장](../examples/method_trace_questions.csv) | 기준선·DP·독립 열거 연결. 질문 10개는 assumed이며 실제 전송·응답 아님 |
| 로컬 설치한 반례 생성·축소 | [OSS 채택·설치·복구](OSS_ADOPTION.md), [과거 로컬 인수](OSS_VALIDATION.md), 잠금·해시·원본 라이선스 | Hypothesis/sortedcontainers 선택 기능. 환경 자체·wheel·개인 로그를 공개 소스로 복제하지 않음 |
| 합성 모의·설명 훈련 | [모의 A~E](MOCK_EXAMS.md), [짧은 훈련](PRACTICE_COFA.md), [직접 설명](NO_AI_REHEARSAL.md) | 사용자 수행·이해 완료와 자료 구축은 별도 |
| 웹 지피티의 작업실 개선 | [시작](SAFE_WORKROOM_START.md), [보고 규약](WORKROOM_REPORTING_STANDARD.md), `tools/workroom.py`, `tools/workroom_ui.html` | L0~L4 근거 계층, 실제 관측 PASS, 사람의 결정·에이전트 제안 구분 유지 |
| 코드 품질·멀티세션·최종 인계 | [개발 전 과정](DEVELOPMENT_LIFECYCLE.md), [세션 인계 양식](../templates/AGENT_HANDOFF.md) | 기존 작업실에 계획·주요 단계 검토·품질·최종 인계 문서 추가. 같은 파일은 한 작성자 |
| 개인 포트폴리오·경험·원 첨부 | 개인 원본 보존 | 이 공개 키트에는 원본을 복제하지 않음. 과거 원 PDF/TXT 미회수 상태를 임의로 완료 처리하지 않음 |

## 최신 사용·검사 상태

최신 소스는 main을 사용합니다. 기존 v0.5.0 릴리스 ZIP은 당시 41개 Skill 스냅샷이며 이번 통합본이 아닙니다. [이번 통합·검사 기록](INTEGRATION_20261105.md)을 따릅니다. 로컬 검사·원격 게시·실제 평가 UI·사용자 실습 완료는 별도 상태입니다. 실제 AI 금지 단계에서는 지원을 중단합니다.
