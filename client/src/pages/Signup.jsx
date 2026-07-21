import { useState } from "react";
import NavBar from "../components/Navbar";
import { signUp, TOKEN_KEY } from "../api";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = await signUp(username, email, password);
      localStorage.setItem(TOKEN_KEY, result.token);

      // After successful signup, go into onboarding flow
      window.location.href = "/onboarding";
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
          <h1>Sign Up</h1>

          <div className="auth-fields">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <div className="auth-actions">
            {error && <p className="form-error">{error}</p>}
            <button type="submit" className="auth-primary-button" disabled={loading}>
              {loading ? "Creating account..." : "Sign Up"}
            </button>

            <button className="auth-secondary-button" onClick={() => (window.location.href = "/onboarding")}>
              Welcome to Atomic
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
