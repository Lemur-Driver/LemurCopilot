import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { AuthContext } from './auth-context'
import type { AuthUser } from './auth-types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'lemur_access_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(Boolean(token))

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const authFetch = useCallback(async (path: string, init: RequestInit = {}) => {
    const headers = new Headers(init.headers)
    if (!headers.has('Content-Type') && init.body) headers.set('Content-Type', 'application/json')
    const currentToken = localStorage.getItem(TOKEN_KEY)
    if (currentToken) headers.set('Authorization', `Bearer ${currentToken}`)
    const response = await fetch(`${API_URL}${path}`, { ...init, headers })
    if (response.status === 401) logout()
    return response
  }, [logout])

  const login = useCallback((data: AuthUser & { access_token: string }) => {
    localStorage.setItem(TOKEN_KEY, data.access_token)
    setToken(data.access_token)
    setUser(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    if (!token) return

    let active = true
    void (async () => {
      try {
        const response = await fetch(`${API_URL}/students/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (response.ok && active) setUser(await response.json())
        if (response.status === 401 && active) logout()
      } catch {
        // La sesión se conserva para permitir reintentar si el backend no está disponible.
      } finally {
        if (active) setLoading(false)
      }
    })()

    return () => {
      active = false
    }
  }, [logout, token])

  const value = useMemo(() => ({ user, token, loading, login, logout, authFetch }), [user, token, loading, login, logout, authFetch])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

