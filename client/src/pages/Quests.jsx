import NavBar from "../components/Navbar";

export default function Quests() {
  return <Page title="Quests" text="Daily and weekly money habits will show up here." />;
}

function Page({ title, text }) {
  return (
    <div className="simple-page">
      <NavBar />
      <main className="simple-card">
        <p className="eyebrow">Small wins</p>
        <h1>{title}</h1>
        <p>{text}</p>
      </main>
    </div>
  );
}
