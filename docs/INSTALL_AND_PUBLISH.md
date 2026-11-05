# 가져오기·패키지·게시 상태

현재 저장소: https://github.com/AgenticLab-SH/sh-workflows

## 평가 환경에서 사용

[가져오기·선택](IMPORT_AND_SELECT_SKILLS.md)을 따릅니다. 공개 Clone이 허용될 때 참고 폴더로 가져오고 필요한 Skill만 읽습니다. 개인 인증, Git Push, Codex 업데이트가 필요하지 않습니다.

## 개인 준비 환경의 다운로드

[릴리스](https://github.com/AgenticLab-SH/sh-workflows/releases)에는 전체 소스 ZIP, 개별 Skill ZIP 묶음, 각 Skill ZIP을 제공합니다. 새로 패키징한 파일이며 원 대화의 ZIP·Git 번들을 회수한 것은 아닙니다. ZIP 생성은 동작 검증이 아닙니다.

개별 Skill ZIP은 루트의 SKILL.md와 agents/openai.yaml을 포함합니다. 소스 전체 ZIP을 단일 Skill로 등록하지 않습니다. 실제 업로드/발견 지원은 사용 환경의 공식 UI에 따릅니다.

릴리스 파일 이름(v0.5.0부터): `sh-workflows-v0.5.0-source.zip`(Git이 추적하는 파일 전체), `sh-workflows-v0.5.0-skills.zip`(개별 Skill ZIP 41개 묶음), `<skill-name>.zip`(Skill 하나). 각 파일의 SHA-256은 릴리스 설명에 적습니다. 릴리스 페이지에 해당 버전이 보이기 전에는 main을 사용합니다.

## 소유자 개발 환경에서 후속 게시

이 절은 시험 환경 밖의 저장소 소유자용입니다. 기존 저장소와 이력을 보존하고 새 커밋을 게시합니다. 다른 프로젝트를 이 저장소로 덮어쓰거나 강제 Push하지 않습니다. 시험 규칙상 공개 유지 기간이 있다면 그 기간 동안 Public을 유지합니다.

원본 Git 번들은 회수하지 못했습니다. 현재 게시 이력은 GitHub에서 Clone할 수 있으나 이를 과거 원번들 복원이라고 부르지 않습니다.

## 현재 한계

로컬 합성 테스트(`python -B -m unittest discover -s tests`)는 CHANGELOG 최신 항목의 결과를 따릅니다. 빌드·린트·타입·브라우저·Cofa 사용 검증은 수행하지 않았습니다. 과거 대화에 나온 테스트 통과 수치를 현재 릴리스에 붙이지 않습니다. 자동 검사 workflow는 포함하지 않습니다.

## 로컬 보강 패키지와 게시의 구분

새 사전 학습 보강의 로컬 패키지는 `.local/packages/` 아래에만 준비한다. 기존 공개 릴리스를 교체하거나 최신 main에 게시됐다고 주장하지 않는다. 실제 포함 항목·검사 결과는 [연결 검증 기록](METHOD_TRACE_VALIDATION.md)에 적는다.

로컬 개별 Skill ZIP은 `SKILL.md`, `agents/openai.yaml`, 키트 `LICENSE` 외에 해당 Skill의 `references/`가 있으면 함께 담는다. 전체 소스용 `../../../docs` 참조는 개별 ZIP 안에 없으므로 본문의 독립 절차를 사용한다. ZIP 파일이 만들어져도 환경의 Skill 등록·동작·공식 반입·제출 승인이 된 것은 아니다. 로컬 소스 ZIP에는 확인한 준비 자료만 담고 `.git`, `.local`, 인증·개인 원본·실제 과제 데이터는 담지 않는다.
선택형 OSS 반례 연습은 별도 [채택·격리 설치·복구 안내](OSS_ADOPTION.md)를 따른다. 새 의존성은 공개 소스 ZIP에 내장하지 않으며, 이전 로컬 패키지 43개도 재생성하지 않았다. 현재 소스의 새 옵션과 이전 패키지 스냅샷을 구분한다.