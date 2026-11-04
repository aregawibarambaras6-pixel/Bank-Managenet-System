-- ====================================================================
-- Apex Bank Management System - Analytical & Operational SQL Queries
-- ====================================================================

-- 1. Total Bank Liquidity & Deposit Summary
SELECT 
    account_type,
    COUNT(id) AS total_accounts,
    SUM(balance) AS total_holdings,
    AVG(balance) AS average_balance,
    MIN(balance) AS minimum_balance,
    MAX(balance) AS maximum_balance
FROM accounts
WHERE status = 'active'
GROUP BY account_type;

-- 2. Top Active Customers by Total Balance
SELECT 
    u.id AS user_id,
    u.full_name,
    u.email,
    COUNT(a.id) AS account_count,
    COALESCE(SUM(a.balance), 0.0) AS aggregate_net_worth
FROM users u
LEFT JOIN accounts a ON u.id = a.user_id
WHERE u.role = 'customer'
GROUP BY u.id, u.full_name, u.email
ORDER BY aggregate_net_worth DESC
LIMIT 10;

-- 3. High-Risk Transaction Audit (Java & SQL Risk Analysis)
SELECT 
    f.reference_id,
    f.account_number,
    f.amount,
    f.risk_score,
    f.risk_level,
    f.decision,
    f.rules_triggered,
    f.evaluated_at
FROM fraud_audit_logs f
WHERE f.risk_level IN ('HIGH', 'CRITICAL')
ORDER BY f.evaluated_at DESC;

-- 4. Daily Transaction Volume and Turnover Breakdown
SELECT 
    DATE(timestamp) AS transaction_date,
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_volume
FROM transactions
GROUP BY DATE(timestamp), transaction_type
ORDER BY transaction_date DESC;

-- 5. Customer Ledger Reconciliation with C++ Verification Checksums
SELECT 
    t.reference_id,
    t.timestamp,
    t.transaction_type,
    t.amount,
    t.balance_after,
    COALESCE(c.checksum_hash, 'UNVERIFIED') AS cpp_ledger_hash,
    COALESCE(c.verified, 0) AS is_tamper_free
FROM transactions t
LEFT JOIN ledger_checksums c ON t.reference_id = c.reference_id
ORDER BY t.timestamp DESC
LIMIT 50;

