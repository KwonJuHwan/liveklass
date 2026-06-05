import random
import uuid
from datetime import timedelta
from app.db.models import TrafficLog, PaymentLog, RefundLog
from app.core.constants import UserState, EventType, RefundReason, PaymentMethod, ErrorCode

class UserJourneyFSM:
    def __init__(self, user_id, course, start_time, config):
        self.user_id = user_id
        self.session_id = str(uuid.uuid4())
        self.course = course 
        self.current_time = start_time
        self.config = config
        
        self.logs = []
        min_clicks, max_clicks = self.config.course_click_ranges[self.course.id]
        self.total_clicks = random.randint(min_clicks, max_clicks)
        self.current_click = 0
        self.has_coupon = False

    def run(self):
        current_state = UserState.COURSE_VIEW
        while current_state != UserState.EXIT:
            handler = getattr(self, f"state_{current_state.name.lower()}")  
            current_state = handler()
        return self.logs

    def state_course_view(self):
        self.current_click += 1
        
        self.logs.append(TrafficLog(
            timestamp=self.current_time, user_id=self.user_id, session_id=self.session_id,
            event_type=EventType.COURSE_VIEW.value, course_id=self.course.id, 
            course_fee=self.course.fee, is_main_exposed=self.course.is_main
        ))
        
        self.current_time += timedelta(minutes=random.randint(*self.config.view_delay_minutes))
        
        if self.current_click < self.total_clicks:
            return UserState.COURSE_VIEW
            
        if self.course.fee > 0 and random.random() <= self.config.cart_prob:
            return UserState.CART
            
        return UserState.EXIT

    def state_cart(self):
        self.current_time += timedelta(minutes=random.randint(*self.config.cart_delay_minutes))
        self.logs.append(PaymentLog(
            timestamp=self.current_time, user_id=self.user_id, session_id=self.session_id, 
            event_type=EventType.ADD_TO_CART.value, course_id=self.course.id, amount=self.course.fee
        ))
        
        if random.random() <= self.config.checkout_prob:
            return UserState.CHECKOUT
        return UserState.EXIT

    def state_checkout(self):
        self.current_time += timedelta(minutes=random.randint(*self.config.checkout_delay_minutes))
        self.logs.append(PaymentLog(
            timestamp=self.current_time, user_id=self.user_id, session_id=self.session_id, 
            event_type=EventType.CHECKOUT_STARTED.value, course_id=self.course.id, amount=self.course.fee
        ))
        
        self.has_coupon = random.random() <= self.config.coupon_prob
        success_rate = self.config.success_rate_with_coupon if self.has_coupon else self.config.success_rate_no_coupon
        
        if random.random() <= success_rate:
            return UserState.PAYMENT_SUCCESS
        return UserState.PAYMENT_FAIL

    def state_payment_success(self):
        self.current_time += timedelta(minutes=random.randint(*self.config.payment_delay_minutes))
        final_amount = self.course.fee - 20000 if self.has_coupon else self.course.fee
        coupon_id = f"CPN_{random.randint(100,999)}" if self.has_coupon else None
        
        methods = list(PaymentMethod)
        pay_method = random.choices(methods, weights=self.config.payment_success_weights, k=1)[0].value
        
        self.logs.append(PaymentLog(
            timestamp=self.current_time, user_id=self.user_id, session_id=self.session_id, 
            event_type=EventType.PAYMENT_COMPLETED.value, course_id=self.course.id, 
            amount=final_amount, coupon_id=coupon_id, payment_method=pay_method
        ))
        
        if random.random() <= self.config.refund_prob:
            return UserState.REFUND
        return UserState.EXIT

    def state_payment_fail(self):
        self.current_time += timedelta(minutes=random.randint(*self.config.payment_delay_minutes))
        final_amount = self.course.fee - 20000 if self.has_coupon else self.course.fee
        coupon_id = f"CPN_{random.randint(100,999)}" if self.has_coupon else None
        
        methods = list(PaymentMethod)
        pay_method = random.choices(methods, weights=self.config.payment_fail_weights, k=1)[0].value
        
        error_codes = list(ErrorCode)
        error = random.choices(error_codes, weights=self.config.error_code_weights, k=1)[0].value 
        
        self.logs.append(PaymentLog(
            timestamp=self.current_time, user_id=self.user_id, session_id=self.session_id, 
            event_type=EventType.PAYMENT_FAILED.value, course_id=self.course.id, 
            amount=final_amount, coupon_id=coupon_id, payment_method=pay_method, error_code=error
        ))
        return UserState.EXIT

    def state_refund(self):
        self.current_time += timedelta(days=random.randint(*self.config.refund_delay_days))
        
        reasons = list(RefundReason)
        reason = random.choices(reasons, weights=self.config.refund_reason_weights, k=1)[0].value
        
        self.logs.append(RefundLog(
            timestamp=self.current_time, user_id=self.user_id, session_id=self.session_id, 
            event_type=EventType.REFUND_REQUESTED.value, course_id=self.course.id, refund_reason=reason
        ))
        return UserState.EXIT