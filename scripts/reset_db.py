import pymysql
import app.core.config as config

def reset_database():
    conn = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset='utf8mb4'
    )
    
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE traffic_logs;")
        cursor.execute("TRUNCATE TABLE payment_logs;")
        cursor.execute("TRUNCATE TABLE refund_logs;")
        
    conn.commit()
    conn.close()
    print("초기화 완료")

if __name__ == "__main__":
    reset_database()