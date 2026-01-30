import { Link } from 'react-router-dom'

export const LandingPage = () => (
  <div className="landing">
    <header className="landing-header">
      <h1 className="landing-logo">LifePulse</h1>
      <p className="landing-tagline">Your personal life analytics dashboard</p>
      <nav className="landing-actions">
        <Link to="/login" className="landing-btn secondary">
          Sign in
        </Link>
        <Link to="/register" className="landing-btn primary">
          Get started
        </Link>
      </nav>
    </header>
    <section className="landing-hero">
      <h2>See how sleep, money, and focus connect — decide from your own data</h2>
      <p>
        For anyone who tracks life in journals and spreadsheets: one place to log health, finance,
        productivity, and learning, then spot trends and correlations. Make better choices, not
        guesswork.
      </p>
      <ul className="landing-features">
        <li>Health: sleep, energy, wellbeing</li>
        <li>Finance: income and expenses</li>
        <li>Productivity: deep work hours, focus</li>
        <li>Learning: study hours and topics</li>
      </ul>
      <Link to="/register" className="landing-cta">
        Create free account
      </Link>
      <p className="landing-free-note">
        Free sign-up and core dashboard. Premium plans (deeper analytics, integrations) coming
        soon.
      </p>
    </section>
    <section className="landing-social">
      <p className="landing-social-text">
        Join others who track their life data
        {/* TODO: replace with real stats, e.g. "X+ entries logged" or "X users" */}
      </p>
    </section>
    <footer className="landing-footer">
      <Link to="/privacy">Privacy Policy</Link>
      <span className="sep">·</span>
      <Link to="/terms">Terms of Use</Link>
    </footer>
  </div>
)
