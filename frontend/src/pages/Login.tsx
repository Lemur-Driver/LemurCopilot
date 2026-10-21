import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import GoogleSignInButton, { type GoogleUser } from '../components/GoogleSignInButton'
import lemurImage from '../assets/icon.png'
import { useAuth } from '../auth/useAuth'

function Login() {
  const navigate = useNavigate()
  const { login, loginGuest} = useAuth()
  const [error, setError] = useState<string | null>(null)

  function handleSuccess(user: GoogleUser) {
    login(user)
    setError(null)
    navigate('/')
  }

  function handleError(err: Error) {
    console.error('Error de login con Google:', err)
    setError('No pudimos iniciar sesión con Google. Intenta de nuevo.')
  }

  function handleGuestLogin() {
    loginGuest()
    navigate('/')
  }

  return (
    <main className="login-page">
      <Link className="login-home-link" to="/about">Conoce Lemur <span aria-hidden="true">↗</span></Link>
      <div className="login-layout">
        <section className="login-story">
          <div className="login-brand"><span className="login-mascot"><img src={lemurImage} alt="" /></span><span><strong>Lemur</strong><small>Aprende a conducir</small></span></div>
          <div className="login-story-copy"><span className="section-kicker">Tu camino empieza aquí</span><h1>Una meta grande.<br /><span>Un paso a la vez.</span></h1><p>Prepárate para tu licencia Clase B con lecciones claras, práctica guiada y un progreso que siempre te acompaña.</p></div>
          <div className="login-trail" aria-label="Tu recorrido de aprendizaje"><span className="trail-stop complete">✓</span><i /><span className="trail-stop current">✦</span><i /><span className="trail-stop">3</span><i /><span className="trail-stop">4</span><small>Aprender · Practicar · Avanzar</small></div>
          <img className="login-story-mascot" src={lemurImage} alt="Tu compañero Lemur te espera para aprender" />
          <span className="login-sparkle sparkle-one" aria-hidden="true">✦</span><span className="login-sparkle sparkle-two" aria-hidden="true">✳</span>
        </section>
        <section className="login-card">
          <span className="login-card-kicker">Qué bueno tenerte aquí</span>
          <h2>Inicia sesión para continuar</h2>
          <p>Guarda tu progreso y retoma tu camino de aprendizaje donde lo dejaste.</p>
          <div className="login-button"><GoogleSignInButton onSuccess={handleSuccess} onError={handleError} /></div>
          {import.meta.env.VITE_DEMO_MODE === 'true' && <button type="button" onClick={handleGuestLogin} className="guest-button">Explorar como invitado <span aria-hidden="true">→</span></button>}
          {error && <p className="login-error" role="alert">{error}</p>}
          <div className="login-reassurance"><span aria-hidden="true">🔒</span> Tu progreso es personal y seguro.</div>
        </section>
      </div>
      <p className="login-legal">Al continuar, aceptas nuestros <Link to="/terms">Términos de uso</Link> y <Link to="/privacy">Política de privacidad</Link>.</p>
    </main>
  )
}

export default Login