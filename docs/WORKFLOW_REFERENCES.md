# 공개 워크플로우·평가 참고 색인
2026-10-31 공개 GitHub 메타데이터와 아래 예제 경로를 확인했다. 원문 전체·실행 결과를 재검증한 것은 아니다.
패턴 참고용이며 외부 API·유료 서비스·SDK 설치를 시험에서 허용한다는 뜻이 아니다. 코드를 복제하지 않았다.

| 출처 | 목적 / 적용 조건 | 검증 방법 | 라이선스 / 재사용 한계 |
| --- | --- | --- | --- |
| [OpenAI Cookbook evaluation](https://github.com/openai/openai-cookbook/tree/main/examples/evaluation) | 평가 반복: 기대 사례→실패 분류→작은 수정. 정답 또는 평가 기준이 있어야 함 | 고정 합성 사례와 별도 검증 사례 비교; 실제 실행한 것만 기록 | 저장소 MIT 확인. 개별 데이터·외부 의존 조건 별도 확인; API 예제는 시험에서 실행하지 않음 |
| [OpenAI Agents SDK patterns](https://github.com/openai/openai-agents-python/tree/main/examples/agent_patterns) | 역할 분리·단계 조합 패턴. 단일 스크립트로 부족한 근거가 있을 때만 | 단계별 입력/출력·실패 경로·사람 승인 검사 | 저장소 MIT 확인. 현재 예제별 조건 확인 후 재사용; 여러 Agent 도입 권고가 아님 |
| [OpenAI Evals](https://github.com/openai/evals) | 평가 사례와 채점 기준을 분리하는 설계 참고 | 정상·경계·실패 사례, 지표 한계와 재현 가능성 확인 | API 라이선스 NOASSERTION, LICENSE 경로 404: 라이선스 미확인. 코드·데이터 복제 보류, 링크 색인만 제공 |

시간이 부족하면 첫 번째의 평가 반복 원칙만 현재 과제의 로컬 테스트에 적용한다.
기존 연구 원칙은 [RESEARCH_METHODS.md](RESEARCH_METHODS.md)에 유지한다.
