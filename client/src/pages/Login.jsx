import { useState } from "react";
import NavBar from "../components/Navbar";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
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
            <button type="submit" className="auth-primary-button">Log In</button>
            <a href="/signup" className="auth-secondary-button">Create an account</a>
          </div>
        </form>
      </main>
    </div>
  );
}
