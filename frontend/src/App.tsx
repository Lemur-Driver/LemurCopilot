import type React from 'react'
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom'

import Home from './pages/Home'
import Lesson from './pages/Lesson'
import Login from './pages/Login'

import ChatWidget from './components/ChatWidget'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth()
  if (loading) return null
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>

      <Routes>

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/"
          element={<ProtectedRoute><Home /></ProtectedRoute>}
        />

        <Route
          path="/lesson/:lessonId"
          element={<ProtectedRoute><Lesson /></ProtectedRoute>}
        />

      </Routes>

      <ChatWidget />

    </BrowserRouter>
    </AuthProvider>
  )
}


export default App