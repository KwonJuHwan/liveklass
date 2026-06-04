import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
from models import TrafficLog, PaymentLog, RefundLog

fake = Faker('ko_KR')

COURSES = {
    "C_1001": {"name": "Spring Boot Master", "fee": 100000, "is_main": False},
    "C_1002": {"name": "Python Basic", "fee": 0, "is_main": True},
    "C_1003": {"name": "MSA Architecture", "fee": 200000, "is_main": False}
}
COURSE_IDS = list(COURSES.keys())
COURSE_WEIGHTS = [35, 50, 15] 

PAYMENT_METHODS = ["CREDIT_CARD", "KAKAOPAY", "TOSSPAY", "BANK_TRANSFER"]
ERROR_CODES = ["ERR_TIMEOUT", "ERR_LIMIT_EXCEEDED", "ERR_USER_CANCEL", "ERR_SYSTEM"]

def generate_logs(num_users=1000, days_ago=30):
    all_logs = []
    start_date = datetime.now() - timedelta(days=days_ago)

    print(f"{num_users}명의 유저 시나리오 생성을 시작")

    for i in range(1, num_users + 1):
        user_id = f"user_{str(i).zfill(4)}"
        
        # 1. 유저당 들을 강의 개수 결정 (1개 80%, 2개 15%, 3개 5%)
        num_courses = random.choices([1, 2, 3], weights=[80, 15, 5], k=1)[0]
        selected_courses = random.choices(COURSE_IDS, weights=COURSE_WEIGHTS, k=num_courses)
        selected_courses = list(set(selected_courses))

        for course_id in selected_courses:
            course = COURSES[course_id]
            session_id = str(uuid.uuid4())
            
            # 유저의 해당 강의 첫 접속 시간 (최근 30일 내 랜덤)
            current_time = start_date + timedelta(
                days=random.randint(0, days_ago - 3),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # 트래픽/유입 로그 생성
            # 몇 화까지 볼 것인가? 
            max_ep_weights = [30, 15, 10, 10, 8, 7, 5, 5, 4, 3, 2, 1] 
            max_ep = random.choices(range(1, 13), weights=max_ep_weights, k=1)[0]

            for ep in range(1, max_ep + 1):
                log = TrafficLog(
                    timestamp=current_time,
                    user_id=user_id,
                    session_id=session_id,
                    event_type="EPISODE_VIEW",
                    course_id=course_id,
                    episode_category=course["name"],
                    episode_number=ep,
                    course_fee=course["fee"],
                    is_main_exposed=course["is_main"]
                )
                all_logs.append(log)
                # 다음 화를 보기까지 5~15분 소요
                current_time += timedelta(minutes=random.randint(5, 15))

            # 결제 퍼널 로직 (유료 강의만 해당)
            if course["fee"] > 0:
                # 30% 확률로 장바구니 담기
                if random.random() <= 0.3:
                    current_time += timedelta(minutes=random.randint(1, 5))
                    all_logs.append(PaymentLog(
                        timestamp=current_time, user_id=user_id, session_id=session_id,
                        event_type="ADD_TO_CART", course_id=course_id, amount=course["fee"]
                    ))

                    # 장바구니 담은 유저 중 70%가 결제창 진입
                    if random.random() <= 0.7:
                        current_time += timedelta(minutes=random.randint(1, 3))
                        all_logs.append(PaymentLog(
                            timestamp=current_time, user_id=user_id, session_id=session_id,
                            event_type="CHECKOUT_STARTED", course_id=course_id, amount=course["fee"]
                        ))

                        # 쿠폰 발급 여부 (80% 확률)
                        has_coupon = random.random() <= 0.8
                        coupon_id = f"CPN_{random.randint(100,999)}" if has_coupon else None
                        final_amount = course["fee"] - 20000 if has_coupon else course["fee"]
                        
                        # 결제 성공 확률: 쿠폰 O (90%), 쿠폰 X (40%)
                        success_rate = 0.9 if has_coupon else 0.4
                        is_success = random.random() <= success_rate
                        
                        current_time += timedelta(minutes=random.randint(1, 2))
                        pay_method = random.choice(PAYMENT_METHODS)

                        if is_success:
                            all_logs.append(PaymentLog(
                                timestamp=current_time, user_id=user_id, session_id=session_id,
                                event_type="PAYMENT_COMPLETED", course_id=course_id, 
                                amount=final_amount, coupon_id=coupon_id, payment_method=pay_method
                            ))

                            # 환불 로직 (결제 성공 유저 중 5%가 환불)
                            if random.random() <= 0.05:
                                refund_time = current_time + timedelta(days=random.randint(1, 3))
                                reason = "SIMPLE_CHANGE_OF_MIND" if course_id == "C_1001" else "NOT_AS_EXPECTED"
                                all_logs.append(RefundLog(
                                    timestamp=refund_time, user_id=user_id, session_id=session_id,
                                    event_type="REFUND_REQUESTED", course_id=course_id, refund_reason=reason
                                ))
                        else:
                            # 결제 실패
                            error = random.choice(ERROR_CODES)
                            all_logs.append(PaymentLog(
                                timestamp=current_time, user_id=user_id, session_id=session_id,
                                event_type="PAYMENT_FAILED", course_id=course_id, 
                                amount=final_amount, coupon_id=coupon_id, 
                                payment_method=pay_method, error_code=error
                            ))

    all_logs.sort(key=lambda x: x.timestamp)
    print(f"총 {len(all_logs)}건의 로그가 생성 및 정렬.")
    
    return all_logs