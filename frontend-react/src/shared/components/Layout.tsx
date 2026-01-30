import { Link, NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../../features/auth/AuthContext'
import { Footer } from './Footer'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/weekly-report', label: 'Weekly report' },
  { to: '/health', label: 'Health' },
  { to: '/finance', label: 'Finance' },
  { to: '/productivity', label: 'Productivity' },
  { to: '/learning', label: 'Learning' },
  { to: '/integrations', label: 'Integrations' },
  { to: '/billing', label: 'Billing' },
  { to: '/settings', label: 'Settings' },
]

export const Layout = () => {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/dashboard" className="brand-link">
          <div className="brand">
            <div className="brand-title">LifePulse</div>
            <div className="brand-subtitle">Life analytics</div>
          </div>
        </Link>
        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <div>
            <h2>Hello, {user?.full_name || user?.email}</h2>
            <p className="muted">Role: {user?.role ?? 'user'}</p>
          </div>
          <button onClick={logout} className="secondary">
            Sign out
          </button>
        </header>
        <section className="content">
          <Outlet />
        </section>
        <Footer />
      </main>
    </div>
  )
}
