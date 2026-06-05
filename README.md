## 0. SQL 집계 결과 시각화 및 기술 스택
### 시각화
![대시보드 스크린샷](./images/dashboard.png)

### Stack

- **Language:** Python 3.8
- **Database:** MySQL
- **Infra / BI:** Docker Compose, Grafana

## 1. 실행 방법

이 프로젝트는 배치 스크립트를 통해 가상환경 구성, DB 세팅, 초기 데이터 생성을 한 번에 처리합니다.

**1-1. 사전 요구 사항**

- Python 3.8 이상
- Docker 및 Docker Compose 가동 중

**1-2. 실행 명령어**
프로젝트 최상위 디렉터리에서 아래 스크립트를 실행합니다.

**진행 과정:** 가상환경 생성 및 의존성 설치 → DB/Grafana 컨테이너 실행 → 메인 로직(app/main.py) 자동 실행 (데이터 및 로그 생성)

```
setup.bat
```

## 2. 저장소 선정 및 설계

### 2-1. Log Storage: MariaDB

- **선정 이유 (명확한 스키마 구조화):** 단순 파일 저장이 아닌 '필드를 명확히 분리'하라는 요구사항을 충족하기 위해, 정형화된 스키마를 강제할 수 있는 RDBMS를 선택했습니다.
- **Trade-off 고민:** 실제 대규모 서비스의 로그 수집이라면 쓰기 부하와 비정형 데이터 확장을 고려해 NoSQL 파이프라인을 도입했겠지만, 본 과제의 볼륨과 시각화 툴과의 SQL 연동 편의성을 우선하여 MySQL를 채택했습니다.

### 2-2. 스키마 설명

"단일 테이블에 모든 로그를 혼합하면 불필요한 Null 값이 많아지고 쿼리 성능이 저하됩니다. 따라서 트래픽, 결제 퍼널, 환불이라는 비즈니스 도메인별로 테이블을 물리적으로 분리하여 관심사를 명확히 하고, 시각화 시 쿼리 조회 효율을 높였습니다."

### 2-3. 주요 데이터 스키마

로그 데이터의 특성을 고려하여, 트래픽/결제/환불 도메인별로 테이블을 분리하여 설계했습니다.

1. 트래픽 및 유입 로그 (traffic_logs)
  
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | PK / INT | 로그 고유 ID |
| `timestamp` | DATETIME | 이벤트 발생 시간 |
| `session_id` | VARCHAR | 유저 세션 식별자 (퍼널 분석용) |
| `user_id` | VARCHAR | 유저 식별자 |
| `event_type` | VARCHAR | 이벤트 타입 (예: `COURSE_VIEW`) |
| `course_id` | VARCHAR | 조회한 강의 ID |
| `course_fee` | INT | 강의 가격 (유/무료 구분용) |
| `is_main_exposed` | BOOLEAN | 메인 화면 노출 여부 |

2. 결제 퍼널 및 에러 로그 (payment_logs)
   
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | PK / INT | 로그 고유 ID |
| `timestamp` | DATETIME | 이벤트 발생 시간 |
| `session_id` | VARCHAR | 유저 세션 식별자 |
| `user_id` | VARCHAR | 유저 식별자 |
| `event_type` | VARCHAR | 이벤트 타입 (예: `ADD_TO_CART`, `PAYMENT_COMPLETED`) |
| `course_id` | VARCHAR | 결제 대상 강의 ID |
| `amount` | INT | 결제 금액 |
| `coupon_id` | VARCHAR | 사용된 쿠폰 ID (Nullable) |
| `payment_method` | VARCHAR | 결제 수단 (예: `CREDIT_CARD`, `TOSSPAY`) |
| `error_code` | VARCHAR | 결제 실패 시 에러 코드 (Nullable) |

3. 이탈 및 환불 로그 (refund_logs)
   
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | PK / INT | 로그 고유 ID |
| `timestamp` | DATETIME | 이벤트 발생 시간 |
| `session_id` | VARCHAR | 유저 세션 식별자 |
| `user_id` | VARCHAR | 유저 식별자 |
| `event_type` | VARCHAR | 이벤트 타입 (예: `REFUND_REQUESTED`) |
| `course_id` | VARCHAR | 환불 대상 강의 ID |
| `refund_reason` | VARCHAR | 환불 사유 (예: `단순 변심`, `서비스 불만족`) |

## 3. 이벤트 설계

단순한 랜덤 난수 생성이 아닌, 라이브클래스 서비스에서 실제로 발생할 법한 유저 시나리오에 가중치를 두어 타겟팅 이벤트를 생성했습니다.

