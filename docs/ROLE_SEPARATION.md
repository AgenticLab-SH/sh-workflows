# 역할 분리 설계 패턴

과제에 사용자 유형이 둘 이상일 때(이용자/운영자, 신청자/승인자 등) 화면·데이터·권한·흐름을 나누는 준비용 패턴입니다. 아래 사례는 모두 합성 예시이며 실제 평가 과제와 관계가 없습니다. 공식 규칙과 과제 지시가 우선이고, 역할 정의와 공개 범위는 참가자와 담당자가 결정합니다.

실행 흐름은 [role-separated-design Skill](../.agents/skills/role-separated-design/SKILL.md), 빈 양식은 [역할 매트릭스](../templates/ROLE_MATRIX.md)에 있습니다.

## 1. 흐름 요약

1. 요구 문장·데이터 컬럼에서 누가 입력·결정·조회·수정하는지 찾는다. 불명확하면 담당자에게 묻는다.
2. 역할 × 목표/진입점/보기/수정/행동/결과로 매트릭스를 만든다.
3. 공용 원천 데이터 하나와 역할별 파생 뷰를 정한다.
4. 처리 함수·API에서 역할 값과 행 소유자를 검사해 권한을 강제한다.
5. 상태 전이와 전이 주체, 이용자 뷰 반영 시점을 정한다.
6. 순수 핵심 로직과 역할별 어댑터를 나눈다.
7. 과제 요구와 남은 시간으로 구현 형태를 고른다.
8. 역할별 허용/거부·누출·일관성·잘못된 역할을 테스트한다.
9. 역할별 한 줄 시나리오와 설계 이유로 설명한다.

## 2. 사례 비교

### 사례 A: 문화센터 강좌 (수강생 / 운영자)

| 항목 | 수강생 | 운영자 |
| --- | --- | --- |
| 목표 | 원하는 강좌를 신청하고 확정 결과 확인 | 정원에 맞게 수강생을 확정하고 일정 변경 공지 |
| 진입점 | `/learner` 화면 또는 `apply`, `cancel`, `my-status` 명령 | `/operator` 화면 또는 `allocate`, `change` 명령 |
| 볼 수 있는 데이터 | 강좌 목록·남은 자리, 본인 신청·확정 상태 | 전체 신청 목록, 강좌별 인원, 내부 메모 |
| 바꿀 수 있는 데이터 | 본인 신청(배분 실행 전까지 취소 가능) | 확정 결과, 강좌 정원·시간, 내부 메모 |
| 행동 | 신청, 취소, 결과 조회 | 정원 배분 실행, 확정, 변경 |
| 결과·알림 | 확정·변경 시 본인 상태 문구 갱신 | 배분 결과 요약(확정 수·대기 수) |

### 사례 B: 도서관 좌석 (이용자 / 관리자)

| 항목 | 이용자 | 관리자 |
| --- | --- | --- |
| 목표 | 빈 좌석을 예약하고 본인 예약 확인 | 좌석 상태 관리, 장기 미사용 예약 정리 |
| 진입점 | `/seats` 화면 또는 `reserve`, `release`, `my-reservation` 명령 | `/admin` 화면 또는 `force-release`, `block-seat` 명령 |
| 볼 수 있는 데이터 | 좌석별 빈/사용 중 여부, 본인 예약 | 좌석별 예약자, 이용 시간, 정리 이력 |
| 바꿀 수 있는 데이터 | 본인 예약 생성·반납 | 좌석 사용 불가 지정, 예약 강제 해제 |
| 행동 | 예약, 연장, 반납 | 해제, 좌석 차단, 이용 현황 조회 |
| 결과·알림 | 강제 해제 시 본인 예약 상태가 "해제됨"으로 바뀜 | 정리된 예약 수와 사유 |

두 사례 모두 이용자는 **다른 사람이 누구인지** 볼 필요가 없습니다. 이용자 뷰에는 "남은 자리"나 "사용 중" 같은 집계·상태만 보입니다. 이용자가 기존 행을 바꾸는 동작(사례 A의 `cancel`, 사례 B의 `release`(반납)·연장)은 그 행의 소유자가 요청자일 때만 허용합니다.

## 3. 최소 데이터 모델 예 (사례 A)

공용 원천 테이블은 파일(CSV/JSON) 하나여도 충분합니다. 과제가 요구하지 않으면 DB를 추가하지 않습니다.

