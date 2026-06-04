CREATE DATABASE IF NOT EXISTS liveclass_logs;
USE liveclass_logs;

-- 트래픽 및 유입 로그 테이블
CREATE TABLE IF NOT EXISTS traffic_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    episode_category VARCHAR(100),
    episode_number INT,
    course_fee INT DEFAULT 0,
    is_main_exposed BOOLEAN,
    INDEX idx_session (session_id),
    INDEX idx_timestamp (timestamp)
);

-- 결제 퍼널 및 에러 로그 테이블
CREATE TABLE IF NOT EXISTS payment_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    amount INT NOT NULL,
    coupon_id VARCHAR(50) NULL,
    payment_method VARCHAR(50) NULL,
    error_code VARCHAR(50) NULL,
    INDEX idx_session (session_id),
    INDEX idx_event_type (event_type),
    INDEX idx_timestamp (timestamp)
);

-- 이탈 및 환불 로그 테이블
CREATE TABLE IF NOT EXISTS refund_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    course_id VARCHAR(50) NOT NULL,
    refund_reason VARCHAR(100) NOT NULL,
    INDEX idx_course (course_id),
    INDEX idx_timestamp (timestamp)
);