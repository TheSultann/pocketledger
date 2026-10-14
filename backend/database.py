import sqlite3
from decimal import Decimal
from typing import List, Dict, Any, Optional

DB_PATH = "pocketledger.db"

def init_db(db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def add_transaction(amount: Decimal, description: str, category: str, date_str: str, db_path: str = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO transactions (amount, description, category, date) VALUES (?, ?, ?, ?)",
            (str(amount), description, category, date_str)
        )
        conn.commit()
        return cursor.lastrowid

def list_transactions(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT id, amount, description, category, date FROM transactions ORDER BY date DESC, id DESC").fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "amount": Decimal(r["amount"]),
                "description": r["description"],
                "category": r["category"],
                "date": r["date"]
            })
        return result

def delete_transaction(tx_id: int, db_path: str = DB_PATH) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_live_balance(db_path: str = DB_PATH) -> Decimal:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT amount FROM transactions").fetchall()
        total = Decimal("0.00")
        for r in rows:
            total += Decimal(r["amount"])
        return total.quantize(Decimal("0.01"))

def get_spending_breakdown(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT category, amount FROM transactions").fetchall()
        totals: Dict[str, Decimal] = {}
        for r in rows:
            cat = r["category"]
            amt = Decimal(r["amount"])
            totals[cat] = totals.get(cat, Decimal("0.00")) + amt
        
        return [
            {"category": cat, "total": total.quantize(Decimal("0.01"))}
            for cat, total in sorted(totals.items())
        ]
