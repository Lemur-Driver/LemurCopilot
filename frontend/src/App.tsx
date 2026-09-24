import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Lesson from './pages/Lesson'

function App() {
  return (
    <BrowserRouter>

      <Routes>

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