# 합성 모의 의뢰: 지역 문화센터 주간 강좌 배정

> 합성 연습 자료, 실제 대회 문제·업무 데이터 아님. 수강생 이름·모임·강좌는 모두 가상입니다.

> 동네 문화센터는 매주 강좌 신청을 받아 운영자가 손으로 수강생을 배정하고 있습니다.
> 배정에 시간이 오래 걸리고, 원하는 강좌에 못 들어갔다는 불만도 많습니다.
> 수강생은 자기가 낸 신청과 배정 결과를 직접 확인하고 싶어 합니다.
> 운영자는 강좌 정원과 시간대 겹침을 관리하면서 배정을 실행하고, 필요하면 손으로 조정하고 싶어 합니다.
> 이 일을 돕는 작은 도구를 만들어 주세요.

제공 자료는 [participants.csv](participants.csv)(수강 신청)와 [sessions.csv](sessions.csv)(강좌 목록)뿐입니다. 두 CSV의 이름·모임·강좌도 모두 가상 값입니다. 배정 규칙, 우선순위, 데이터 정제 기준, 화면 형태는 **전달되지 않았습니다.** 담당자에게 묻지 않은 내용을 AI가 임의로 채우지 않게 합니다.

## 할 일

1. **질문 원장**: 담당자(문화센터 운영 책임자)에게 물을 질문을 원장에 쌓습니다. 담당자 역할은 [FACILITATOR.md](FACILITATOR.md)를 든 진행자나 별도 AI가 맡습니다. 담당자는 특정 열·값·경계·사례를 지목한 구체 질문에만 답합니다. 질문 수 제한은 없으니 엣지 케이스, 애매한 값, 두 파일 사이의 차이를 하나씩 물으세요.
2. **역할 매트릭스**: 수강생과 운영자가 각각 무엇을 보고 무엇을 할 수 있는지, 무엇을 보면 안 되는지 표로 나눕니다.
3. **정제 로그**: 원 행 수, 제거·변환한 행과 이유, 정제 후 수치를 남깁니다. 원 식별자는 유지합니다.
4. **정식화 카드**: 결정 변수, 목적, 하드 제약, 소프트 기준, 동점 처리를 한 장에 적습니다.
5. **기준선 → 개선 알고리즘**: 단순 기준선(신청시각이 빠른 수강생부터 한 명씩, 그 사람의 희망 순서대로 가능한 만큼 배정)을 먼저 만들고, 직접 고른 개선 방법과 목적값·제약 위반 수를 비교합니다.
6. **비용 기록**: 에이전트 호출 횟수, 큰 재작업, 불필요하게 다시 읽은 자료를 기록하고 줄일 방법을 한 줄로 남깁니다.

## 연결 자료

- 질문: [stakeholder-agent-questioning](../../.agents/skills/stakeholder-agent-questioning/SKILL.md), [QUESTION_LEDGER.csv](../../templates/QUESTION_LEDGER.csv), [question_ledger.py](../../tools/question_ledger.py)
- 역할 분리: [role-separated-design](../../.agents/skills/role-separated-design/SKILL.md), [ROLE_MATRIX.md](../../templates/ROLE_MATRIX.md)
- 최적화: [optimization-modeling](../../.agents/skills/optimization-modeling/SKILL.md), [opt_kit.py](../../tools/opt_kit.py)
- 비용: [cost-aware-execution](../../.agents/skills/cost-aware-execution/SKILL.md)

먼저 진짜 문제 한 문장, 첫 질문 5개, 수강생·운영자 각각의 필수 기능 2개를 적으세요. 그다음 질문을 시작합니다. 완성 답안과 정답 코드는 제공하지 않습니다.
