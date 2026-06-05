from enum import Enum
from dataclasses import dataclass

class UserState(Enum):
    COURSE_VIEW = "강의 조회"
    CART = "장바구니 담기"
    CHECKOUT = "결제 진입"
    PAYMENT_SUCCESS = "결제 성공"
    PAYMENT_FAIL = "결제 실패"
    REFUND = "환불"
    EXIT = "이탈"

class EventType(Enum):
    COURSE_VIEW = "COURSE_VIEW"
    ADD_TO_CART = "ADD_TO_CART"
    CHECKOUT_STARTED = "CHECKOUT_STARTED"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    REFUND_REQUESTED = "REFUND_REQUESTED"

class RefundReason(Enum):
    SIMPLE_CHANGE_OF_MIND = "단순 변심"
    LOW_QUALITY = "강의 퀄리티 불만족"
    REPURCHASE = "재구매"
    NOT_AS_EXPECTED = "예상과 다름"
    UNFRIENDLY_INSTRUCTOR = "강사 불친절"

class PaymentMethod(Enum):
    CREDIT_CARD = "신용카드"
    BANK_TRANSFER = "계좌이체"
    KAKAOPAY = "카카오페이"
    NAVERPAY = "네이버페이"
    TOSSPAY = "토스페이"

class ErrorCode(Enum):
    ERR_TIMEOUT = "통신 시간 초과"
    ERR_LIMIT_EXCEEDED = "한도 초과"
    ERR_USER_CANCEL = "사용자 변심 취소"
    ERR_SYSTEM = "PG사 시스템 오류"
    ERR_INTERNAL_SYSTEM = "내부 시스템 오류"

@dataclass
class ScenarioConfig:
    # 퍼널 전환 확률
    cart_prob: float = 0.6              # 장바구니 진입 확률 (60%)
    checkout_prob: float = 0.7          # 장바구니 -> 결제창 전환율 (70%)
    coupon_prob: float = 0.8            # 결제창 진입 시 쿠폰 소지 확률 (80%)
    success_rate_with_coupon: float = 0.9 # 쿠폰 소지자 결제 성공률 (90%)
    success_rate_no_coupon: float = 0.4   # 쿠폰 미소지자 결제 성공률 (40%)
    refund_prob: float = 0.15           # 결제 성공 후 환불 요청 확률 (5%)

    # 가중치 설정

    # 1. 강의별 클릭 수 범위 지정
    course_click_ranges: dict = None
    
    def __post_init__(self):
        self.course_click_ranges = {
            "C_1001": (1, 70),
            "C_1002": (0, 150),
            "C_1003": (0, 30)
        }
    
    # 2. 환불 사유 비율 (단순변심, 퀄리티불만, 재구매, 예상다름, 강사불친절 순)
    refund_reason_weights: tuple = (70, 7, 10, 11, 2)

    # 3. 결제 수단 비율 (신용카드, 계좌이체, 카카오, 네이버, 토스 순)
    # 3-1. 결제 '성공' 시 수단 분포 
    payment_success_weights: tuple = (10, 5, 30, 20, 35) 
    
    # 3-2. 결제 '실패' 시 수단 분포
    payment_fail_weights: tuple = (40, 30, 15, 10, 5)
    # 3-3. 에러 코드 발생 가중치 (통신초과, 한도초과, 변심, PG오류, 내부오류 순)
    error_code_weights: tuple = (30, 20, 40, 9, 1)

    # 시간 지연 설정 - (최소, 최대)
    view_delay_minutes: tuple = (1, 5)     # 강의 조회 소요 시간
    cart_delay_minutes: tuple = (1, 5)      # 장바구니 체류 시간
    checkout_delay_minutes: tuple = (1, 3)  # 결제창 체류 시간
    payment_delay_minutes: tuple = (1, 2)   # PG사 결제 승인 소요 시간
    refund_delay_days: tuple = (1, 3)       # 결제 후 환불까지 걸리는 일수