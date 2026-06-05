import pymysql
import app.core.config as config
from app.db.models import TrafficLog, PaymentLog, RefundLog

class DatabaseManager:
    def __init__(self):
        self.connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def insert_traffic_log(self, log: TrafficLog):
        """트래픽 로그 INSERT"""
        sql = """
            INSERT INTO traffic_logs 
            (timestamp, user_id, session_id, event_type, course_id, course_fee, is_main_exposed) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self.connection.cursor() as cursor:
                cursor.execute(sql, (
                    log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    log.user_id,
                    log.session_id,
                    log.event_type,
                    log.course_id,
                    log.course_fee,
                    log.is_main_exposed
                ))
        self.connection.commit()

    def insert_payment_log(self, log: PaymentLog):
        """결제 퍼널 로그 INSERT"""
        sql = """
            INSERT INTO payment_logs 
            (timestamp, user_id, session_id, event_type, course_id, amount, coupon_id, payment_method, error_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (
                log.timestamp, 
                log.user_id, 
                log.session_id, 
                log.event_type, 
                log.course_id,
                log.amount, 
                log.coupon_id, 
                log.payment_method, 
                log.error_code
            ))
        self.connection.commit()

    def insert_refund_log(self, log: RefundLog):
        """환불 로그 INSERT"""
        sql = """
            INSERT INTO refund_logs 
            (timestamp, user_id, session_id, event_type, course_id, refund_reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (
                log.timestamp, 
                log.user_id, 
                log.session_id, 
                log.event_type, 
                log.course_id, 
                log.refund_reason
            ))
        self.connection.commit()

    def close(self):
        self.connection.close()