-- ====================================================================
-- Apex Bank Management System - Relational SQL Database Schema (DDL)
-- Compatible with SQLite, PostgreSQL, and MySQL
-- ====================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'customer', -- 'customer', 'manager', 'admin'
    profile_picture VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bank Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    account_type VARCHAR(20) NOT NULL DEFAULT 'checking', -- 'checking', 'savings'
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(5) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- 'active', 'frozen', 'closed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. Transactions Ledger Table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_id VARCHAR(36) NOT NULL UNIQUE,
    account_id INTEGER NOT NULL,
    transaction_type VARCHAR(20) NOT NULL, -- 'deposit', 'withdrawal', 'transfer_in', 'transfer_out'
    amount DECIMAL(15, 2) NOT NULL,
    balance_after DECIMAL(15, 2) NOT NULL,
    description VARCHAR(255),
    related_account VARCHAR(30),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE
);

-- 4. Beneficiaries Directory Table
CREATE TABLE IF NOT EXISTS beneficiaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    account_number VARCHAR(30) NOT NULL,
    bank_name VARCHAR(100) DEFAULT 'Apex Bank',
    nickname VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 5. Enterprise Fraud Risk & Compliance Audit Table (Populated by Java Engine)
CREATE TABLE IF NOT EXISTS fraud_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_id VARCHAR(36) NOT NULL,
    account_number VARCHAR(30) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    risk_score INTEGER NOT NULL, -- 0 to 100
    risk_level VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    decision VARCHAR(20) NOT NULL, -- 'APPROVED', 'FLAGGED', 'REJECTED'
    rules_triggered TEXT,
    recommendation TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. High-Performance C++ Ledger Checksums Table (Populated by C++ Engine)
CREATE TABLE IF NOT EXISTS ledger_checksums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_id VARCHAR(36) NOT NULL UNIQUE,
    checksum_hash VARCHAR(64) NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT 1,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices for High Performance Queries
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts (account_number);
CREATE INDEX IF NOT EXISTS idx_accounts_user ON accounts (user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_ref ON transactions (reference_id);
CREATE INDEX IF NOT EXISTS idx_transactions_acc ON transactions (account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_time ON transactions (timestamp);
CREATE INDEX IF NOT EXISTS idx_fraud_ref ON fraud_audit_logs (reference_id);