| 공용 테이블 `enrollments` 필드 | 수강생 뷰 | 운영자 뷰 |
| --- | --- | --- |
| `enrollment_id` | 본인 것만 보기 | 보기 |
| `class_id` | 본인 것만 보기 | 보기·수정 |
| `learner_id` | 숨김(요청 주체로만 사용) | 보기 |
| `learner_name` | 숨김 | 보기 |
| `contact` | 숨김 | 마스킹(`010-****-1234`) |
| `status` | 본인 것만 보기 | 보기·수정 |
| `priority_score` | 숨김 | 보기 |
| `memo_internal` | 숨김 | 보기·수정 |

`classes` 테이블의 `capacity`는 수강생에게 그대로 보여 주지 않고 `remaining_seats`(정원 − 확정 수)라는 파생 값으로 보여 줍니다.

## 4. 권한 강제 의사 코드

```python
import re

ROLES = {"learner", "operator"}          # 정확히 이 소문자 값만 허용
ALLOWED = {
    "apply":     {"learner"},
    "cancel":    {"learner"},
    "my_status": {"learner"},
    "allocate":  {"operator"},
    "change":    {"operator"},
}
OWNED_ACTIONS = {"cancel"}               # 기존 행을 바꾸는 이용자 동작: 행 소유자 검사

def handle(action, ctx, payload, store):
    role = ctx.role                      # 화면·CLI에서 선택된 역할(데모용, 실제 인증 아님)
    requester_id = ctx.user_id           # 선택된 세션 맥락에서만 받는다
    if role not in ROLES:                # "Operator", " operator", "" 모두 거부
        raise PermissionError("unknown role")
    if role not in ALLOWED.get(action, set()):
        raise PermissionError(f"{role} cannot {action}")
    if role == "learner":
        payload = {**payload, "learner_id": requester_id}   # 본문에 넣은 ID는 무시하고 덮어씀
        if action in OWNED_ACTIONS:
            row = store.get(payload.get("enrollment_id"))
            if row is None or row["learner_id"] != requester_id:
                raise PermissionError("not your enrollment")
    result = CORE[action](payload, store)  # 역할을 모르는 순수 로직
    return to_view(role, result, requester_id)

def mask_contact(contact):
    m = re.fullmatch(r"(\d{2,3})-\d{3,4}-(\d{4})", contact or "")
    return f"{m[1]}-****-{m[2]}" if m else "****"   # 형식이 다르면 전부 가림

def to_view(role, rows, requester_id):
    if role == "operator":               # 데이터 모델 표대로 운영자에게도 연락처는 마스킹
        return [{**r, "contact": mask_contact(r.get("contact"))} for r in rows]
    mine = [r for r in rows if r["learner_id"] == requester_id]
    return [{k: r[k] for k in ("enrollment_id", "class_id", "status")} for r in mine]
```

`ctx`는 화면의 역할 선택이나 CLI의 `--role`·`--user` 옵션에서 만든 값입니다. 데모용 선택이며 실제 인증이 아닙니다. 화면과 README에 그 사실을 적습니다. 요청 본문(`payload`)의 `learner_id`·`requester_id`로 본인을 판별하지 않습니다. 사례 B의 이용자 `release`(반납)와 연장도 `OWNED_ACTIONS`에 넣어 같은 검사를 받습니다. 무거운 `allocate`는 운영자 동작에서 한 번 실행하고 결과를 저장하며, `my_status`는 저장된 결과만 읽습니다.

## 5. 테스트 표

| 번호 | 역할 | 동작 | 기대 결과 |
| --- | --- | --- | --- |
| T1 | 수강생 | `apply` | 성공, 상태 `requested`, 행의 `learner_id`는 `ctx.user_id` |
| T2 | 수강생 | `allocate` | `PermissionError` |
| T3 | 수강생 | `my_status` | 본인 행만, `learner_name`·`contact`·`priority_score`·`memo_internal` 키 없음 |
| T4 | 수강생 | 본문에 다른 사람 `learner_id`를 넣고 `my_status` | 본인 행만 나옴 |
| T5 | 수강생 | 다른 사람 `enrollment_id`로 `cancel` | `not your enrollment` 거부, 행은 그대로 |
| T6 | `""`, `admin`, `Operator`, `" operator"` | 아무 동작 | `unknown role` 거부(소문자 `learner`·`operator`만 허용) |
| T7 | 운영자 | `allocate` 후 수강생 `my_status` | 확정 결과가 저장값과 같음 |
| T8 | 운영자 | `change`로 강좌 변경 | 다음 수강생 조회에 변경 반영, 다른 수강생 행은 그대로 |
| T9 | 운영자 | 신청 목록 조회 | `contact`가 `010-****-1234` 형식, 원본 번호 없음 |
| T10 | 이용자(사례 B) | 다른 사람 예약 `release` | `PermissionError`, 예약은 그대로 |
| T11 | 관리자(사례 B) | 좌석 차단 후 이용자 좌석 조회 | 해당 좌석이 예약 불가로 표시 |

