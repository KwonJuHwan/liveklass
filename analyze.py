import pymysql
import config

def run_analysis():
    conn = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    queries = {
        "1. 회차별 시청 이탈률 ": """
            SELECT episode_number, COUNT(DISTINCT session_id) AS view_count
            FROM traffic_logs
            WHERE course_id = 'C_1001'
            GROUP BY episode_number
            ORDER BY episode_number LIMIT 5;
        """,
        "2. 쿠폰 유무에 따른 결제 전환율": """
            SELECT
                coupon_status,
                COUNT(*) AS checkout_users,
                SUM(is_paid) AS paid_users,
                ROUND(SUM(is_paid) / COUNT(*) * 100, 1) AS conversion_rate
            FROM (
                SELECT session_id,
                    IF(MAX(coupon_id) IS NOT NULL, '쿠폰 사용', '쿠폰 미사용') AS coupon_status,
                    MAX(IF(event_type = 'PAYMENT_COMPLETED', 1, 0)) AS is_paid
                FROM payment_logs
                WHERE event_type IN ('CHECKOUT_STARTED', 'PAYMENT_COMPLETED', 'PAYMENT_FAILED')
                GROUP BY session_id
            ) AS session_summary
            GROUP BY coupon_status;
        """,
        "3. 결제 수단별 에러 비율": """
            SELECT payment_method, COUNT(*) AS total_attempts,
                   SUM(IF(event_type = 'PAYMENT_FAILED', 1, 0)) AS errors,
                   ROUND(SUM(IF(event_type = 'PAYMENT_FAILED', 1, 0)) / COUNT(*) * 100, 1) AS error_rate
            FROM payment_logs
            WHERE event_type IN ('PAYMENT_COMPLETED', 'PAYMENT_FAILED')
            GROUP BY payment_method
            ORDER BY error_rate DESC;
        """,
        "4. 강의별 환불 사유": """
            SELECT 
                course_id, 
                refund_reason, 
                COUNT(*) AS refund_count
            FROM refund_logs
            GROUP BY course_id, refund_reason
            ORDER BY course_id, refund_count DESC;
        """
    }

    with conn.cursor() as cursor:
        for title, sql in queries.items():
            print(f"\n{'='*50}\n📊 {title}\n{'='*50}")
            cursor.execute(sql)
            results = cursor.fetchall()
            
            # 헤더 출력
            if results:
                headers = results[0].keys()
                print(f"{' | '.join(headers)}")
                print("-" * 50)
                # 데이터 출력
                for row in results:
                    values = [str(val) for val in row.values()]
                    print(f"{' | '.join(values)}")
            else:
                print("데이터가 없습니다.")

    conn.close()

if __name__ == "__main__":
    run_analysis()