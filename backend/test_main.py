import os
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
import database
from main import app

@pytest.fixture(autouse=True)
def clean_db():
    database.init_db()
    with database.get_connection() as conn:
        conn.execute("DELETE FROM transactions")
        conn.commit()
    yield

def test_add_and_list_transaction():
    tx_id = database.add_transaction(
        amount=Decimal("150.50"),
        description="Groceries",
        category="Food",
        date_str="2026-10-14"
    )
    assert tx_id > 0
    txs = database.list_transactions()
    assert len(txs) == 1
    assert txs[0]["amount"] == Decimal("150.50")
    assert txs[0]["category"] == "Food"

def test_decimal_precision_no_float_rounding():
    database.add_transaction(Decimal("0.10"), "Step 1", "Misc", "2026-10-14")
    database.add_transaction(Decimal("0.20"), "Step 2", "Misc", "2026-10-14")
    balance = database.get_live_balance()
    assert balance == Decimal("0.30")
    assert str(balance) == "0.30"

def test_delete_transaction():
    tx_id = database.add_transaction(Decimal("50.00"), "Book", "Education", "2026-10-14")
    assert database.delete_transaction(tx_id) is True
    assert len(database.list_transactions()) == 0
    assert database.delete_transaction(9999) is False

def test_live_balance_calculation():
    database.add_transaction(Decimal("1000.00"), "Salary", "Income", "2026-10-01")
    database.add_transaction(Decimal("-250.75"), "Rent", "Housing", "2026-10-02")
    database.add_transaction(Decimal("-49.25"), "Dinner", "Food", "2026-10-03")
    balance = database.get_live_balance()
    assert balance == Decimal("700.00")

def test_spending_breakdown_aggregation():
    database.add_transaction(Decimal("-50.00"), "Lunch", "Food", "2026-10-10")
    database.add_transaction(Decimal("-30.00"), "Dinner", "Food", "2026-10-10")
    database.add_transaction(Decimal("-100.00"), "Subway", "Transport", "2026-10-11")
    breakdown = database.get_spending_breakdown()
    breakdown_map = {item["category"]: item["total"] for item in breakdown}
    assert breakdown_map["Food"] == Decimal("-80.00")
    assert breakdown_map["Transport"] == Decimal("-100.00")

def test_auth_protection_endpoints():
    os.environ["POCKETLEDGER_TOKEN"] = "secret-token-test"
    client = TestClient(app)
    
    # Missing auth
    res_no_auth = client.get("/transactions")
    assert res_no_auth.status_code == 401
    
    # Valid auth
    res_auth = client.get("/transactions", headers={"Authorization": "Bearer secret-token-test"})
    assert res_auth.status_code == 200
