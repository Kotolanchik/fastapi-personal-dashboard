import { Link } from 'react-router-dom'

export const PrivacyPage = () => (
  <div className="legal-page">
    <div className="legal-content">
      <h1>Privacy Policy</h1>
      <p className="legal-updated">Last updated: January 2025</p>
      <p>
        LifePulse (&quot;we&quot;, &quot;our&quot;) respects your privacy. This policy describes how we collect,
        use, and protect your information when you use our service.
      </p>
      <h2>Information we collect</h2>
      <p>
        We collect the information you provide when registering (email, name) and the data you
        enter in the app (health, finance, productivity, learning entries). We use this to provide
        the dashboard and analytics.
      </p>
      <h2>How we use it</h2>
      <p>
        Your data is used to display your dashboard, charts, and insights. We do not sell your
        personal data to third parties.
      </p>
      <h2>Data security</h2>
      <p>
        We use industry-standard measures to protect your data. Access to the app is secured with
        authentication.
      </p>
      <p>
        For questions, contact us at the address provided in the app or on the website.
      </p>
      <Link to="/" className="legal-back">← Back to home</Link>
    </div>
  </div>
)
