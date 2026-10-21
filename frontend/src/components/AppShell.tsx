import type { ReactNode } from 'react'
import { NavLink, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import lemurImage from '../assets/icon.png'

function AppShell({ children }: { children: ReactNode }) {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-frame">
      <header className="app-header">
        <Link className="brand app-brand" to="/" aria-label="Lemur, ir al inicio">
          <span className="brand-avatar"><img src={lemurImage} alt="" /></span>
          <span className="brand-copy"><strong>Lemur</strong><span>Aprende a conducir</span></span>
        </Link>
        <nav className="main-nav" aria-label="Navegación principal">
          {token ? <>
            <NavLink to="/" end>Aprender</NavLink>
            <NavLink to="/profile">Mi progreso</NavLink>
          </> : <>
            <NavLink to="/about">Quiénes somos</NavLink>
            <NavLink to="/contact">Contacto</NavLink>
          </>}
        </nav>
        <div className="header-account">
          {token ? <>
            <Link className="account-link" to="/profile">
              {user?.picture ? <img src={user.picture} alt="" /> : <span className="account-initial">{user?.name?.charAt(0) ?? 'L'}</span>}
              <span>{user?.name?.split(' ')[0] ?? 'Mi perfil'}</span>
            </Link>
            <button className="logout-button" type="button" onClick={handleLogout}>Salir</button>
          </> : <Link className="public-login-link" to="/login">Iniciar sesión <span aria-hidden="true">→</span></Link>}
        </div>
      </header>
      {children}
      <footer className="site-footer">
        <Link to="/about">Quiénes somos</Link>
        <Link to="/contact">Contacto</Link>
        <Link to="/privacy">Privacidad</Link>
        <Link to="/terms">Términos</Link>
        <span>© {new Date().getFullYear()} Lemur · Aprende a tu ritmo, conduce con seguridad.</span>
      </footer>
    </div>
  )
}

export default AppShell
