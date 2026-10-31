# 합성 모의 의뢰 E: 벼룩시장 기부 물품 보관 상자 정리

> 합성 연습 자료, 실제 대회 문제·업무 데이터 아님. 물품·묶음·기록은 모두 가상입니다.

> 동네 벼룩시장 운영 모임은 기부받은 물품을 같은 크기의 보관 상자에 나눠 담아 창고에 둡니다.
> 지금은 담당자가 눈대중으로 담아서 상자가 너무 많이 나오고, 같이 팔아야 하는 물품이 흩어지기도 합니다.
> 물품 기록표를 읽어 상자를 적게 쓰는 담기 계획을 만들어 주는 작은 도구가 필요합니다.

제공 자료는 [items.csv](items.csv)(물품 기록) 하나입니다. 상자 한 개의 한도, 함께 담으면 안 되는 물품, 기록의 단위와 중복 처리, 결과 형식은 **전달되지 않았습니다.** 담당자에게 묻지 않은 내용을 AI가 임의로 채우지 않게 합니다.

이 모의는 [모의 D](../session-allocation/BRIEF.md)와 유형이 다릅니다. 사람을 자리에 배정하는 문제가 아니라 크기가 있는 물건을 용기에 나눠 담는 **적재·묶음** 문제이고, 사용자 역할도 담당자 한 명입니다.

## 할 일

1. **질문 원장**: 담당자(벼룩시장 운영 모임 창고 담당)에게 물을 질문을 원장에 쌓습니다. 담당자 역할은 [FACILITATOR.md](FACILITATOR.md)를 든 진행자나 별도 AI가 맡고, 특정 열·값·경계·사례를 지목한 구체 질문에만 답합니다. 데이터에서 보이는 지점은 `tools/question_candidates.py items.csv`로 초안을 뽑을 수 있습니다. 데이터에 드러나지 않는 규칙(상자 한도, 함께 담기 금지, 목적)은 직접 물어야 합니다.
2. **정제 로그**: 원 행 수, 제외·변환한 행과 이유, 정제 후 수치를 남깁니다. 원 식별자는 유지합니다.
3. **정식화 카드**: 결정 변수, 목적, 하드 제약, 소프트 기준, 동점 처리를 한 장에 적습니다.
4. **기준선 → 개선**: 단순 기준선(부피가 큰 물품부터, 넣을 수 있는 첫 상자에 넣기)을 먼저 만들고, 직접 고른 개선 방법과 상자 수·제약 위반 수를 비교합니다. 상자 수의 하한(총량 ÷ 한도 올림)도 함께 계산합니다.
5. **결과**: 상자별 물품 목록과 상자에 넣지 못한 물품 목록을 냅니다.
6. **비용 기록**: 에이전트 호출 횟수, 큰 재작업, 불필요하게 다시 읽은 자료를 한 줄로 남깁니다.

## 연결 자료

- 질문: [stakeholder-agent-questioning](../../.agents/skills/stakeholder-agent-questioning/SKILL.md), [QUESTION_LEDGER.csv](../../templates/QUESTION_LEDGER.csv), [question_candidates.py](../../tools/question_candidates.py), [question_ledger.py](../../tools/question_ledger.py)
- 최적화: [optimization-modeling](../../.agents/skills/optimization-modeling/SKILL.md), [최적화 운영서](../../docs/OPTIMIZATION_PLAYBOOK.md), [opt_kit.py](../../tools/opt_kit.py)
- 비용: [cost-aware-execution](../../.agents/skills/cost-aware-execution/SKILL.md)

먼저 진짜 문제 한 문장, 첫 질문 5개, 필수 출력 2개를 적으세요. 그다음 질문을 시작합니다. 완성 답안과 정답 코드는 제공하지 않습니다.
