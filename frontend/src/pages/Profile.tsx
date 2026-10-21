import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import ActivityCalendar from '../components/ActivityCalendar'
import { useAuth } from '../auth/useAuth'
import type { DashboardSummary, MasteryMap } from '../data/mastery'
import { course } from '../data/course'

interface ActivityResponse {
  days: string[]
}

function Profile() {
  const { user, authFetch } = useAuth()
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null)
  const [mastery, setMastery] = useState<MasteryMap>({})
  const [activityDays, setActivityDays] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let active = true
    void Promise.all([
      authFetch('/students/me/dashboard'),
      authFetch('/students/me/mastery'),
      authFetch('/students/me/activity?days=365'),
    ]).then(async ([dashboardResponse, masteryResponse, activityResponse]) => {
      if (!active) return
      if (!dashboardResponse.ok || !masteryResponse.ok || !activityResponse.ok) throw new Error('No se pudo cargar el progreso')
      const [dashboardData, masteryData, activityData] = await Promise.all([
        dashboardResponse.json() as Promise<DashboardSummary>,
        masteryResponse.json() as Promise<{ mastery?: MasteryMap }>,
        activityResponse.json() as Promise<ActivityResponse>,
      ])
      if (!active) return
      setDashboard(dashboardData)
      setMastery(masteryData.mastery ?? {})
      setActivityDays(activityData.days ?? [])
    }).catch(() => { if (active) setError(true) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [authFetch])

  const recentLessons = useMemo(() => Object.entries(mastery)
    .filter(([, entry]) => entry.last_seen)
    .sort(([, first], [, second]) => new Date(second.last_seen ?? 0).getTime() - new Date(first.last_seen ?? 0).getTime())
    .slice(0, 5), [mastery])
  const lessonTitles = useMemo(() => new Map(course.flatMap((unit) => unit.lessons.map((lesson) => [lesson.id, lesson.title] as const))), [])

  return (
    <main className="profile-page">
      <section className="profile-hero">
        <div className="profile-avatar">{user?.picture ? <img src={user.picture} alt="" /> : <span>{user?.name?.charAt(0) ?? 'L'}</span>}</div>
        <div><span className="section-kicker">Tu espacio Lemur</span><h1>Hola, {user?.name?.split(' ')[0] ?? 'conductor'} 👋</h1><p>Aquí tienes un vistazo a todo lo que has avanzado en tu camino.</p></div>
        <div className="profile-member"><span>Aprendiendo desde</span><strong>{user?.created_at ? new Intl.DateTimeFormat('es-CL', { month: 'long', year: 'numeric' }).format(new Date(user.created_at)) : 'Tu cuenta Lemur'}</strong></div>
      </section>

      {error && <div className="profile-error" role="alert"><strong>No pudimos cargar algunos datos.</strong><span>Revisa tu conexión e inténtalo de nuevo.</span></div>}
      {loading ? <div className="profile-loading" role="status">Preparando tu resumen de aprendizaje…</div> : <>
        <section className="profile-stats" aria-label="Resumen de progreso">
          <article className="profile-stat"><span className="profile-stat-icon green">✦</span><strong>{dashboard?.preparation ?? 0}%</strong><span>Preparación</span><small>Clases aprobadas del curso</small></article>
          <article className="profile-stat"><span className="profile-stat-icon blue">✓</span><strong>{dashboard?.completed_lessons ?? 0}</strong><span>Clases completadas</span><small>De {dashboard?.total_lessons ?? 0} disponibles</small></article>
          <article className="profile-stat"><span className="profile-stat-icon yellow">⭐</span><strong>{dashboard?.xp ?? 0} XP</strong><span>Puntos ganados</span><small>40 puntos por clase aprobada</small></article>
          <article className="profile-stat"><span className="profile-stat-icon peach">↻</span><strong>{dashboard?.total_attempts ?? 0}</strong><span>Quizzes realizados</span><small>Cada intento suma experiencia</small></article>
        </section>

        <ActivityCalendar activityDays={activityDays} currentStreak={dashboard?.current_streak_days ?? 0} longestStreak={dashboard?.longest_streak_days ?? 0} />

        <section className="recent-card">
          <div className="recent-heading"><div><span className="section-kicker">Tu recorrido</span><h2>Actividad reciente</h2></div><Link to="/#learning-path">Seguir aprendiendo <span aria-hidden="true">→</span></Link></div>
          {recentLessons.length ? <ul className="recent-list">{recentLessons.map(([lessonId, entry]) => <li key={lessonId}><span className="recent-check">✓</span><span className="recent-lesson"><strong>{lessonTitles.get(lessonId) ?? `Lección ${lessonId}`}</strong><small>{entry.attempts} {entry.attempts === 1 ? 'intento' : 'intentos'} · Mejor resultado {Math.round((entry.best_score ?? entry.score) * 100)}%</small></span><time dateTime={entry.last_seen ?? undefined}>{entry.last_seen ? new Intl.DateTimeFormat('es-CL', { day: 'numeric', month: 'short' }).format(new Date(entry.last_seen)) : ''}</time></li>)}</ul> : <div className="empty-activity"><span aria-hidden="true">🌱</span><strong>Tu historia empieza aquí</strong><p>Completa un quiz y volverás a encontrar tu progreso en este espacio.</p><Link to="/#learning-path">Explorar lecciones <span aria-hidden="true">→</span></Link></div>}
        </section>

        <section className="account-card"><div><span className="section-kicker">Tu cuenta</span><h2>Datos de perfil</h2><p>Esta información viene de tu cuenta de Google y se usa para identificar tu progreso.</p></div><dl><div><dt>Nombre</dt><dd>{user?.name ?? '—'}</dd></div><div><dt>Correo</dt><dd>{user?.email || 'Sesión de invitado'}</dd></div></dl></section>
      </>}
    </main>
  )
}

export default Profile
