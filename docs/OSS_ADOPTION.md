# 선택형 OSS: 합성 반례 탐색·축소

사전 준비용 소스와 실제 설치를 구분한다. 이 기능은 기존 합성 예제의 선택형 확장이다. 실제 평가자료를 읽지 않으며 사용자 답변·이해 점수·금지 단계 메모를 만들지 않는다. 최신 공식 규칙에서 공개 의존성 반입·설치·실행을 허용하는지는 **미확인**이다. 로컬 설치 성공은 시험 허용 증거가 아니다. 실제 AI 금지 단계에는 실행·지원하지 않는다.

## 무엇이 추가됐나

기존 고정/난수 합성 검사는 유지한다. Hypothesis가 한정된 입력을 생성하고, 잘못된 주장에 맞는 반례를 탐색·축소한다. 이를 기존 질문 Q02(효율과 총효과의 충돌), Q03(쪼개기), Q09(반복), Q10(의존성)→결정 D02→두 함수→실제 반례로 잇는다. 업무 규칙을 자동으로 확정하거나 자연어 설명을 대신 작성하지 않는다.

[방법→설명 연습](METHOD_TO_EXPLANATION.md)과 같은 입력/함수를 사용한다. 새 실행 옵션만 `examples/method_trace.py --property-checks`에 추가했다. 기본 명령은 계속 표준 라이브러리만 쓴다.

## 후보·채택 원장

공식 저장소·원문과 PyPI 배포 메타데이터를 2026-11-03 확인했다. 최신이라는 이유로 기능을 자동 활성화하지 않는다. 확인한 배포 버전을 고정한다.

