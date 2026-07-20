import NavBar from "../components/Navbar";

export default function Room() {
  return (
    <div className="simple-page">
      <NavBar />
      <main className="simple-card">
        <p className="eyebrow">Level 1</p>
        <h1>Your room</h1>
        <p>Your Sprout room will appear here as you build healthy money habits.</p>
      </main>
    </div>
  );
}
