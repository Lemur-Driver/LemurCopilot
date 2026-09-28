import {
  BrowserRouter,
  Routes,
  Route,
} from 'react-router-dom'

import Home from './pages/Home'
import Lesson from './pages/Lesson'
import Login from './pages/Login'

import ChatWidget from './components/ChatWidget'


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/lesson/:lessonId"
          element={<Lesson />}
        />

      </Routes>

      <ChatWidget />

    </BrowserRouter>
  )
}


export default App