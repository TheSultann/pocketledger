# PocketLedger — Project Architecture & Agent Guide

PocketLedger is a personal finance tracker application designed for precision, testability, and clean architecture.

---

## 1. System Architecture

The application comprises two core services:

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     frontend/ (React 18)        │  HTTP │      backend/ (FastAPI)         │
│  - Vite dev server (:5173)      ├──────►│  - uvicorn server (:8000)       │
│  - Native SVG Category Chart    │       │  - SQLite Ledger Database       │
│  - Plain CSS (no external UI)   │       │  - Exact Decimal Arithmetic     │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

### Services Layout:
- **`backend/`**: Python 3.12, FastAPI, SQLite, Pydantic, pytest.
  - `main.py`: REST API routes with Bearer token authentication dependency.
  - `database.py`: Data layer managing parameterized queries and Decimal conversions.
  - `test_main.py`: Complete pytest test suite (6 tests passing).
- **`frontend/`**: TypeScript, React 18, Vite.
  - `src/App.tsx`: Unified dashboard handling transaction inputs, filters, live balance, and SVG charting.
  - `src/index.css`: Minimalist responsive CSS theme.

---

## 2. Authentication Model

- Authentication is enforced via a static Bearer token passed in the `Authorization` header.
- Expected value: `Bearer <POCKETLEDGER_TOKEN>`
- The token is loaded from `os.environ.get("POCKETLEDGER_TOKEN", "dev-token-123")`.
- All mutation and data access endpoints require token validation (`verify_token`).

---

## 3. Database Layer & Constraints

- **Engine:** SQLite (`pocketledger.db`).
- **Monetary Precision Rule:** All currency amounts are strictly modeled and calculated using `decimal.Decimal`. Amounts are serialized to text in SQLite to prevent IEEE 754 floating-point drift.
- **Double-Entry Discipline:** Positive amounts represent income, negative amounts represent expenditure.
- **Category Visualization:** Requirement F6 forbids third-party chart libraries (Recharts/Chart.js/D3). Category distribution is rendered natively via declarative SVG bars.

---

## 4. Developer Workflows

- Run all backend tests: `cd backend && pytest -v`
- Build frontend: `cd frontend && npm run build`
- Start full stack: `./start.sh`
