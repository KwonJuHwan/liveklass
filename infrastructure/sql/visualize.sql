-- Grafana 시각화에 활용한 SQL Query

-- 강의 특성별 조회수 비율
SELECT
    CONCAT(IF(is_main_exposed=1, '메인 노출 O', '메인 노출 X'), ' / ', IF(course_fee > 0, '유료', '무료')) AS metric,
    COUNT(*) AS value
FROM traffic_logs
GROUP BY course_id, is_main_exposed, course_fee
ORDER BY value DESC;

-- 쿠폰 사용 여부에 따른 결제 퍼널 비율
SELECT 
    status AS metric, 
    COUNT(*) AS value
FROM (
    SELECT 
        session_id,
        CASE  
            WHEN MAX(IF(event_type = 'PAYMENT_COMPLETED', 1, 0)) = 0 THEN '결제 미완료 (이탈)'
            WHEN MAX(IF(event_type = 'PAYMENT_COMPLETED' AND coupon_id IS NOT NULL, 1, 0)) = 1 THEN '쿠폰 사용 결제'
            ELSE '쿠폰 미사용 결제'
        END AS status
    FROM payment_logs
    WHERE session_id IN (
        SELECT session_id 
        FROM payment_logs 
        WHERE event_type = 'ADD_TO_CART'
    )
    GROUP BY session_id
) AS funnel
GROUP BY status;

-- 결제 수단별 에러 비율
SELECT
    payment_method,
    completed,
    failed
FROM (
    SELECT
        payment_method,
        SUM(CASE WHEN event_type = 'PAYMENT_COMPLETED' THEN 1 ELSE 0 END) AS completed,
        SUM(CASE WHEN event_type = 'PAYMENT_FAILED' THEN 1 ELSE 0 END) AS failed,
        COUNT(*) AS total_cnt
    FROM payment_logs
    WHERE event_type IN ('PAYMENT_COMPLETED', 'PAYMENT_FAILED')
    GROUP BY payment_method
) t
ORDER BY total_cnt ASC;

-- 결제 실패시 에러 코드별 비율
SELECT error_code AS metric, COUNT(*) AS value
FROM payment_logs
WHERE event_type = 'PAYMENT_FAILED'
GROUP BY error_code
ORDER BY value DESC;

-- 환불 사유별 비율
SELECT refund_reason AS metric, COUNT(*) AS value
FROM refund_logs
GROUP BY refund_reason;