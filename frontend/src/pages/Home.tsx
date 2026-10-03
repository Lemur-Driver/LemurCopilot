import { useEffect, useMemo, useState } from 'react'
import LearningPath from '../components/LearningPath'
import { course } from '../data/course'
import type { DashboardSummary, MasteryMap } from '../data/mastery'
import lemurImage from '../assets/icon.png'
import { useAuth } from '../auth/useAuth'
import type { CourseProgressResponse, UnitProgress} from '../data/mastery'



function Home() {
  const { user, authFetch } = useAuth()
  const [mastery, setMastery] = useState<MasteryMap>({})
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null)
  const [ courseProgress, setCourseProgress] = useState<UnitProgress[]>([])

  useEffect(() => {
    let active = true
    void Promise.all([
      authFetch('/students/me/mastery'),
      authFetch('/students/me/dashboard'),
      authFetch('/students/me/course-progress'),
    ])
      .then(async ([
        masteryResponse,
        dashboardResponse,
        progressResponse,
      ]) => {

        if (!active) return

        if (masteryResponse.ok) {
          const data =
            await masteryResponse.json() as {
              mastery?: MasteryMap
            }

          setMastery(
            data.mastery ?? {}
          )
        }

        if (dashboardResponse.ok) {
          setDashboard(
            await dashboardResponse.json() as DashboardSummary
          )
        }

        if (progressResponse.ok) {
          const data =
            await progressResponse.json() as CourseProgressResponse

          setCourseProgress(
            data.units ?? []
          )
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
  const completedLessons = dashboard?.completed_lessons ?? 0
  const preparation = dashboard?.preparation ?? 0
  const attemptedLessons = dashboard?.attempted_lessons ?? 0
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
            ⭐ {dashboard?.xp ?? 0} XP
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
            <strong>{dashboard?.current_streak_days ?? 0} días</strong>
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


      {course.map((unit) => {

        const progress =
          courseProgress.find(
            (item) =>
              item.unit_id === unit.id
          )

        return (
          <LearningPath
            key={unit.id}
            unit={unit}
            mastery={mastery}
            locked={
              progress
                ? !progress.unlocked
                : unit.id !== 'unit-1'
            }
          />
        )
      })}

      </section>

    </main>
  )
}

export default Home