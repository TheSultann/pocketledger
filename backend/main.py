import csv
import io
import os
import io
import csv
from decimal import Decimal
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Header, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

import database

app = FastAPI(title="PocketLedger API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    database.init_db()

def verify_token(authorization: Optional[str] = Header(None)):
    expected_token = os.environ.get("POCKETLEDGER_TOKEN", "dev-token-123")
    if not authorization or authorization != f"Bearer {expected_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., description="Monetary amount (positive for income, negative for expense)")
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    date: str = Field(..., description="ISO Date string (YYYY-MM-DD)")

class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    description: str
    category: str
    date: str

class BreakdownItem(BaseModel):
    category: str
    total: Decimal

class BalanceResponse(BaseModel):
    balance: Decimal

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PocketLedger API"}

@app.post("/transactions", response_model=TransactionResponse, dependencies=[Depends(verify_token)])
def create_transaction(item: TransactionCreate):
    tx_id = database.add_transaction(
        amount=item.amount,
        description=item.description,
        category=item.category,
        date_str=item.date
    )
    return {
        "id": tx_id,
        "amount": item.amount,
        "description": item.description,
        "category": item.category,
        "date": item.date
    }

@app.get("/transactions", response_model=List[TransactionResponse], dependencies=[Depends(verify_token)])
def get_transactions():
    return database.list_transactions()

@app.delete("/transactions/{tx_id}", dependencies=[Depends(verify_token)])
def delete_transaction(tx_id: int):
    success = database.delete_transaction(tx_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "deleted", "id": tx_id}

@app.get("/balance", response_model=BalanceResponse, dependencies=[Depends(verify_token)])
def get_balance():
    return {"balance": database.get_live_balance()}

@app.get("/breakdown", response_model=List[BreakdownItem], dependencies=[Depends(verify_token)])
def get_breakdown():
    return database.get_spending_breakdown()


@app.get("/transactions/export", dependencies=[Depends(verify_token)])
def export_transactions_csv():
    """Export all transactions as a CSV file download."""
    transactions = database.list_transactions()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "description", "category", "amount"])
    for tx in transactions:
        writer.writerow([tx["id"], tx["date"], tx["description"], tx["category"], tx["amount"]])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )
