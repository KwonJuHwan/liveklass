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
    episode_category: str
    episode_number: int
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