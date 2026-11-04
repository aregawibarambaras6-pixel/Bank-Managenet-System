"""
Java 25 Enterprise Fraud Detection Integration Module
Calls the compiled Java FraudDetectionService class to perform AML and risk scoring.
"""

import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

SERVICES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'services'))
JAVA_CLASS_NAME = 'FraudDetectionService'

def analyze_transaction_risk(reference_id, transaction_type, amount, account_type='checking', status='active', daily_txn_count=1):
    """
    Invokes the Java 25 FraudDetectionService binary to assess risk.
    Returns a dictionary with status, risk_score, risk_level, and rules triggered.
    """
    cmd = [
        'java',
        '-cp',
        SERVICES_DIR,
        JAVA_CLASS_NAME,
        str(reference_id),
        str(transaction_type),
        str(float(amount)),
        str(account_type),
        str(status),
        str(int(daily_txn_count))
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if proc.returncode == 0 and proc.stdout:
            result = json.loads(proc.stdout.strip())
            return result
        else:
            logger.error(f"Java fraud engine stderr: {proc.stderr}")
    except Exception as e:
        logger.warning(f"Java fraud engine call failed: {e}. Falling back to internal rule evaluation.")

    # Python Fallback if Java process call is unavailable
    risk_score = 0
    rules = []
    if amount >= 10000.0:
        risk_score += 45
        rules.append("HIGH_VALUE_AML_THRESHOLD_EXCEEDED (Amount >= $10,000.00)")
    elif amount >= 5000.0:
        risk_score += 20
        rules.append("ELEVATED_VALUE_TRANSFER (Amount >= $5,000.00)")

    if daily_txn_count >= 10:
        risk_score += 35
        rules.append("VELOCITY_SPIKE_DETECTED (Daily transactions >= 10)")
    elif daily_txn_count >= 5:
        risk_score += 15
        rules.append("MODERATE_VELOCITY (Daily transactions >= 5)")

    if status.lower() != 'active':
        risk_score += 50
        rules.append("DORMANT_OR_RESTRICTED_ACCOUNT_ACTIVITY")

    if amount > 1000.0 and amount % 1000.0 == 0.0:
        risk_score += 10
        rules.append("ROUND_AMOUNT_STRUCTURING_CHECK")

    risk_score = min(risk_score, 100)
    if risk_score >= 75:
        risk_level = "CRITICAL"
        decision = "REJECTED"
        rec = "Transaction auto-blocked. Escalate to Compliance & Risk Officer."
    elif risk_score >= 40:
        risk_level = "HIGH"
        decision = "FLAGGED"
        rec = "Transaction held for secondary manual manager review."
    elif risk_score >= 20:
        risk_level = "MEDIUM"
        decision = "APPROVED"
        rec = "Approved with audit trail logging."
    else:
        risk_level = "LOW"
        decision = "APPROVED"
        rec = "Standard transaction verified successfully."

    return {
        "status": "success",
        "engine": "Java 25 Enterprise Fraud Engine (Emulated Fallback)",
        "reference_id": reference_id,
        "decision": decision,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendation": rec,
        "rules_triggered": rules
    }

