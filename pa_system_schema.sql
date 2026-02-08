-- PA System Database Schema
-- Purpose: User conversation history, preferences, and chatbot session management

-- Create database
CREATE DATABASE IF NOT EXISTS pa_system;
USE pa_system;

-- Set character set
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- User Properties Table
-- Stores user preferences, settings, and custom properties
CREATE TABLE IF NOT EXISTS user_properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    key VARCHAR(255) NOT NULL,
    value JSON NOT NULL,
    type ENUM('preference', 'setting', 'context', 'profile') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_user_key (user_id, key),
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Conversation Sessions Table
-- Stores user conversation sessions
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    context JSON DEFAULT NULL,
    status ENUM('active', 'archived', 'closed') DEFAULT 'active',
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Conversation Messages Table
-- Stores individual messages in conversations
CREATE TABLE IF NOT EXISTS conversation_messages (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON DEFAULT NULL,
    
    -- Foreign key constraints
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_role (role),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_session (user_id, session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Session Summary Table
-- Quick access to session summaries for performance optimization
CREATE TABLE IF NOT EXISTS user_session_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    last_message TEXT DEFAULT NULL,
    last_message_time DATETIME DEFAULT NULL,
    total_messages INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_last_message_time (last_message_time),
    INDEX idx_total_messages (total_messages)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User Profiles Table
-- Extended user profile information for personalization
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) DEFAULT NULL,
    email VARCHAR(255) DEFAULT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    theme VARCHAR(20) DEFAULT 'light',
    preferences JSON DEFAULT '{}',
    metadata JSON DEFAULT '{}',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_language (language),
    INDEX idx_theme (theme)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chatbot Context History Table
-- Tracks context changes and important conversation points
CREATE TABLE IF NOT EXISTS chatbot_context_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    context_key VARCHAR(255) NOT NULL,
    context_value JSON NOT NULL,
    change_type ENUM('start', 'update', 'clear', 'error') NOT NULL,
    reason VARCHAR(500) DEFAULT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (session_id) REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_session_id (session_id),
    INDEX idx_context_key (context_key),
    INDEX idx_change_type (change_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System Configuration Table
-- Stores system-wide chatbot configuration
CREATE TABLE IF NOT EXISTS system_configurations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSON NOT NULL,
    description VARCHAR(500) DEFAULT NULL,
    category VARCHAR(100) DEFAULT 'general',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_config_key (config_key),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create triggers for updating session summaries
DELIMITER //
CREATE TRIGGER after_message_insert
AFTER INSERT ON conversation_messages
FOR EACH ROW
BEGIN
    -- Update or create session summary
    INSERT INTO user_session_summaries (user_id, session_id, last_message, last_message_time, total_messages)
    VALUES (NEW.user_id, NEW.session_id, LEFT(NEW.message, 500), NEW.timestamp, 1)
    ON DUPLICATE KEY UPDATE
        last_message = LEFT(NEW.message, 500),
        last_message_time = NEW.timestamp,
        total_messages = total_messages + 1,
        updated_at = CURRENT_TIMESTAMP;
END//
CREATE TRIGGER after_message_update
AFTER UPDATE ON conversation_messages
FOR EACH ROW
BEGIN
    IF NEW.message <> OLD.message THEN
        UPDATE user_session_summaries
        SET last_message = LEFT(NEW.message, 500),
            last_message_time = NEW.timestamp,
            updated_at = CURRENT_TIMESTAMP
        WHERE session_id = NEW.session_id;
    END IF;
END//
CREATE TRIGGER after_session_status_update
AFTER UPDATE ON conversation_sessions
FOR EACH ROW
BEGIN
    IF NEW.status <> OLD.status THEN
        -- Archive summary when session is archived
        IF NEW.status = 'archived' THEN
            -- Additional archive logic can be added here
        END IF;
    END IF;
END//
DELIMITER ;

-- Set foreign key checks back to default
SET FOREIGN_KEY_CHECKS = 1;

-- Insert default system configurations
INSERT IGNORE INTO system_configurations (config_key, config_value, description, category) VALUES
('max_conversation_length', 1000, 'Maximum number of messages per conversation', 'limits'),
('max_session_duration_hours', 24, 'Maximum duration of a conversation session in hours', 'limits'),
('default_language', 'en', 'Default language for new conversations', 'general'),
('enable_memory', true, 'Enable long-term memory for users', 'features'),
('cache_ttl_hours', 24, 'Cache expiration time in hours', 'performance'),
('max_context_tokens', 4000, 'Maximum context tokens per conversation', 'limits'),
('response_timeout_seconds', 30, 'Timeout for AI response generation', 'performance');

-- Grant privileges (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON pa_system.* TO 'chatbot_user'@'%';
-- FLUSH PRIVILEGES;

-- Create optimized views for common queries
CREATE VIEW user_active_sessions AS
SELECT s.id, s.user_id, s.title, s.created_at, s.updated_at, s.context, s.status,
       COUNT(m.id) as message_count,
       MAX(m.timestamp) as last_activity
FROM conversation_sessions s
LEFT JOIN conversation_messages m ON s.id = m.session_id
WHERE s.status = 'active'
GROUP BY s.id, s.user_id, s.title, s.created_at, s.updated_at, s.context, s.status;

CREATE VIEW conversation_summary AS
SELECT 
    s.id as session_id,
    s.user_id,
    s.title,
    s.created_at,
    s.updated_at,
    s.status,
    COALESCE(ss.last_message, '') as last_message,
    COALESCE(ss.last_message_time, s.updated_at) as last_message_time,
    COALESCE(ss.total_messages, 0) as total_messages,
    JSON_LENGTH(s.context) as context_size
FROM conversation_sessions s
LEFT JOIN user_session_summaries ss ON s.id = ss.session_id;