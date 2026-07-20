import NavBar from "../components/Navbar";

export default function Onboarding() {
  return <DemoPage title="Start your plan" text="Your income, expenses, and savings goals will live here." />;
}

function DemoPage({ title, text }) {
  return (
    <div className="simple-page">
      <NavBar />
      <main className="simple-card">
        <p className="eyebrow">Atomic</p>
        <h1>{title}</h1>
        <p>{text}</p>
      </main>
    </div>
  );
}
