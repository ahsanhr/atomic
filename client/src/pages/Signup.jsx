import { useState } from "react";
import NavBar from "../components/Navbar";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    console.log({
      email,
      password,
    });


  }

  return (
    <div className="auth-page">
      <NavBar />

      <main className="auth-main">
        <form className="auth-card" onSubmit={handleSubmit}>
          <h1>Sign Up</h1>

          <div className="auth-fields">
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
            <button type="submit" className="auth-primary-button">
              Sign Up
            </button>

            <a href="/login" className="auth-secondary-button">
              I already have an account
            </a>
          </div>
        </form>
      </main>
    </div>
  );
}
