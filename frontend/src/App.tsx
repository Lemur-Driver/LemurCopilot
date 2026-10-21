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
import Profile from './pages/Profile'
import InfoPage from './pages/InfoPage'

import AppShell from './components/AppShell'
import ChatWidget from './components/ChatWidget'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { ChatProvider } from './chat/ChatContext'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth()
  if (loading) return null
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

function AuthenticatedChatWidget() {
  const { token } = useAuth()
  return token ? <ChatWidget /> : null
}

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <BrowserRouter basename={import.meta.env.BASE_URL}>

        <Routes>

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/"
            element={<ProtectedRoute><AppShell><Home /></AppShell></ProtectedRoute>}
          />

          <Route
            path="/lesson/:lessonId"
            element={<ProtectedRoute><AppShell><Lesson /></AppShell></ProtectedRoute>}
          />

          <Route
            path="/profile"
            element={<ProtectedRoute><AppShell><Profile /></AppShell></ProtectedRoute>}
          />

          <Route path="/about" element={<AppShell><InfoPage /></AppShell>} />
          <Route path="/contact" element={<AppShell><InfoPage /></AppShell>} />
          <Route path="/privacy" element={<AppShell><InfoPage /></AppShell>} />
          <Route path="/terms" element={<AppShell><InfoPage /></AppShell>} />

        </Routes>

        <AuthenticatedChatWidget />

        </BrowserRouter>
      </ChatProvider>
    </AuthProvider>
  )
}


export default App