import LearningPath from '../components/LearningPath'
import { course } from '../data/course'
import lemurImage from '../assets/icon.png'

function Home() {
  return (
    <main className="home-page">

      {/* ======================
          TOP BAR
      ====================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-avatar">
            <img
              src={lemurImage}
              alt="Lemur"
            />
          </div>

          <div className="brand-copy">
            <strong>Lemur</strong>
            <span>
              Aprende a conducir
            </span>
          </div>

        </div>


        <div className="topbar-stats">

          <span className="streak">
            🔥 3 días
          </span>

          <span className="xp">
            ⭐ 120 XP
          </span>

        </div>

      </header>


      {/* ======================
          HERO
      ====================== */}

      <section className="hero">

        <div className="hero-road-decoration">
          <span />
          <span />
          <span />
        </div>


        <div className="hero-content">

          <span className="eyebrow">
            🇨🇱 Licencia Clase B
          </span>


          <h1>
            Aprende a conducir
            <span>
              {' '}a tu propio ritmo.
            </span>
          </h1>


          <p>
            Aprende las reglas del tránsito,
            practica y prepárate para tu licencia
            con un camino que se adapta a tu progreso.
          </p>


          <div className="hero-actions">

            <a
              href="#learning-path"
              className="primary-action"
            >
              Continuar aprendiendo

              <span>
                →
              </span>
            </a>


            <div className="hero-progress">

              <strong>
                Unidad 1
              </strong>

              <span>
                En progreso
              </span>

            </div>

          </div>

        </div>


        <div className="hero-mascot">

          <div className="mascot-circle" />

          <img
            src={lemurImage}
            alt="Lemur, tu compañero de aprendizaje"
          />

        </div>

      </section>


      {/* ======================
          QUICK STATS
      ====================== */}

      <section className="quick-stats">

        <div className="stat-card">

          <div className="stat-icon green">
            🎯
          </div>

          <div>
            <strong>59%</strong>
            <span>Preparación</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon yellow">
            🔥
          </div>

          <div>
            <strong>3 días</strong>
            <span>Racha actual</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon blue">
            ✓
          </div>

          <div>
            <strong>12</strong>
            <span>Clases completadas</span>
          </div>

        </div>

      </section>


      {/* ======================
          LEARNING PATH
      ====================== */}

      <section
        id="learning-path"
        className="learning-section"
      >

        <div className="section-title">

          <span>
            Tu camino
          </span>

          <h2>
            Sigue avanzando
          </h2>

          <p>
            Completa pequeñas lecciones,
            practica y demuestra lo que aprendiste.
          </p>

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