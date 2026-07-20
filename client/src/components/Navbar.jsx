export default function NavBar() {
  return (
    <nav className="navbar">
      <a href="/" className="logo">
        <div className="logo-image"></div>
        <h2 class = "Fredoka">Atomic</h2>
      </a>

      <div className="navbar-item">
        <a href="/auth">Sign Up</a>
        <a href="/login">Login</a>
      </div>
    </nav>
  );
}