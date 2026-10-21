import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { AuthContext } from './auth-context'
import type { AuthUser } from './auth-types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'lemur_access_token'

const GUEST_KEY = 'lemur_guest_session'
const GUEST_TOKEN = 'demo-guest'

const guestUser: AuthUser = {
  id: 'guest',
  google_sub: '',
  email: '',
  name: 'Invitado',
  picture: null,
}

function getInitialToken(): string | null {
  const realToken = localStorage.getItem(TOKEN_KEY)
  if (realToken) return realToken

  return sessionStorage.getItem(GUEST_KEY) === '1'
    ? GUEST_TOKEN
    : null
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(getInitialToken)

  const [user, setUser] = useState<AuthUser | null>(
    token === GUEST_TOKEN ? guestUser : null
  )

  const [loading, setLoading] = useState(
    Boolean(token && token !== GUEST_TOKEN)
  )

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(GUEST_KEY)
    setToken(null)
    setUser(null)
    setLoading(false)
  }, [])

  const login = useCallback(
    (data: AuthUser & { access_token: string }) => {
      sessionStorage.removeItem(GUEST_KEY)
      localStorage.setItem(TOKEN_KEY, data.access_token)
      setToken(data.access_token)
      setUser(data)
      setLoading(false)
    },
    []
  )

  const loginGuest = useCallback(() => {
    // Solo se habilita en el sitio estático de demostración.
    if (import.meta.env.VITE_DEMO_MODE !== 'true') return

    localStorage.removeItem(TOKEN_KEY)
    sessionStorage.setItem(GUEST_KEY, '1')

    setToken(GUEST_TOKEN)
    setUser(guestUser)
    setLoading(false)
  }, [])

  const authFetch = useCallback(
    async (path: string, init: RequestInit = {}) => {
      if (token === GUEST_TOKEN) {
        const mockData: Record<string, unknown> = {
          '/students/me/mastery': { mastery: {} },
          '/students/me/dashboard': {
            xp: 0,
            preparation: 0,
            attempted_lessons: 0,
            completed_lessons: 0,
            current_streak_days: 0,
          },
          '/students/me/course-progress': { units: [] },
        }

        if (Object.prototype.hasOwnProperty.call(mockData, path)) {
          return new Response(JSON.stringify(mockData[path]), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        }

        return new Response(
          JSON.stringify({
            detail: 'Funcionalidad no disponible en modo demo',
          }),
          {
            status: 503,
            headers: { 'Content-Type': 'application/json' },
          }
        )
      }

      const headers = new Headers(init.headers)

      if (!headers.has('Content-Type') && init.body) {
        headers.set('Content-Type', 'application/json')
      }

      const currentToken = localStorage.getItem(TOKEN_KEY)

      if (currentToken) {
        headers.set('Authorization', `Bearer ${currentToken}`)
      }

      const response = await fetch(`${API_URL}${path}`, {
        ...init,
        headers,
      })

      if (response.status === 401) logout()
      return response
    },
    [logout, token]
  )

  useEffect(() => {
    if (!token || token === GUEST_TOKEN) {
      return
    }

    let active = true

    void (async () => {
      try {
        const response = await fetch(`${API_URL}/students/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (response.ok && active) {
          setUser(await response.json())
        }

        if (response.status === 401 && active) {
          logout()
        }
      } catch {
        // Conserva la sesión si el backend no responde.
      } finally {
        if (active) setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [logout, token])

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      loginGuest,
      logout,
      authFetch,
    }),
    [user, token, loading, login, loginGuest, logout, authFetch]
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

