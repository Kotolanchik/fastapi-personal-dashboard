import { Link } from 'react-router-dom'

export const NotFoundPage = () => (
  <div className="not-found">
    <h1>Page not found</h1>
    <p className="muted">The page you're looking for doesn't exist or has been moved.</p>
    <Link to="/" className="not-found-link">
      Back to home
    </Link>
  </div>
)
