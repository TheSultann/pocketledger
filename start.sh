#!/usr/bin/env bash
set -e
export POCKETLEDGER_TOKEN="${POCKETLEDGER_TOKEN:-dev-token-123}"
cd backend && pip install -r requirements.txt -q && uvicorn main:app --reload --port 8000 &
cd ../frontend && npm install -q && npm run dev &
wait
