import { NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../../features/auth/AuthContext'

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/health', label: 'Health' },
  { to: '/finance', label: 'Finance' },
  { to: '/productivity', label: 'Productivity' },
  { to: '/learning', label: 'Learning' },
  { to: '/integrations', label: 'Integrations' },
  { to: '/billing', label: 'Billing' },
]

export const Layout = () => {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-title">Personal Dashboard</div>
          <div className="brand-subtitle">Life analytics</div>
        </div>
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
            <h2>Привет, {user?.full_name || user?.email}</h2>
            <p className="muted">Роль: {user?.role ?? 'user'}</p>
          </div>
          <button onClick={logout} className="secondary">
            Выйти
          </button>
        </header>
        <section className="content">
          <Outlet />
        </section>
      </main>
    </div>
  )
}
