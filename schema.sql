-- User Accounts
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    role ENUM('traveler', 'admin') DEFAULT 'traveler',
    is_banned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Watched Routes
CREATE TABLE watches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    depart_date DATE NOT NULL,
    return_date DATE,
    threshold_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Price History
CREATE TABLE price_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    watch_id INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    provider VARCHAR(100),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (watch_id) REFERENCES watches(id) ON DELETE CASCADE
);

-- Notifications
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Global Settings
CREATE TABLE settings (
    setting_key VARCHAR(50) PRIMARY KEY,
    setting_value VARCHAR(255)
);

-- System Metrics
CREATE TABLE system_metrics (
    metric_key VARCHAR(50) PRIMARY KEY,
    metric_value INT DEFAULT 0,
    last_updated DATE
);

-- CMS: Popular Destinations
CREATE TABLE destinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    price_estimate INT NOT NULL,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE
);

-- Initialize Defaults
INSERT INTO settings (setting_key, setting_value) VALUES ('provider_mode', 'mock');
INSERT INTO system_metrics (metric_key, metric_value, last_updated) VALUES ('api_usage_daily', 0, CURRENT_DATE);