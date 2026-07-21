import { useEffect, useState } from "react";
import NavBar from "../components/Navbar";
import {
  createPlaidLinkToken,
  createSandboxPublicToken,
  exchangePlaidToken,
  getDashboard,
  syncPlaidTransactions,
  TOKEN_KEY,
} from "../api";

export default function Hub() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [connecting, setConnecting] = useState(false);
  const authenticated = Boolean(localStorage.getItem(TOKEN_KEY));

  useEffect(() => {
    if (!authenticated) {
      window.location.href = "/login";
      return;
    }
    loadDashboard();
  }, [authenticated]);

  async function loadDashboard() {
    try {
      setDashboard(await getDashboard());
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function connectPlaid() {
    setError("");
    setMessage("");
    setConnecting(true);
    try {
      if (!window.Plaid) throw new Error("Plaid Link is still loading. Try again in a moment.");
      const { link_token: linkToken } = await createPlaidLinkToken();
      const handler = window.Plaid.create({
        token: linkToken,
        onSuccess: async (publicToken) => {
          try {
            await exchangePlaidToken(publicToken);
            const result = await syncPlaidTransactions();
            setMessage(`Plaid connected. ${result.added} transactions synced.`);
            await loadDashboard();
          } catch (requestError) {
            setError(requestError.message);
          } finally {
            setConnecting(false);
          }
        },
        onExit: () => setConnecting(false),
      });
      handler.open();
    } catch (requestError) {
      setError(requestError.message);
      setConnecting(false);
    }
  }

  async function connectSandbox() {
    setError("");
    setMessage("");
    setConnecting(true);
    try {
      const sandbox = await createSandboxPublicToken();
      if (sandbox.already_connected) {
        setMessage("Plaid Sandbox is already connected.");
        await loadDashboard();
        return;
      }
      const { public_token: publicToken } = sandbox;
      await exchangePlaidToken(publicToken);
      const result = await syncPlaidTransactions();
      setMessage(`Sandbox connected. ${result.added} transactions synced.`);
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setConnecting(false);
    }
  }

  return (
    <div className="simple-page">
      <main className="dashboard-page">
        <div className="dashboard-heading">
          <div>
            <p className="eyebrow">Financial hub</p>
            <h1>Your progress</h1>
          </div>
          <div className="dashboard-actions">
            <button className="primary-button dashboard-button" onClick={connectSandbox} disabled={connecting}>
              {connecting ? "Connecting..." : "Use Plaid Sandbox"}
            </button>
            <button className="secondary-button dashboard-button" onClick={connectPlaid} disabled={connecting}>
              Connect with Plaid Link
            </button>
          </div>
        </div>

        {error && <p className="form-error">{error}</p>}
        {message && <p className="status-message">{message}</p>}
        {!dashboard && !error && authenticated && <p className="dashboard-loading">Loading your dashboard...</p>}
        {dashboard && <DashboardCards dashboard={dashboard} />}
      </main>
    </div>
  );
}

function DashboardCards({ dashboard }) {
  const cards = [
    ["Income", dashboard.income],
    ["Expenses", dashboard.expenses],
    ["Net cash flow", dashboard.net_cash_flow],
    ["Recommended savings", dashboard.recommended_savings],
  ];

  return (
    <>
      <section className="dashboard-grid">
        {cards.map(([label, value]) => (
          <article className="dashboard-card" key={label}>
            <p>{label}</p>
            <strong>${Number(value || 0).toFixed(2)}</strong>
          </article>
        ))}
      </section>
      <section className="dashboard-panel">
        <h2>Recent transactions</h2>
        {dashboard.recent_transactions?.length ? (
          <div className="transaction-list">
            {dashboard.recent_transactions.map((transaction) => (
              <div className="transaction-row" key={transaction.id}>
                <span>{transaction.merchant || "Transaction"}</span>
                <span>${Math.abs(Number(transaction.amount || 0)).toFixed(2)}</span>
              </div>
            ))}
          </div>
        ) : <p>No transactions yet.</p>}
      </section>
    </>
  );
}
