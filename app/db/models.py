from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TrafficLog:
    """트래픽 및 유입 로그 DTO"""
    timestamp: datetime
    user_id: str
    session_id: str
    event_type: str
    course_id: str
    course_fee: int
    is_main_exposed: bool
    id: Optional[int] = None 

@dataclass
class PaymentLog:
    """결제 퍼널 및 에러 로그 DTO"""
    timestamp: datetime
    user_id: str
    session_id: str
    event_type: str
    course_id: str
    amount: int
    coupon_id: Optional[str] = None
    payment_method: Optional[str] = None
    error_code: Optional[str] = None
    id: Optional[int] = None

@dataclass
class RefundLog:
    """이탈 및 환불 로그 DTO"""
    timestamp: datetime
    user_id: str
    session_id: str
    event_type: str
    course_id: str
    refund_reason: str
    id: Optional[int] = None

@dataclass
class Course:
    id: str
    name: str
    fee: int
    is_main: bool

COURSE_CATALOG = {
    "C_1001": Course(id="C_1001", name="Spring Boot Master", fee=100000, is_main=True),
    "C_1002": Course(id="C_1002", name="Python Basic", fee=0, is_main=False),
    "C_1003": Course(id="C_1003", name="MSA Architecture", fee=200000, is_main=False)
}