역할 값은 정확히 소문자 `learner`·`operator`만 허용합니다. 대문자 변환이나 앞뒤 공백 제거로 보정하지 않으므로 T6의 네 값은 모두 거부됩니다. 담당자가 다른 규칙을 정하면 이 문단과 T6을 함께 바꿉니다. 현재 정책이 허용하지 않는 검사는 NOT_RUN으로 기록합니다.

## 6. 체크리스트

- [ ] 요구 문장과 컬럼에서 역할을 모두 찾았고 근거 문장을 적었다.
- [ ] 불명확한 역할·공개 범위는 담당자 답변으로 확정했다.
- [ ] 역할 매트릭스에 빈 칸이 없다.
- [ ] 이용자 흐름과 운영자 흐름이 둘 다 끝까지 동작한다.
- [ ] 공용 원천 데이터는 한 곳이고 역할별 뷰는 파생으로 만든다.
- [ ] 이용자 응답에 타인 정보와 운영자 전용 필드가 없다.
- [ ] 운영자 응답도 데이터 모델 표의 마스킹 규칙을 따른다.
- [ ] 권한은 처리 함수·API에서 역할 값으로 검사한다.
- [ ] 요청자 ID는 선택된 역할·세션 맥락에서 받고, 이용자의 기존 행 변경은 행 소유자를 검사한다.
- [ ] 잘못된 역할 값은 거부한다.
- [ ] 데모용 역할 선택에 "실제 인증 아님"을 표시했다.
- [ ] 상태 전이마다 전이 주체와 조건이 있고, 금지 전이를 막는다.
- [ ] 운영자 변경이 이용자 뷰에 반영되는 시점을 정하고 확인했다.
- [ ] 무거운 계산은 운영자 동작에서 실행·저장하고 이용자는 조회만 한다.
- [ ] 과제가 요구하지 않은 로그인·DB·서버를 추가하지 않았다.
- [ ] 역할별 한 줄 시나리오와 설계 이유를 설명할 수 있다.

## 7. 담당자에게 물을 질문 예

질문 진행은 stakeholder-agent-questioning Skill이 있으면 그쪽을, 없으면 stakeholder-interview Skill을 따릅니다. 질문 하나에는 사실 하나와 물음표 하나만 넣고, 예/아니오·수치·선택지로 답할 수 있게 씁니다. 사람 담당자에게는 2~3개씩 묻습니다. 구체 질문에만 답하는 무제한 담당자 에이전트에게는 질문 하나에 사실 하나로 모두 묻고, 한 번에 보낼 묶음 크기는 반응을 보고 정합니다.

1. 수강생이 다른 수강생의 신청 내역을 볼 수 있나요?
2. 수강생 화면에는 정원 숫자 대신 "남은 자리"만 보여 주면 되나요?
3. 운영자가 확정한 뒤에도 결과를 바꿀 수 있나요?
4. 확정 후 변경이 생기면 수강생 화면의 상태 문구만 바꾸면 되나요?
5. 수강생은 운영자가 배분을 실행하기 전까지만 신청을 취소할 수 있나요?
6. 운영자는 한 명으로 가정해도 되나요?
7. 내부 메모는 수강생 화면에서 완전히 숨기면 되나요?
8. 우선순위 점수도 수강생 화면에서 완전히 숨기면 되나요?
9. 운영자 화면의 연락처는 가운데 자리를 가린 `010-****-1234` 형식이면 되나요?
10. 운영자 변경은 수강생 화면에 즉시 반영해야 하나요?
11. 신청자와 승인자가 같은 사람일 수 있나요?
12. 본인 신청을 본인이 승인하는 것은 막아야 하나요?
13. 이번 범위에서는 실제 로그인 없이 역할 선택으로 시연해도 되나요?

## 8. 하지 않는 것

- 과제가 요구하지 않는 인증 서버·토큰·DB 권한 체계를 만들지 않습니다.
- 실제 과제 데이터·문구를 이 문서나 공개 저장소에 옮기지 않습니다.
- 과제 데이터 외부 전송, 감독 시험 중 Git Push, 캡처·GUI 자동화는 금지입니다.
