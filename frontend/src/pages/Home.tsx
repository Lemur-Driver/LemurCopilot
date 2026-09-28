import { useEffect, useMemo, useState } from 'react'
import LearningPath from '../components/LearningPath'
import { course } from '../data/course'
import type { MasteryMap } from '../data/mastery'
import lemurImage from '../assets/icon.png'
import { useAuth } from '../auth/useAuth'

function Home() {
  const { user, authFetch } = useAuth()
  const [mastery, setMastery] = useState<MasteryMap>({})

  useEffect(() => {
    let active = true
    void authFetch('/students/me/mastery')
      .then(async (response) => {
        if (response.ok && active) {
          const data = await response.json() as { mastery?: MasteryMap }
          setMastery(data.mastery ?? {})
        }
      })
      .catch(() => undefined)
    return () => {
      active = false
    }
  }, [authFetch])

  const lessonEntries = useMemo(
    () => course.flatMap((unit) => unit.lessons),
    [],
  )
  const completedLessons = lessonEntries.filter(
    (lesson) => (mastery[lesson.id]?.best_score ?? 0) >= 0.6,
  ).length
  const preparation = lessonEntries.length
    ? Math.round((completedLessons / lessonEntries.length) * 100)
    : 0
  const attemptedLessons = lessonEntries.filter(
    (lesson) => (mastery[lesson.id]?.attempts ?? 0) > 0,
  ).length
  const currentLesson = lessonEntries.find(
    (lesson) => !(mastery[lesson.id]?.attempts),
  ) ?? lessonEntries[lessonEntries.length - 1]
  const currentUnit = course.find((unit) =>
    unit.lessons.some((lesson) => lesson.id === currentLesson?.id),
  )

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
            👋 {user?.name ?? 'Conductor'}
          </span>

          <span className="xp">
            ⭐ {completedLessons * 40} XP
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
            Hola, {user?.name?.split(' ')[0] ?? 'conductor'}
            <span>
              {' '}sigue aprendiendo a tu propio ritmo.
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
              {attemptedLessons ? 'Continuar aprendiendo' : 'Comenzar a aprender'}

              <span>
                →
              </span>
            </a>


            <div className="hero-progress">

              <strong>
                {currentUnit?.code ?? 'Tu camino'}
              </strong>

              <span>
                {preparation}% completado
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
            <strong>{preparation}%</strong>
            <span>Preparación</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon yellow">
            🔥
          </div>

          <div>
            <strong>{attemptedLessons} intentos</strong>
            <span>Racha actual</span>
          </div>

        </div>


        <div className="stat-card">

          <div className="stat-icon blue">
            ✓
          </div>

          <div>
            <strong>{completedLessons}</strong>
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
          mastery={mastery}
          />
        ))}

      </section>

    </main>
  )
}

export default Home