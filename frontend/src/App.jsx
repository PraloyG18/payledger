import { useEffect, useState } from "react";
import "./App.css";

const MERCHANT_ID = 1;

function App() {
  const [balance, setBalance] = useState(0);
  const [payouts, setPayouts] = useState([]);
  const [amount, setAmount] = useState("");

  const fetchData = async () => {
    const res = await fetch(
      `http://127.0.0.1:8000/api/dashboard/${MERCHANT_ID}/`,
    );
    const data = await res.json();

    setBalance(data.balance);
    setPayouts(data.payouts);
  };

  const createPayout = async () => {
    if (!amount) return;

    const amountInPaise = Math.round(parseFloat(amount) * 100);

    await fetch(`http://127.0.0.1:8000/api/payout/${MERCHANT_ID}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify({ amount: amountInPaise }),
    });

    setAmount("");
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Payto</h2>
        <a href="#">Dashboard</a>
        <a href="#">Payouts</a>
        <a href="#">Settings</a>
      </div>

      {/* Main */}
      <div className="main">
        {/* Project Name */}
        <h1 className="project-name">PayLedger</h1>

        <h1 className="dashboard-title">Dashboard</h1>

        <div className="cards">
          <div className="card">
            <h3>Balance</h3>
            <p>₹{(balance / 100).toFixed(2)}</p>
          </div>

          <div className="card">
            <h3>Total Payouts</h3>
            <p>{payouts.length}</p>
          </div>
        </div>

        <div className="input-group">
          <input
            type="number"
            placeholder="Enter amount (₹)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <button onClick={createPayout}>Create Payout</button>
        </div>

        <div className="table">
          <div className="table-header">
            <span>Amount</span>
            <span>Status</span>
          </div>

          {payouts.map((p) => (
            <div key={p.id} className="table-row">
              <span>₹{(p.amount_paise / 100).toFixed(2)}</span>
              <span className={`status ${p.status}`}>{p.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
