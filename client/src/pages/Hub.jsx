import NavBar from "../components/Navbar";

export default function Hub() {
  return (
    <Page title="Your progress" text="Your income, spending, savings, and quests will appear here." />
    
  );
}

function Page({ title, text }) {
  return (
    <div className="simple-page">
      <NavBar />
      <main className="simple-card">
        <p className="eyebrow">Financial hub</p>
        <h1>{title}</h1>
        <p>{text}</p>

    
      </main>
    </div>
  );
}
