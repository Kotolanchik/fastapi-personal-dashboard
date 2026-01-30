import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../../features/auth/AuthContext'
import { Footer } from './Footer'

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/weekly-report', label: 'Weekly report' },
  { to: '/goals', label: 'Goals' },
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
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const closeSidebar = () => setSidebarOpen(false)

  return (
    <div className="app-shell">
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={closeSidebar}
        onKeyDown={(e) => e.key === 'Escape' && closeSidebar()}
        role="button"
        tabIndex={-1}
        aria-hidden={!sidebarOpen}
        aria-label="Close menu"
      />
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <Link to="/dashboard" className="brand-link" onClick={closeSidebar}>
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
              onClick={closeSidebar}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="topbar">
          <button
            type="button"
            className="sidebar-toggle secondary"
            onClick={() => setSidebarOpen((o) => !o)}
            aria-label="Open menu"
          >
            ☰
          </button>
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
