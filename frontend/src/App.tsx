import {
  BrowserRouter,
  Routes,
  Route,
} from 'react-router-dom'

import Home from './pages/Home'
import Lesson from './pages/Lesson'
import Login from './pages/Login'


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

    </BrowserRouter>
  )
}


export default App