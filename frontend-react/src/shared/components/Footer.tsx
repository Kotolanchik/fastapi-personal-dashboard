import { Link } from 'react-router-dom'

export const Footer = () => (
  <footer className="app-footer">
    <Link to="/privacy">Privacy Policy</Link>
    <span className="footer-sep">·</span>
    <Link to="/terms">Terms of Use</Link>
  </footer>
)
