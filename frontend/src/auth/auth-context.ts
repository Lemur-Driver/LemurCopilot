import { createContext } from 'react'
import type { AuthUser } from './auth-types'

export interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (data: AuthUser & { access_token: string }) => void
  logout: () => void
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
