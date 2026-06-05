import random
from datetime import datetime, timedelta
from app.core.constants import ScenarioConfig
from app.db.models import COURSE_CATALOG
from app.services.fsm import UserJourneyFSM

def generate_logs(num_users=1000, days_ago=30, custom_config=None):
    config = custom_config if custom_config else ScenarioConfig()
    start_date = datetime.now() - timedelta(days=days_ago)
    all_logs = []
    
    print(f" 메인/클릭수 기반 FSM 제너레이터 ({num_users}명) 구동 시작...")
    
    for i in range(1, num_users + 1):
        user_id = f"user_{str(i).zfill(4)}"
        
        # [핵심] 모든 유저가 3개의 강의를 각각 독립적으로 테스트함
        for course_id, course_obj in COURSE_CATALOG.items():
            start_time = start_date + timedelta(
                days=random.randint(0, days_ago - 3), 
                hours=random.randint(0, 23), 
                minutes=random.randint(0, 59)
            )
            
            fsm = UserJourneyFSM(user_id, course_obj, start_time, config)
            all_logs.extend(fsm.run())

    all_logs.sort(key=lambda x: x.timestamp)
    print(f"✅ 총 {len(all_logs)}건 로그 생성 완료.")
    return all_logs