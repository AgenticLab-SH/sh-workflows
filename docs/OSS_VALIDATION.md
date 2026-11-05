# 선택형 OSS 로컬 인수 기록

2026-11-03, 준비용 합성 흐름에 한정한 관측이다. [채택·버전·라이선스·명령·복구](OSS_ADOPTION.md)가 제품 사용 정본이다. 이전 172개 전체 검사 결과를 이번 단위의 전체 검사로 재사용하지 않았다.

| 항목 | 실제 결과 |
| --- | --- |
| 초기 격리 설치 | `.local/oss-integration/venv`, Python 3.13.15, system-site-packages=false. Hypothesis 6.170.14 + sortedcontainers 2.4.0 설치 readback·pip check 통과 |
| 별도 깨끗한 설치 | 정식 설치기 `tools/Install-PropertyChecks.ps1 -EnvironmentName acceptance-venv`로 새 `.local/oss-integration/acceptance-venv` 생성. `--no-index --require-hashes --only-binary=:all: --no-deps --no-compile` 설치와 pip check 통과 |
| 설치기 재실행 | 기존 venv에서 두 배포가 already satisfied이며 버전 동일. 외부 index 접근 없이 실행 |
| 실제 entrypoint | 두 venv에서 `python -B examples/method_trace.py --property-checks` 성공. 기존 고정 사례와 거절 3사례를 이어 실행하고 속성 검사 추가 |
| 생성·대조 | 60개 생성 입력에서 DP=독립 부분집합, 예산 증가 목적값 비감소, 순열 변경 목적값 동일을 각각 60회 관측 |
| 탐색·축소 | 값 `[1,2]`·비용 `[1,2]`·예산 2. 비율 탐욕 1점, DP/독립 열거 2점. 두 회차 같은 반례(시간 값 제외). 전역 최소 보장은 아님 |
| `test_property_integration.py` | 4 tests OK: entrypoint E2E·동일 반례 재실행, network/subprocess 거절, observability 환경 거절, 미검토 버전 거절 |
| `test_method_trace.py` | 3 tests OK: 기존 반례/경계, 작은 변경 입력 40개 대조, 단위/자원 거절 |
| `test_kit_integration.py` | 6 tests OK: 41개 스킬·색인·입구·상대 링크 등 |
| 의존성 없음 | 새 venv의 `python -S -B examples/method_trace.py --property-checks`는 exit 2 및 optional dependencies absent 출력 |
| 기본 모드 복구 | `python -S -B examples/method_trace.py`는 외부 의존성 없이 passed=true |
| 외부 입력 거절 | 지원하지 않는 `--input actual-task.json` 옵션은 파일을 읽지 않고 exit 2 |
| 설치 손상 거절 | 별도 합성 fixture에 텍스트를 wheel 이름으로 놓고 정식 설치기를 실행. hash mismatch로 중단, venv 미생성 확인 |
| 무결성·문법 | 두 wheel·해당 소스 압축본 SHA-256 대조. 설치기 PowerShell 파싱과 `git diff --check` 통과 |

개인 절대 경로·설치 출력 원문·JSON·선행 dirty 보존용 복구 사본은 `.local/oss-integration/`에 둔다. 처음 변경 시점의 전체 스냅샷은 만들지 않았으므로 일부 기존 파일의 복구 사본은 이번 추가문구를 역으로 제거한 **내용 복구용 재구성본**이다. 이를 사전 시각의 바이트 동일 원본이라고 주장하지 않는다. 복구 전 현재 변경과 대조하고 타인의 이후 변경을 덮어쓰지 않는다.

NOT_RUN: 이번 단위 전체 소스 테스트 재실행, 실제 평가 UI·공식 규칙 적합성·실제 과제 데이터, 사용자 Q&A·설명 능력, 다른 OS/Python 설치, 취약점 전수 감사, OS 수준의 모든 통신 차단 검증, 공개 push·릴리스·기존 패키지 재생성. 설치·실행 성공은 시험 허용이나 전체 해커톤 준비 완료를 뜻하지 않는다.

기록 파일 점검 중 복구 사본의 .md 확장자를 상대 링크 검사기가 제품 문서로 읽어 한 번 실패했다. 제품 링크 자체 오류는 아니었으며 복구 사본을 .md.preimage.txt로 보존한 뒤 동일한 문서 검사 6개가 통과했다.
