import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import GoogleSignInButton, { type GoogleUser } from '../components/GoogleSignInButton'
import lemurImage from '../assets/icon.png'

function Login() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  function handleSuccess(user: GoogleUser) {
    // TODO: cuando el backend emita sesión propia, guardarla acá (ej. localStorage/cookie)
    // en lugar de solo loguear el perfil verificado.
    console.log('Usuario autenticado con Google:', user)
    setError(null)
    navigate('/')
  }

  function handleError(err: Error) {
    console.error('Error de login con Google:', err)
    setError('No pudimos iniciar sesión con Google. Intenta de nuevo.')
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

        {error && (
          <p className="login-error">{error}</p>
        )}

      </div>

    </main>
  )
}

export default Login