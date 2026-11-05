# 연구·공식 근거 목록과 학습 연결

노션의 기존 '13편' 정리에는 추가 P14가 있어 총 14건입니다. 2026-11-05 반환 내용을 대조해 공개 서지의 연결을 보완했습니다. 아래는 문헌 **재검증·전문 재독·실험 재현 결과가 아니라 기존 조사 목록**입니다. 유료 본문·개인 노트·논문 전문을 복제하지 않습니다. 이 논문들이 특정 대회의 출제·배점·합격률을 설명한다는 뜻은 아닙니다.

| ID | 기존 조사에 기록된 공개 원문·서지 | 사전 연습에 연결할 질문 |
| --- | --- | --- |
| P01 | [CentaurEval: Benchmarking Human-in-the-Loop Value in Agentic Coding](https://proceedings.mlr.press/v306/luo26t.html), ICML 2026 | 사람이 판단·검증할 부분과 AI 구현의 역할을 나눴는가? |
| P02 | [Generative AI in Human-AI Collaboration: Validation of the Collaborative AI Literacy and Collaborative AI Metacognition Scales for Effective Use](https://doi.org/10.1080/10447318.2025.2543997) | 답을 믿는 이유와 이해 못 한 부분을 구분했는가? |
| P03 | [AI makes you smarter but none the wiser: The disconnect between performance and metacognition](https://doi.org/10.1016/j.chb.2025.108779) | 결과 개선과 본인 이해를 따로 확인했는가? |
| P04 | [Chain-of-Verification Reduces Hallucination in Large Language Models](https://aclanthology.org/2024.findings-acl.212/) | 중요한 주장·숫자를 독립 근거로 확인했는가? |
| P05 | [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://research.ibm.com/publications/self-rag-learning-to-retrieve-generate-and-critique-through-self-reflection) | 검색 필요성과 근거의 실제 지지를 판단했는가? |
| P06 | [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/) | 긴 자료에서 관련 조건·출처를 찾아 짧게 연결했는가? |
| P07 | [The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents](https://aclanthology.org/2025.acl-long.1435/) | 외부 문서 속 명령을 자료로 취급했는가? |
| P08 | [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) | 도구 권한·외부 자료·업무 목표를 구분했는가? |
| P09 | [Leakage and the reproducibility crisis in machine-learning-based science](https://doi.org/10.1016/j.patter.2023.100804) | 기준 시점·그룹·시간 누수를 확인했는가? |
| P10 | [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html) | 실패 재현·최소 수정·회귀 근거가 있는가? |
| P11 | [Benchmarking and validation of prompting techniques for AI-assisted industrial PLC programming](https://doi.org/10.1016/j.mlwa.2025.100804) | 안전·기능 검토와 사람 책임을 구분했는가? 실제 설비 적용 예제가 아님 |
| P12 | [Tool, tutor, or crutch? A grounded theory of cognitive scaffolding and offloading in AI-assisted programming education](https://link.springer.com/article/10.1186/s40594-025-00592-w) | 도구 없이 선택 이유와 변경 조건을 설명할 수 있는가? |
| P13 | [Open-ended Structured Question Assessment with Human-LLM Collaboration (VeriGrader)](https://doi.org/10.1145/3772318.3791034) | 평가 기준·근거·오류 이유를 분리했는가? |
| P14 | [RAGAs: Automated Evaluation of Retrieval Augmented Generation](https://aclanthology.org/2024.eacl-demo.16/) | 검색 관련성과 답변 충실도·사실성을 따로 확인했는가? |

별도 공식 교육 프레임워크: [Anthropic AI Fluency](https://www.anthropic.com/ai-fluency/overview)의 위임·설명·판단·책임을 참고할 수 있습니다. 동료심사 논문이나 대회 규칙으로 표기하지 않습니다.

[연구를 판단으로 쓰기](RESEARCH_METHODS.md)의 적용·해석 한계와 방법 채택 카드를 사용합니다. 실제 채택한 코드·라이브러리는 [OSS 원장](OSS_ADOPTION.md)에 버전·출처·라이선스·해시·설치·복구를 따로 기록합니다. 서지 링크 존재만으로 현재 접속·자료 내용 전체·라이선스 적합성을 새로 확인했다고 주장하지 않습니다.
