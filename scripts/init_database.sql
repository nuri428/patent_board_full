-- MariaDB 초기화 스크립트
-- 사용자 생성 (이미 존재하는 경우 건너�)
CREATE USER IF NOT EXISTS 'patent_user'@'%' IDENTIFIED BY 'patent_system'@'%';
GRANT ALL PRIVILEGES ON patent_db.* TO 'patent_user'@'%';
FLUSH PRIVILEGES;

-- 특허 데이터 생성
USE patent_db;

-- 특허 테이블 생성 (초기 특허 데이터)
CREATE TABLE IF NOT EXISTS patents (
    id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    filing_date DATE,
    status ENUM('pending', 'granted', 'expired', 'abandoned') DEFAULT 'pending',
    assignee VARCHAR(255),
    inventors JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    INDEX idx_filing_date (filing_date),
    INDEX idx_assignee (assignee),
    INDEX idx_status (status)
);

-- 관계 데이터 생성
CREATE TABLE IF NOT EXISTS patent_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patent_id VARCHAR(50) NOT NULL,
    related_patent_id VARCHAR(50) NOT NULL,
    relationship_type ENUM('cites', 'cited_by', 'similar_to', 'divisional', 'priority_date') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    FOREIGN KEY (patent_id) REFERENCES patents(id) ON DELETE CASCADE
);

-- 사용자 관리 테이블
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSON
);

-- MCP 서버 로그
CREATE TABLE IF NOT EXISTS mcp_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100),
    user_id INT,
    action TEXT NOT NULL,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 레포트 분석 테이블
CREATE TABLE IF NOT EXISTS patent_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patent_id VARCHAR(50),
    search_query TEXT,
    search_type VARCHAR(50) DEFAULT 'keyword',
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patent_id) REFERENCES patents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 알림 힘피 알림 테이블
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSON,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 인덱스 테이블
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(50),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 시스템 상태 테이블
CREATE TABLE IF NOT EXISTS system_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    message TEXT,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 샘플링 버전 기록 테이블
CREATE TABLE IF NOT EXISTS version_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    changelog TEXT,
    deployed_by INT,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;