


export default function NavBar() {
  return (
    <nav className="navbar">
      <a href="/" className="logo">
        <div className="logo-image"></div>
        <h2>Atomic</h2>
      </a>
      
      

      <div className="navbar-item">
        <a href="/hub">Hub</a>
        <a href="/room">Room</a>
        <a href="/quests">Quests</a>
        <a href="/roadmap">Roadmap</a>
      </div>
    </nav>
  );
}

