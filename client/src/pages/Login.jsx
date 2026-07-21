import { useState } from "react";
import NavBar from "../components/Navbar";
import { logIn, TOKEN_KEY } from "../api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await logIn(email, password);
      localStorage.setItem(TOKEN_KEY, result.token);
      window.location.href = "/hub";
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <NavBar />
      <main className="auth-main">
        <form className="auth-card" onSubmit={handleSubmit}>
          <h1>Welcome back</h1>
          <div className="auth-fields">
            <input type="email" placeholder="Email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            <input type="password" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>
          <div className="auth-actions">
            {error && <p className="form-error">{error}</p>}
            <button type="submit" className="auth-primary-button" disabled={loading}>
              {loading ? "Logging in..." : "Log In"}
            </button>
            <a href="/signup" className="auth-secondary-button">Create an account</a>
          </div>
        </form>
      </main>
    </div>
  );
}
