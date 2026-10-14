import React, { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000';
const TOKEN = 'dev-token-123';

interface Transaction {
  id: number;
  amount: string;
  description: string;
  category: string;
  date: string;
}

interface BreakdownItem {
  category: string;
  total: string;
}

/**
 * Props for the BalanceCard component.
 * @property balance - The current live balance formatted as a signed string.
 */
interface BalanceCardProps {
  balance: string;
}

/**
 * BalanceCard displays the live ledger balance with color coding.
 */
const BalanceCard: React.FC<BalanceCardProps> = ({ balance }) => {
  const num = parseFloat(balance || '0');
  const isPos = num >= 0;
  return (
    <div className="card balance-card">
      <div>
        <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Live Ledger Balance</div>
        <div className={`balance-val ${isPos ? 'pos' : 'neg'}`}>
          {isPos ? `+€${num.toFixed(2)}` : `-€${Math.abs(num).toFixed(2)}`}
        </div>
      </div>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
        SQLite Persisted · Exact Decimal
      </div>
    </div>
  );
};

/**
 * Props for the CategoryChart component.
 * @property items - Aggregated spending breakdown items by category.
 */
interface CategoryChartProps {
  items: BreakdownItem[];
}

/**
 * CategoryChart renders horizontal bars using plain native SVG.
 * No external charting libraries used.
 */
const CategoryChart: React.FC<CategoryChartProps> = ({ items }) => {
  if (items.length === 0) {
    return <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No category data yet.</div>;
  }

  const maxVal = Math.max(...items.map((i) => Math.abs(parseFloat(i.total))), 1);

  return (
    <div className="card">
      <h3 style={{ marginBottom: '14px' }}>Category Breakdown (SVG Chart)</h3>
      <svg height={items.length * 40} width="100%">
        {items.map((item, idx) => {
          const val = parseFloat(item.total);
          const barWidth = Math.min((Math.abs(val) / maxVal) * 260, 260);
          const y = idx * 36;
          return (
            <g key={item.category} transform={`translate(0, ${y})`}>
              <text x="0" y="16" fill="var(--text-muted)" fontSize="12" fontWeight="500">
                {item.category}
              </text>
              <rect
                x="110"
                y="4"
                width={barWidth}
                height="16"
                rx="4"
                fill={val >= 0 ? 'var(--success)' : 'var(--primary)'}
              />
              <text x={120 + barWidth} y="16" fill="var(--text)" fontSize="12" fontWeight="600">
                €{Math.abs(val).toFixed(2)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

/**
 * Main application component managing state and operations.
 */
export default function App() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [balance, setBalance] = useState('0.00');
  const [breakdown, setBreakdown] = useState<BreakdownItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  // Form inputs
  const [amount, setAmount] = useState('');
  const [desc, setDesc] = useState('');
  const [cat, setCat] = useState('Food');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const authHeaders = {
    Authorization: `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  const loadData = async () => {
    try {
      const [tRes, bRes, kRes] = await Promise.all([
        fetch(`${API_BASE}/transactions`, { headers: authHeaders }),
        fetch(`${API_BASE}/balance`, { headers: authHeaders }),
        fetch(`${API_BASE}/breakdown`, { headers: authHeaders }),
      ]);
      if (tRes.ok) setTransactions(await tRes.json());
      if (bRes.ok) {
        const data = await bRes.json();
        setBalance(data.balance);
      }
      if (kRes.ok) setBreakdown(await kRes.json());
    } catch (err) {
      console.error('Failed to load data', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || !desc) return;
    try {
      const res = await fetch(`${API_BASE}/transactions`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          amount: parseFloat(amount),
          description: desc,
          category: cat,
          date,
        }),
      });
      if (res.ok) {
        setAmount('');
        setDesc('');
        loadData();
      }
    } catch (err) {
      console.error('Failed to add transaction', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE}/transactions/${id}`, {
        method: 'DELETE',
        headers: authHeaders,
      });
      if (res.ok) loadData();
    } catch (err) {
      console.error('Failed to delete transaction', err);
    }
  };

  const categories = ['ALL', ...Array.from(new Set(transactions.map((t) => t.category)))];
  const filtered =
    selectedCategory === 'ALL'
      ? transactions
      : transactions.filter((t) => t.category === selectedCategory);

  return (
    <div className="container">
      <header>
        <div>
          <h1>PocketLedger</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            FastAPI + React 18 · Decimal Precision · Bearer Auth
          </p>
        </div>
      </header>

      <BalanceCard balance={balance} />

      <div className="grid">
        <div className="card">
          <h3 style={{ marginBottom: '14px' }}>Add Transaction</h3>
          <form onSubmit={handleAdd}>
            <input
              type="text"
              placeholder="Description (e.g. Salary, Rent, Grocery)"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              required
            />
            <input
              type="number"
              step="0.01"
              placeholder="Amount (€, e.g. -45.50 for expense, 1500 for income)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
            <select value={cat} onChange={(e) => setCat(e.target.value)}>
              <option value="Food">Food</option>
              <option value="Housing">Housing</option>
              <option value="Transport">Transport</option>
              <option value="Income">Income</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Utilities">Utilities</option>
              <option value="Other">Other</option>
            </select>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <button type="submit">Record Transaction</button>
          </form>
        </div>

        <CategoryChart items={breakdown} />
      </div>

      <div className="card">
        <div className="filter-row">
          <h3>Transaction History</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Filter:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{ padding: '4px 8px' }}
            >
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                  No transactions recorded yet.
                </td>
              </tr>
            ) : (
              filtered.map((t) => {
                const isPos = parseFloat(t.amount) >= 0;
                return (
                  <tr key={t.id}>
                    <td>{t.date}</td>
                    <td style={{ fontWeight: 500 }}>{t.description}</td>
                    <td>
                      <span
                        style={{
                          background: 'rgba(255,255,255,0.06)',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                        }}
                      >
                        {t.category}
                      </span>
                    </td>
                    <td className={isPos ? 'pos' : 'neg'} style={{ fontWeight: 600 }}>
                      {isPos ? `+€${parseFloat(t.amount).toFixed(2)}` : `-€${Math.abs(parseFloat(t.amount)).toFixed(2)}`}
                    </td>
                    <td>
                      <button className="del-btn" onClick={() => handleDelete(t.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
