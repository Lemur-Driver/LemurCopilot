import { useNavigate } from 'react-router-dom'
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

      <div className="login-card">

        <div className="login-mascot">
          <img
            src={lemurImage}
            alt="Lemur, tu compañero de aprendizaje"
          />
        </div>

        <div className="login-copy">
          <strong>Lemur</strong>
          <span>Aprende a conducir</span>
        </div>

        <h1>Inicia sesión para continuar</h1>

        <p>
          Guarda tu progreso y retoma tu camino de aprendizaje
          donde lo dejaste.
        </p>

        <div className="login-button">
          <GoogleSignInButton onSuccess={handleSuccess} onError={handleError} />
        </div>

        {import.meta.env.VITE_DEMO_MODE === 'true' && (
            <button
              type="button"
              onClick={handleGuestLogin}
              className="guest-button"
            >
              Entrar como invitado
            </button>
          )}

        {error && (
          <p className="login-error">{error}</p>
        )}

      </div>

    </main>
  )
}

export default Login