| 후보·정확 버전 | 공식 근거·라이선스 | 적합성·설치/보안 비용 | 결정 |
| --- | --- | --- | --- |
| Hypothesis 6.170.14 | [공식 GitHub](https://github.com/HypothesisWorks/hypothesis), [배포 원문](https://pypi.org/project/hypothesis/6.170.14/), [Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html), [API의 find/settings](https://hypothesis.readthedocs.io/en/latest/reference/api.html), [전략·축소](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html). MPL-2.0; wheel의 LICENSE.txt와 메타데이터 직접 확인 | 입력 생성·반례 축소가 기존 수동 난수 검사에 빠진 기능. Windows CPython 3.13 wheel 690,983 B + 의존성 29,575 B. 선택 extras·원격 서비스 없음 | 채택. 정확 배포+SHA-256으로 식별. Git 태그 API는 404여서 commit을 추정하지 않음 |
| sortedcontainers 2.4.0 | [공식 GitHub](https://github.com/grantjenks/python-sortedcontainers), [정확 배포](https://pypi.org/project/sortedcontainers/2.4.0/). Apache-2.0 | Hypothesis의 유일한 필수 의존성. pure Python wheel. 추가 필수 의존성 없음 | 동반 채택, 2.4.0 고정 |
| pytest 9.2.0 | [공식 GitHub](https://github.com/pytest-dev/pytest), [정확 배포](https://pypi.org/project/pytest/9.2.0/). MIT | Windows에서 colorama와 iniconfig/packaging/pluggy/pygments 필요. unittest 실행과 겹치며 자체 반례 생성·축소 없음 | 미채택·미설치·실행 NOT_RUN. 품질 문제나 보안 거절이 아니라 이번 기능에 추가 이점이 작음 |
| jsonschema 4.26.0 | [공식 GitHub](https://github.com/python-jsonschema/jsonschema), [정확 배포](https://pypi.org/project/jsonschema/4.26.0/). MIT | attrs/jsonschema-specifications/referencing/rpds-py 필요. 형식 검증에 적합하지만 이번 목표는 알고리즘 반례. 원격 참조는 별도 통제 필요 | 미채택·미설치·실행 NOT_RUN. 기존 JSON 도구를 큰 체계로 교체하지 않음 |

사전 검토한 Hypothesis 6.131.9는 순수 Python wheel이지만 attrs와 구형 Python의 exceptiongroup 의존성까지 필요했다. 실제 설치하지 않았고, 현재 호스트에 맞는 검토 버전 6.170.14를 채택했다. 이것을 보안 차단 우회나 구버전으로 제한 우회한 것으로 취급하지 않는다. 취약점 전수 감사는 NOT_RUN이며 해시/라이선스 검토만으로 무결점이라 주장하지 않는다.

## 잠금·원본·귀속

실제 호출: `tools/property_checks.py`에서 공식 `given`, `settings`, `find`, `strategies`를 import한다. 알고리즘은 기존 `tools/opt_kit.py`를 그대로 호출한다. OSS 구현 복사·변형 없음. 코드 API를 쓰는 glue와 두 원본 라이선스만 소스에 포함한다.

Windows CPython 3.13 x64 전용 [설치 잠금](../requirements-property-win-py313.lock), [정확 다운로드 URL·크기·해시](../dependencies/property-wheels-win-py313.json), [귀속/NOTICE와 라이선스](../third_party/NOTICE.md)를 영구 보관한다. 원본 wheel에서 LICENSE를 복사했고 별도 NOTICE 엔트리는 없었다. 다른 배포/버전에는 그 NOTICE도 보존해야 한다. Hypothesis MPL-2.0 파일을 키트 MIT로 바꾸지 않는다.

| 배포 파일 | SHA-256 |
| --- | --- |
| hypothesis-6.170.14-cp313-cp313-win_amd64.whl | `03831d833b161b9b7a32f0b607205293954f3a651196c80138804b9479845d71` |
| sortedcontainers-2.4.0-py2.py3-none-any.whl | `a163dcaede0f1c021485e957a39245190e74249897e2ae4b2aa38595db237ee0` |
| [hypothesis-6.170.14.tar.gz 원본 소스](https://files.pythonhosted.org/packages/d6/0f/10b2076a1314c554eee58c26e1dbe630fd26a32773df2a63bd5dba5d9947/hypothesis-6.170.14.tar.gz) | `8272913eb34c4399a88cf8a9ecdb351c9ef8f621c061f2ac323362d4a66b755d` |
| [sortedcontainers-2.4.0.tar.gz 원본 소스](https://files.pythonhosted.org/packages/e8/c4/ba2f8066cceb6f23394729afe52f3bf7adec04bf9ed2c820b39e19299111/sortedcontainers-2.4.0.tar.gz) | `25caa5a06cc30b6b83d11423433f65d1f9d76c4c6a0c90e3379eaa43b9bfdb88` |

wheel과 해당 소스 압축파일은 `.local/oss-integration/`에만 다운로드·해시 대조했다. 공개 Git/package에 자동 포함하지 않는다. 별도 wheelhouse 배포 시 MPL 원본 소스 제공·접근과 원본 고지 의무를 충족해야 한다.

## 설치와 재실행

다음은 **소유자의 허용된 사전 준비 Windows PowerShell**에서 키트 루트 기준으로 실행한다. Python 3.13 x64가 이미 있어야 한다. Python·Codex 업데이트, 전역 pip 설치, 관리자 권한, 모델/계정 설정 변경은 필요 없다. 설치기는 플랫폼이 다르면 거절한다. Linux/다른 Python용 wheel 잠금·설치는 NOT_RUN이며 표준 라이브러리 모드는 유지한다.

```powershell
# 처음 다운로드가 필요할 때만: 고정 공식 wheel 두 개, 해시 대조 후 venv 설치
.\tools\Install-PropertyChecks.ps1 -Download
# 이후 네트워크 없이 같은 설치를 확인/재실행
.\tools\Install-PropertyChecks.ps1
.\.local\oss-integration\venv\Scripts\python.exe -B examples/method_trace.py --property-checks
# 별도 깨끗한 로컬 venv에서 동일 잠금으로 설치 인수
.\tools\Install-PropertyChecks.ps1 -EnvironmentName acceptance-venv
.\.local\oss-integration\acceptance-venv\Scripts\python.exe -B -m unittest discover -s tests -p test_property_integration.py -v
```

오프라인 설치 옵션은 `--isolated --no-index --only-binary=:all: --require-hashes --no-deps --no-compile`이다. 실행기에 pip를 내장하지 않는다. 파일/해시/버전이 틀리거나 의존성이 없으면 명확히 실패하며 몰래 설치하거나 기본 모드로 바꿔 합격시키지 않는다. 손상된 wheel은 교체·재다운로드하기 전 원인을 확인한다.

## 실행 범위와 오류 거절

- 최대 항목 6개·정수 값 0~30·비용 0~15·용량 0~30, 60개 생성 사례에서 DP=독립 부분집합, 예산 증가 시 목적값 비감소, 순열 변경 시 목적값 동일을 확인한다. 각 사례마다 속성 3개를 본 것이며 180개의 독립 입력이라는 뜻은 아니다.
- 잘못된 주장에 대한 탐색은 별도 최대 800회, 항목 2~5개로 제한한다. `find`가 축소한 반례는 전역 최소나 업무상 유일 반례라는 보장이 없다.
- `database=None`, `derandomize=True`, 기본 Hypothesis backend. 새 계정·네트워크/AI·MCP·플러그인 없음. `HYPOTHESIS_NO_PLUGINS=1`은 현재 자식 실행에만 적용한다. 실험 observability 환경은 거절한다.
- Python audit hook으로 socket·subprocess·os.system 시도를 거절한다. Python 감사 이벤트 범위의 회귀 방어이며 OS 샌드박스나 모든 native 통신 차단 증거가 아니다.
- 상수 캐시는 기본 `.hypothesis` 대신 무시되는 `.local/oss-integration/hypothesis-cache`에 둔다. `database=None`도 모든 파일 쓰기를 없애지는 않는다. 출력에는 합성 반례만 포함한다. 첫 실행의 상수 캐시도 같은 `.local` 아래에 보존했다.
- 외부 입력 경로를 받지 않는다. 없는 의존성·틀린 버전·허용하지 않는 옵션은 exit 2. 기존 소수/음수 비용·자원 한계 거절을 이어 쓴다. 본인 답변은 생성하지 않고 `learner_explanation=NOT_RUN`으로 기록한다.

관측 예: 값 `[1,2]`, 비용 `[1,2]`, 예산 2에서 기준선은 첫 항목의 1점, DP와 독립 열거는 두 번째 항목의 2점이었다. 동률 비율에서 입력순으로 선택하는 탐욕에 대한 반례다. 이를 학습 완료로 평가하지 않는다. 사용자는 별도 사전 연습에서 “동률 규칙이 달라져도 다른 반례가 있는가, 쪼개기가 허용되면 모델이 왜 달라지는가”를 자신의 말로 설명한다. 실제 Q&A는 미실시다.

## 제거·복구

기존 기본 예제는 `--property-checks` 없이 실행하면 된다. 전역 환경은 건드리지 않았으므로 원래 명령으로 즉시 돌아간다. 설치 폴더를 보존한 채 선택 기능 사용만 중단해도 된다.

현재 설치 단위 전체를 가역적으로 비활성화하려면 실행 중인 이 예제의 프로세스가 없음을 확인한 뒤 PowerShell에서 정확한 하위 폴더만 이동한다. 이 경로에는 wheel·캐시·두 venv·설치 근거가 함께 있다. 다른 작업 폴더나 사용자 홈을 이동하지 않는다.

```powershell
$kit = (Resolve-Path -LiteralPath .).Path
$target = [IO.Path]::GetFullPath((Join-Path $kit '.local/oss-integration'))
if ($target -ne (Join-Path $kit '.local/oss-integration')) { throw '예상 경로와 다름' }
if ((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw '링크 경로는 중단' }
$archive = Join-Path $kit ('.local/oss-integration-disabled-' + (Get-Date -Format yyyyMMdd-HHmmss))
Move-Item -LiteralPath $target -Destination $archive
# 복구: 설치기가 아닌 정확한 보관 폴더를 원래 위치로 되돌린 뒤 재실행한다.
# venv는 원래 절대 위치에서 사용한다. 보관 위치에서 직접 실행하지 않는다.
```

물리 삭제·전역 uninstall·기존 패키지 재생성은 하지 않는다. 이번 변경 소스를 되돌릴 때는 이전 dirty와 구분해 이번 preimage/patch만 적용한다. 예전 43개 ZIP은 당시 스냅샷이며 이 OSS 보강이 포함됐다고 주장하지 않는다. 이번 단위는 공개 push·새 릴리스·실제 시험환경 검증·전체 준비 완료가 아니다.

실제 설치/실행·거절·검사별 결과는 [로컬 인수 기록](OSS_VALIDATION.md)을 따른다.
