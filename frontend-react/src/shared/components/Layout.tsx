import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../../features/auth/AuthContext'
import { SUPPORTED_LANGUAGES, type SupportedLanguage } from '../../i18n'
import { Footer } from './Footer'

const navKeys: { to: string; key: string }[] = [
  { to: '/dashboard', key: 'nav.dashboard' },
  { to: '/assistant', key: 'nav.assistant' },
  { to: '/weekly-report', key: 'nav.weeklyReport' },
  { to: '/goals', key: 'nav.goals' },
  { to: '/health', key: 'nav.health' },
  { to: '/finance', key: 'nav.finance' },
  { to: '/productivity', key: 'nav.productivity' },
  { to: '/learning', key: 'nav.learning' },
  { to: '/integrations', key: 'nav.integrations' },
  { to: '/billing', key: 'nav.billing' },
  { to: '/settings', key: 'nav.settings' },
]

export const Layout = () => {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const closeSidebar = () => setSidebarOpen(false)

  const setLang = (lng: SupportedLanguage) => {
    i18n.changeLanguage(lng)
  }

  return (
    <div className="app-shell">
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={closeSidebar}
        onKeyDown={(e) => e.key === 'Escape' && closeSidebar()}
        role="button"
        tabIndex={-1}
        aria-hidden={!sidebarOpen}
        aria-label={t('nav.closeMenu')}
      />
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <Link to="/dashboard" className="brand-link" onClick={closeSidebar}>
          <div className="brand">
            <div className="brand-title">LifePulse</div>
            <div className="brand-subtitle">{t('nav.brandSubtitle')}</div>
          </div>
        </Link>
        <nav className="nav">
          {navKeys.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
              onClick={closeSidebar}
            >
              {t(item.key)}
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
            aria-label={t('nav.openMenu')}
          >
            ☰
          </button>
          <div>
            <h2>{t('layout.greeting', { name: user?.full_name || user?.email || '' })}</h2>
            <p className="muted">{t('common.role')}: {user?.role ?? 'user'}</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="lang-switcher" aria-label="Language">
              {SUPPORTED_LANGUAGES.map((lng) => (
                <button
                  key={lng}
                  type="button"
                  className={`secondary small ${i18n.language?.startsWith(lng) ? 'active' : ''}`}
                  onClick={() => setLang(lng)}
                  aria-pressed={i18n.language?.startsWith(lng)}
                  style={{ minWidth: 32, padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                >
                  {lng.toUpperCase()}
                </button>
              ))}
            </span>
            <button onClick={logout} className="secondary">
              {t('common.signOut')}
            </button>
          </div>
        </header>
        <section className="content">
          <Outlet />
        </section>
        <Footer />
      </main>
    </div>
  )
}
