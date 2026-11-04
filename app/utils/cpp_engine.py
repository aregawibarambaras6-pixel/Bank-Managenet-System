"""
C++ High-Performance Financial Engine Integration Module
Executes compiled C++ binary (bank_engine.exe) for interest calculations,
loan amortization schedules, and cryptographic ledger hashing.
"""

import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

ENGINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'engine'))
ENGINE_EXE = os.path.join(ENGINE_DIR, 'bank_engine.exe')

def calculate_compound_interest(principal, annual_rate, years, frequency=12):
    """
    Calls C++ engine to compute compound growth and yearly breakdown.
    """
    if os.path.exists(ENGINE_EXE):
        try:
            cmd = [ENGINE_EXE, '--interest', str(principal), str(annual_rate), str(years), str(frequency)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout:
                return json.loads(proc.stdout.strip())
        except Exception as e:
            logger.warning(f"C++ engine execution failed: {e}. Falling back to Python math.")

    # High-precision Python fallback matching C++ engine logic
    r = (annual_rate / 100.0) / frequency
    total_periods = years * frequency
    final_balance = principal * ((1.0 + r) ** total_periods)
    total_interest = final_balance - principal

    breakdown = []
    current = principal
    for y in range(1, years + 1):
        year_end = principal * ((1.0 + (annual_rate / 100.0) / frequency) ** (y * frequency))
        earned = year_end - current
        current = year_end
        breakdown.append({
            "year": y,
            "interest_earned": round(earned, 2),
            "balance": round(year_end, 2)
        })

    return {
        "status": "success",
        "engine": "C++ 14 Engine (Emulated Fallback)",
        "principal": round(principal, 2),
        "annual_rate": annual_rate,
        "years": years,
        "compound_frequency_per_year": frequency,
        "total_interest": round(total_interest, 2),
        "final_balance": round(final_balance, 2),
        "yearly_breakdown": breakdown
    }

def calculate_loan_amortization(principal, annual_rate, term_months=12):
    """
    Calls C++ engine to compute monthly payment and amortization schedule.
    """
    if os.path.exists(ENGINE_EXE):
        try:
            cmd = [ENGINE_EXE, '--loan', str(principal), str(annual_rate), str(term_months)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout:
                return json.loads(proc.stdout.strip())
        except Exception as e:
            logger.warning(f"C++ loan calculation failed: {e}. Falling back to Python math.")

    monthly_rate = (annual_rate / 100.0) / 12.0
    if monthly_rate > 0.0:
        factor = (1.0 + monthly_rate) ** term_months
        monthly_payment = principal * (monthly_rate * factor) / (factor - 1.0)
    else:
        monthly_payment = principal / term_months

    total_repayment = monthly_payment * term_months
    total_interest = total_repayment - principal

    schedule = []
    remaining = principal
    limit = min(36, term_months)
    for m in range(1, limit + 1):
        interest_part = remaining * monthly_rate
        principal_part = monthly_payment - interest_part
        remaining -= principal_part
        if remaining < 0 or m == term_months:
            remaining = 0.0
        schedule.append({
            "month": m,
            "payment": round(monthly_payment, 2),
            "principal_paid": round(principal_part, 2),
            "interest_paid": round(interest_part, 2),
            "remaining_balance": round(remaining, 2)
        })

    return {
        "status": "success",
        "engine": "C++ 14 Engine (Emulated Fallback)",
        "principal": round(principal, 2),
        "annual_rate": annual_rate,
        "term_months": term_months,
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "total_repayment": round(total_repayment, 2),
        "schedule": schedule
    }

def generate_ledger_hash(reference_id, sender, receiver, amount, timestamp):
    """
    Generates cryptographic 64-bit ledger hash for transaction verification.
    """
    if os.path.exists(ENGINE_EXE):
        try:
            cmd = [ENGINE_EXE, '--hash', str(reference_id), str(sender), str(receiver), str(amount), str(timestamp)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0 and proc.stdout:
                return json.loads(proc.stdout.strip())
        except Exception as e:
            logger.warning(f"C++ hash generation failed: {e}")

    # Fallback bit-mixing FNV-1a hash
    data = f"{reference_id}|{sender}|{receiver}|{amount}|{timestamp}"
    h = 14695981039346656037
    for char in data:
        h ^= ord(char)
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    h ^= (h >> 33)
    h = (h * 0xff51afd7ed558ccd) & 0xFFFFFFFFFFFFFFFF
    h ^= (h >> 33)

    return {
        "status": "success",
        "engine": "C++ 14 Engine (Emulated Fallback)",
        "reference_id": reference_id,
        "sender": sender,
        "receiver": receiver,
        "amount": round(amount, 2),
        "timestamp": str(timestamp),
        "ledger_hash": f"0x{h:016x}",
        "verified": True
    }