- **트래픽 이벤트:** 웹 서비스의 기초인 '조회수'를 타겟팅. 메인 노출 여부와 강의의 유/무료 속성에 따른 유입량 차이를 비교할 수 있도록 설계했습니다.
- **결제 이벤트:** 장바구니 담기 → 체크아웃 → 결제 성공/실패로 이어지는 실제 커머스 퍼널 플로우를 구현했습니다.
- **환불 이벤트:** 결제 성공 유저 중 일부가 환불로 이어지는 플로우를 구현했습니다.

## 4. 구현하면서 고민한 점

- **문제:** 초기에는 단순한 for문을 돌려 이벤트를 순차적으로 생성했습니다. 하지만 코드가 길어질수록 유저의 행동 흐름을 제어하기 어렵고 유지보수가 불리해졌습니다.
- 해결 (FSM 도입): 이를 해결하기 위해 FSM(Finite State Machine) 패턴과 Enum을 적극 차용했습니다. 유저의 상태(조회 -> 장바구니 -> 결제)를 상태 전이 로직으로 캡슐화하여, 실제 유저 행동과 가장 유사한 형태의 데이터 파이프라인을 구축할 수 있었습니다.

## 5. 데이터 시각화 및 SQL 분석 쿼리

Grafana 대시보드를 구성하기 위해 사용된 핵심 분석 쿼리와 의도입니다.

**패널 1: 강의 특성별 조회수 비율**

- **의도:** 단순한 강의 ID 구분이 아닌, is_main_exposed와 course_fee 값을 조합해 "메인 노출 O / 유료"와 같은 직관적인 네이밍을 동적으로 생성하여 마케팅 인사이트를 도출합니다.

```
SELECT
    CONCAT(IF(is_main_exposed=1, '메인 노출 O', '메인 노출 X'), ' / ', IF(course_fee > 0, '유료', '무료')) AS metric,
    COUNT(*) AS value
FROM traffic_logs
GROUP BY course_id, is_main_exposed, course_fee
ORDER BY value DESC;
```

**패널 2: 쿠폰 사용 여부에 따른 결제 퍼널 비율**

- **의도:** 장바구니에 진입한 총인원을 모수로 하여, 최종 상태를 3가지(이탈 / 쿠폰 결제 / 일반 결제)로 완벽히 분리하여 퍼널 전환율을 추적합니다.

```
SELECT
    status AS metric,
    COUNT(*) AS value
FROM (
    SELECT
        session_id,
        CASE
            WHEN MAX(IF(event_type = 'PAYMENT_COMPLETED', 1, 0)) = 0 THEN '결제 미완료 (이탈)'
            WHEN MAX(IF(event_type = 'PAYMENT_COMPLETED' AND coupon_id IS NOT NULL, 1, 0)) = 1 THEN '쿠폰 사용 결제'
            ELSE '쿠폰 미사용 결제'
        END AS status
    FROM payment_logs
    WHERE session_id IN (
        SELECT session_id
        FROM payment_logs
        WHERE event_type = 'ADD_TO_CART'
    )
    GROUP BY session_id
) AS funnel
GROUP BY status;
```

**패널 3: 결제 수단별 상태 및 에러 분석**

- **의도:** 누적 막대그래프를 통해 결제 수단별 성공/실패 비율을 시각화하고(3-1), 실패 시 가장 많이 발생하는 에러 코드를 식별합니다(3-2).

```
-- [3-1] 결제 수단별 성공/실패 누적 데이터 (총량 기준 정렬 적용)
SELECT
    payment_method,
    completed,
    failed
FROM (
    SELECT
        payment_method,
        SUM(CASE WHEN event_type = 'PAYMENT_COMPLETED' THEN 1 ELSE 0 END) AS completed,
        SUM(CASE WHEN event_type = 'PAYMENT_FAILED' THEN 1 ELSE 0 END) AS failed,
        COUNT(*) AS total_cnt
    FROM payment_logs
    WHERE event_type IN ('PAYMENT_COMPLETED', 'PAYMENT_FAILED')
    GROUP BY payment_method
) t
ORDER BY total_cnt ASC;

-- [3-2] 결제 실패 시 에러 코드별 비율
SELECT error_code AS metric, COUNT(*) AS value
FROM payment_logs
WHERE event_type = 'PAYMENT_FAILED'
GROUP BY error_code
ORDER BY value DESC;
```

**📊 패널 4: 환불 사유별 비율**

- **의도:** 결제 완료 후 이탈하는 유저들의 주요 원인을 파악하여 서비스 개선 지표로 활용합니다.

```
SELECT refund_reason AS metric, COUNT(*) AS value
FROM refund_logs
GROUP BY refund_reason;
```
