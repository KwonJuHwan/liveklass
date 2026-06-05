import time
from app.db.database import DatabaseManager
from app.services.generators import generate_logs
from app.db.models import TrafficLog, PaymentLog, RefundLog

def main():
    start_time = time.time()
    
    db = DatabaseManager()
    
    logs = generate_logs(num_users=1000, days_ago=30)
    
    print("\n DB에 데이터를 순차적으로 적재 시작...")
    
    total = len(logs)
    for i, log in enumerate(logs):
        if isinstance(log, TrafficLog):
            db.insert_traffic_log(log)
        elif isinstance(log, PaymentLog):
            db.insert_payment_log(log)
        elif isinstance(log, RefundLog):
            db.insert_refund_log(log)
            
        if (i + 1) % 1000 == 0:
            print(f"🔄 [{i + 1} / {total}] 적재 완료...")

    db.close()
    
    elapsed_time = time.time() - start_time
    print(f"\n🎉 모든 데이터 파이프라인 적재 완료! (소요 시간: {elapsed_time:.2f}초)")

if __name__ == "__main__":
    main()