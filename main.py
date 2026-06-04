import time
from database import DatabaseManager
from generators import generate_logs
from models import TrafficLog, PaymentLog, RefundLog

def main():
    db = DatabaseManager()
    
    logs = generate_logs(num_users=1000, days_ago=30)
    
    print("DB에 데이터를 적재 시작.")
    
    total = len(logs)
    for i, log in enumerate(logs):
        if isinstance(log, TrafficLog):
            db.insert_traffic_log(log)
        elif isinstance(log, PaymentLog):
            db.insert_payment_log(log)
        elif isinstance(log, RefundLog):
            db.insert_refund_log(log)
            
        if (i + 1) % 1000 == 0:
            print(f"[{i + 1} / {total}] 적재 완료...")

    db.close()
    print("모든 데이터 파이프라인 적재가 완료")

if __name__ == "__main__":
    main()