import pymysql
import app.core.config as config

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
        "1. 강의 특성별 조회수 비교 (총 View 포함)": """
            SELECT
                CASE
                    WHEN is_main_exposed = 1 AND course_fee > 0 THEN '메인 노출 O / 유료'
                    WHEN is_main_exposed = 0 AND course_fee = 0 THEN '메인 노출 X / 무료'
                    WHEN is_main_exposed = 0 AND course_fee > 0 THEN '메인 노출 X / 유료'
                END AS course_type,
                COUNT(*) AS view_count
            FROM traffic_logs
            WHERE
                (is_main_exposed = 1 AND course_fee > 0)
                OR (is_main_exposed = 0 AND course_fee = 0)
                OR (is_main_exposed = 0 AND course_fee > 0)
            GROUP BY is_main_exposed, course_fee

            UNION ALL

            SELECT
                '총 조회수' AS course_type,
                COUNT(*) AS view_count
            FROM traffic_logs
            ORDER BY
                CASE course_type
                    WHEN '메인 노출 O / 유료' THEN 1
                    WHEN '메인 노출 X / 무료' THEN 2
                    WHEN '메인 노출 X / 유료' THEN 3
                    WHEN '총 조회수' THEN 4
                END;
        """,
        
        "2. 결제 퍼널 종합 (장바구니 및 쿠폰 유무)": """
            SELECT
                COUNT(DISTINCT IF(event_type = 'ADD_TO_CART', session_id, NULL)) AS total_cart,
                COUNT(DISTINCT IF(event_type = 'PAYMENT_COMPLETED', session_id, NULL)) AS total_paid,
                COUNT(DISTINCT IF(event_type = 'PAYMENT_COMPLETED' AND coupon_id IS NOT NULL, session_id, NULL)) AS paid_with_coupon,
                COUNT(DISTINCT IF(event_type = 'PAYMENT_COMPLETED' AND coupon_id IS NULL, session_id, NULL)) AS paid_without_coupon
            FROM payment_logs;
        """,
        
        "3. 결제 에러 심층 분석 (수단별 & 에러코드별)": """
            SELECT 
                IFNULL(payment_method, '총계(Total)') AS payment_method,
                IFNULL(error_code, '수단별 소계') AS error_code,
                COUNT(*) AS error_count
            FROM payment_logs
            WHERE event_type = 'PAYMENT_FAILED'  
            GROUP BY payment_method, error_code WITH ROLLUP;
        """,
        
        "4. 환불 사유 통계 (총 환불 포함)": """
            SELECT 
                IFNULL(refund_reason, '총 환불 횟수(Total)') AS refund_reason, 
                COUNT(*) AS refund_count
            FROM refund_logs
            GROUP BY refund_reason WITH ROLLUP;
        """
    }

    with conn.cursor() as cursor:
        for title, sql in queries.items():
            print(f"\n{'='*50}\n {title}\n{'='*50}")
            cursor.execute(sql)
            results = cursor.fetchall()
            
            if results:
                headers = results[0].keys()
                print(f"{' | '.join(headers)}")
                print("-" * 50)
                for row in results:
                    values = [str(val) for val in row.values()]
                    print(f"{' | '.join(values)}")
            else:
                print("데이터가 없습니다.")

    conn.close()

if __name__ == "__main__":
    run_analysis()