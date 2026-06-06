import time
from app.db.database import DatabaseManager
from app.services.generators import generate_logs
from app.db.models import TrafficLog, PaymentLog, RefundLog

def main():
    start_time = time.time()
    
    db = DatabaseManager()
    
    logs = generate_logs(num_users=1000, days_ago=30)
    
    print("\n DB에 데이터 적재 시작")
    
    traffic_batch = []
    payment_batch = []
    refund_batch = []
    
    for log in logs:
        if isinstance(log, TrafficLog):
            traffic_batch.append(log)
        elif isinstance(log, PaymentLog):
            payment_batch.append(log)
        elif isinstance(log, RefundLog):
            refund_batch.append(log)
            
    if traffic_batch:
        db.bulk_insert_traffic_logs(traffic_batch)
        print(f"트래픽 로그 {len(traffic_batch)}건 적재 완료")
        
    if payment_batch:
        db.bulk_insert_payment_logs(payment_batch)
        print(f"결제 로그 {len(payment_batch)}건 적재 완료")
        
    if refund_batch:
        db.bulk_insert_refund_logs(refund_batch)
        print(f"환불 로그 {len(refund_batch)}건 적재 완료")

    db.close()
    
    elapsed_time = time.time() - start_time
    print(f"\n모든 데이터 파이프라인 적재 완료 (소요 시간: {elapsed_time:.2f}초)")

if __name__ == "__main__":
    main()