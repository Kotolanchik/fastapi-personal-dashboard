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
      <h2>Track health, finance, productivity & learning in one place</h2>
      <p>
        LifePulse helps you log daily metrics, see trends, and get simple insights. Add entries for
        sleep, income, deep work, study time, and more — then view charts and correlations on your
        dashboard.
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
    </section>
    <footer className="landing-footer">
      <Link to="/privacy">Privacy Policy</Link>
      <span className="sep">·</span>
      <Link to="/terms">Terms of Use</Link>
    </footer>
  </div>
)
