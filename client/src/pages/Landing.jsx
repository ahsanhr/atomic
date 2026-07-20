// Landing.jsx — public landing page
//
// introduces Sprout as a gamified personal-finance application
//
// responsibilities:
//   - explain the main value of the app
//   - introduce Sprout and the room progression concept
//   - provide a Get Started button
//   - route new users to the authentication page
import NavBar from "../components/Navbar";

export default function Landing() {
  return (
    <div className="landing-page">
      <NavBar />

      <main className="landing-main">

        {/* Hero section */}
    <section className="hero-section">
      <div className="hero-image">
          <img src="https://images.vexels.com/media/users/3/192102/isolated/preview/e9487eea13eaa258311cae7954db98f4-hanukkah-coin-cute-color.png" 
          alt="Image" 
          />
      </div>

      <div className="hero-content">
          <h1>Budgeting you can finally commit to</h1>
          <p className="hero-subcopy">
              Ditch the spreadsheets, charts, and graphs,
              and finally sustainably improve your personal
              finance one day at a time.
          </p>

          <div className="hero-actions">
              <a href="/auth" className="primary-button">
                  Get Started
              </a>
              <a href="/login" className="secondary-button">
                  I already have an account
              </a>

          </div>

      </div>

</section>

        {/* First feature */}
        <section className="feature-section">

          <div className="feature-text">
            <h2>Budgeting, finally made fun</h2>

            <p>
              Budgeting with Atomic is made fun, accessible, and easy.
              With quick snapshots of daily financial decisions,
              you can earn XP and points to build out your room while
              achieving your personal finance goals.
            </p>
          </div>

          <div className="feature-image">
          <img src="/images/budgeting.svg" alt="Budgeting illustration" />
          </div>

        </section>

        {/* Second feature */}
        <section className="feature-section reverse">

          <div className="feature-image">
            <img src="/images/psychology.svg" alt="People working together" />
          </div>

          <div className="feature-text">
            <h2>Psychologically tested</h2>

            <p>
              We use proven gamified methods to keep you engaged with
              your finances instead of being pushed away.
            </p>
          </div>

        </section>

        {/* Third feature */}
        <section className="feature-section">

          <div className="feature-text">
            <h2>Keeps you coming back</h2>

            <p>
              Small financial wins lead to big rewards.
              We generate daily quests to encourage consistency.
            </p>
          </div>

          <div className="feature-image">
          <img src="/images/quests.svg" alt="Daily quests illustration" />
          </div>

        </section>

        {/* Fourth feature */}
        <section className="feature-section reverse">

          <div className="feature-image">
            <img src="/images/tailored.svg" alt="Personalized plan illustration" />
          </div>

          <div className="feature-text">
            <h2>Tailored to you</h2>

            <p>
              Use the power of a small daily habit of checking your
              finances every day, backed by tips tailored to keep
              you on track.
            </p>
          </div>

        </section>

      </main>
    </div>
  );
}
