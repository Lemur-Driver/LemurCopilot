import LearningPath from '../components/LearningPath'
import { course } from '../data/course'

function Home() {
  return (
    <main className="home-page">

      <section className="hero">

        <div className="hero-content">

          <span className="eyebrow">
            🇨🇱 Adaptive Driving Tutor
          </span>

          <h1>
            Aprende a conducir.
            <br />
            <span>a tu propio ritmo.</span>
          </h1>

          <p>
            Un camino de aprendizaje adaptativo para preparar
            tu licencia de conducir Clase B.
          </p>

        </div>

        <div className="hero-lemur">
          🐒
        </div>

      </section>

      <section className="learning-section">

        <div className="section-title">
          <span>Tu progreso</span>
          <h2>Camino de aprendizaje</h2>
        </div>

        {course.map((unit) => (
          <LearningPath
            key={unit.id}
            unit={unit}
          />
        ))}

      </section>

    </main>
  )
}

export default Home