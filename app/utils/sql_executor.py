"""
Direct SQL Database Execution Engine
Provides raw SQL querying, database schema migrations, and admin analytics queries.
"""

import sqlite3
import os
import time

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'bank_system.db'))
SCHEMA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'schema.sql'))

def get_connection():
    """Returns a direct sqlite3 connection with row factory enabled."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database_schema():
    """Executes database/schema.sql to ensure all relational tables, indices, and audit structures exist."""
    if not os.path.exists(SCHEMA_FILE):
        return False, "Schema file not found."
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        return True, "Database schema synchronized successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def execute_raw_query(query_text, max_rows=100):
    """
    Executes a raw SQL statement against the SQLite database.
    Returns: {
        'success': bool,
        'columns': list[str],
        'rows': list[list],
        'row_count': int,
        'execution_time_ms': float,
        'error': str or None
    }
    """
    cleaned_query = query_text.strip()
    if not cleaned_query:
        return {'success': False, 'error': 'Query text cannot be empty.', 'columns': [], 'rows': [], 'row_count': 0, 'execution_time_ms': 0.0}

    conn = get_connection()
    start_time = time.time()
    try:
        cursor = conn.cursor()
        cursor.execute(cleaned_query)
        
        is_select = cleaned_query.upper().startswith(('SELECT', 'PRAGMA', 'EXPLAIN'))
        
        if is_select and cursor.description:
            columns = [col[0] for col in cursor.description]
            fetched_rows = cursor.fetchmany(max_rows)
            rows = [list(r) for r in fetched_rows]
            row_count = len(rows)
            conn.commit()
        else:
            conn.commit()
            columns = ['affected_rows']
            row_count = cursor.rowcount
            rows = [[row_count]]
            
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return {
            'success': True,
            'columns': columns,
            'rows': rows,
            'row_count': row_count,
            'execution_time_ms': elapsed_ms,
            'error': None
        }
    except Exception as err:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return {
            'success': False,
            'columns': [],
            'rows': [],
            'row_count': 0,
            'execution_time_ms': elapsed_ms,
            'error': str(err)
        }
    finally:
        conn.close()

def log_fraud_audit(reference_id, account_number, amount, risk_score, risk_level, decision, rules_triggered, recommendation):
    """Logs Java fraud detection assessment into SQL database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fraud_audit_logs 
            (reference_id, account_number, amount, risk_score, risk_level, decision, rules_triggered, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reference_id,
            account_number,
            amount,
            risk_score,
            risk_level,
            decision,
            ', '.join(rules_triggered) if isinstance(rules_triggered, list) else str(rules_triggered),
            recommendation
        ))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def log_ledger_checksum(reference_id, checksum_hash, verified=True):
    """Logs C++ cryptographic checksum into SQL database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO ledger_checksums (reference_id, checksum_hash, verified)
            VALUES (?, ?, ?)
        """, (reference_id, checksum_hash, 1 if verified else 0))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

