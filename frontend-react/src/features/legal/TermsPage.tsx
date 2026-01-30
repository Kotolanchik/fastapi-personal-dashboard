import { Link } from 'react-router-dom'

export const TermsPage = () => (
  <div className="legal-page">
    <div className="legal-content">
      <h1>Terms of Use</h1>
      <p className="legal-updated">Last updated: January 2025</p>
      <p>
        By using LifePulse you agree to these terms. Please read them carefully.
      </p>
      <h2>Use of the service</h2>
      <p>
        LifePulse is a personal analytics dashboard. You must provide accurate information when
        registering and are responsible for keeping your account secure.
      </p>
      <h2>Acceptable use</h2>
      <p>
        You may not use the service for illegal purposes or to harm others. We may suspend or
        terminate accounts that violate these terms.
      </p>
      <h2>Disclaimer</h2>
      <p>
        The service is provided &quot;as is&quot;. We do not guarantee uninterrupted availability or
        that the analytics are suitable for any particular purpose.
      </p>
      <p>
        For questions, contact us at the address provided in the app or on the website.
      </p>
      <Link to="/" className="legal-back">← Back to home</Link>
    </div>
  </div>
)
