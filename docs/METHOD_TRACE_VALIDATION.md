# 합성 연결 검증 기록

2026-11-02, 로컬 준비 소스·합성 자료만 확인했다. 사용자 답변이나 담당자 질의응답을 실행한 기록이 아니다. 기준 Git 소스는 `c5616c6`이며 아래 보강은 커밋·공개 게시 전 작업 파일이다.

## 실제 실행

| 검사 | 관측 결과 |
| --- | --- |
| `python -B examples/method_trace.py` | 8개 정상·경계 사례의 DP 목적값이 독립 부분집합 열거와 일치. 기준선·DP 모두 예산/중복/합계 위반 0. 잘못된 비용 단위·음수 비용·셀 한계의 3개 입력 거절 확인 |
| 핵심 반례 | 같은 합성 입력에서 기준선 A+B: 비용 30·160점, DP B+C: 비용 50·220점. 절대 개선 60점. 예산을 30으로 바꾸면 두 방법 모두 160점 |
| `python -B tools/question_ledger.py lint examples/method_trace_questions.csv` | 10행, 문제 0건. 전부 `assumed`·전송 횟수 0이며 실제 응답으로 승격하지 않음 |
| `python -B -m unittest discover -s tests -p test_method_trace.py -v` | 3 tests OK. 고정 반례/경계, seed=93의 작은 변경 입력 40개 독립 열거 대조, 잘못된 단위·자원 한계 거절 |
| `python -B -m unittest discover -s tests -v` | Python 3.13.15, 최종 172 tests OK (5.086초). 기존 41개 Skill frontmatter/색인/입구/상대 링크 등 통합 검사 6개 포함 |
| 최초 전체 검사 | 171개 중 기존 질문 생성 CLI의 한글 CSV를 UTF-8로 읽는 검사 1개 오류. Windows 자식 프로세스의 CP949 출력이 원인이었음. `tools/question_candidates.py`의 CLI 출력을 UTF-8로 고정하고 CP949 환경 회귀 검사 추가 후 위 172개 통과 |
| `git diff --check` | 공백 오류 없음 |
| Skill-creator `quick_validate.py` | 실행 시 `ModuleNotFoundError: No module named 'yaml'`. 검사 본체는 NOT_RUN(의존성 없음). 설치하지 않았고 위 기존 구조검사 통과로 범위를 구분 |

재실행 시 시간 값은 달라진다. 한 번의 작은 측정으로 DP와 다른 solver의 속도 우열이나 큰 입력 성능을 주장하지 않는다. 최초 실패·최종 로그와 합성 JSON 출력은 공개 소스가 아닌 `.local/`에 보존한다.

## 로컬 패키지

41개 개별 Skill ZIP과 묶음을 로컬 생성하고 **각 ZIP 내부 모든 엔트리의 SHA-256을 현재 파일과 대조**했다. 각 개별 ZIP에 `SKILL.md`, `agents/openai.yaml`, 키트 `LICENSE`가 있고, research-evidence·short-answer-defense의 새 `references/`도 포함했다. 전체 소스 전용 문서는 개별 ZIP에 없으므로 본문의 독립 절차를 쓴다.

전체 소스 ZIP은 현재 추적 파일과 검토한 새 준비 파일을 담는다. `.git`, `.local`, 바이트코드와 비밀 키 파일은 패키지 목록에서 제외한다. 로컬 패키지 디렉터리·전체 소스 ZIP의 완료 여부·파일 수·해시·엔트리 검증 결과는 별도 `.local/package-receipt.json`에서 확인한다. 소스 패키지는 Git 커밋 스냅샷이나 공식 제출물이 아니다.

## 미실행과 남은 학습

- NOT_RUN: 실제 평가환경·공식 제출·Browser·대형 입력 성능·OR-Tools 실행/설치·새 GitHub push/릴리스·전역 Skill 설치.
- 사용자 직접 설명·꼬리질문·이해 확인과 실제 담당자 Q&A는 미실시. A~E 전체 모의의 완성 구현/사용자 수행과 이 작은 연결 예제의 실행은 별개다.
- 다음 학습은 [혼자 시작하기](METHOD_TO_EXPLANATION.md)에서 사용자 본인이 질문 공백과 후보 선택 이유를 먼저 적고, 설명→반례→조건 변경을 한 번에 하나씩 연습하는 것이다.
- 최신 공식 규칙·허용 자료·검사 범위는 별도 확인 대상이다. 오래된 안내나 합성 가정을 실제 시험의 규칙으로 확정하지 않는다. 실제 AI 금지 단계에는 지원을 중단한다.
