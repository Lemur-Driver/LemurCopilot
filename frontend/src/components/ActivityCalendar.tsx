import { useMemo, useState } from 'react'

interface ActivityCalendarProps {
  activityDays: string[]
  currentStreak: number
  longestStreak: number
}

const monthFormatter = new Intl.DateTimeFormat('es-CL', { month: 'long', year: 'numeric' })
const weekdayLabels = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

function dateKey(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function ActivityCalendar({ activityDays, currentStreak, longestStreak }: ActivityCalendarProps) {
  const [visibleMonth, setVisibleMonth] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1))
  const activeDays = useMemo(() => new Set(activityDays), [activityDays])
  const firstWeekday = (visibleMonth.getDay() + 6) % 7
  const daysInMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + 1, 0).getDate()
  const today = dateKey(new Date())
  const dates = Array.from({ length: firstWeekday + daysInMonth }, (_, index) => {
    if (index < firstWeekday) return null
    return new Date(visibleMonth.getFullYear(), visibleMonth.getMonth(), index - firstWeekday + 1)
  })
  const isCurrentMonth = visibleMonth.getFullYear() === new Date().getFullYear() && visibleMonth.getMonth() === new Date().getMonth()

  function shiftMonth(amount: number) {
    setVisibleMonth((month) => new Date(month.getFullYear(), month.getMonth() + amount, 1))
  }

  return (
    <section className="activity-card" aria-labelledby="activity-heading">
      <div className="activity-heading-row">
        <div><span className="section-kicker">Tu constancia</span><h2 id="activity-heading">Un día a la vez</h2><p>Cada día de práctica cuenta, incluso los pequeños avances.</p></div>
        <div className="streak-badge" aria-label={`Racha actual de ${currentStreak} días`}><span aria-hidden="true">🔥</span><strong>{currentStreak}</strong><small>días seguidos</small></div>
      </div>
      <div className="calendar-toolbar">
        <button type="button" onClick={() => shiftMonth(-1)} aria-label="Mes anterior">←</button>
        <h3 aria-live="polite">{monthFormatter.format(visibleMonth)}</h3>
        <button type="button" onClick={() => shiftMonth(1)} disabled={isCurrentMonth} aria-label="Mes siguiente">→</button>
      </div>
      <div className="activity-calendar" role="grid" aria-label={`Calendario de actividad: ${monthFormatter.format(visibleMonth)}`}>
        {weekdayLabels.map((day, index) => <span className="calendar-weekday" role="columnheader" key={`${day}-${index}`} aria-label={['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'][index]}>{day}</span>)}
        {dates.map((date, index) => {
          if (!date) return <span className="calendar-day calendar-empty" role="gridcell" aria-hidden="true" key={`empty-${index}`} />
          const key = dateKey(date)
          const active = activeDays.has(key)
          return <span className={`calendar-day${active ? ' is-active' : ''}${key === today ? ' is-today' : ''}`} role="gridcell" aria-label={`${date.getDate()} de ${monthFormatter.format(visibleMonth)}${active ? ', actividad registrada' : ', sin actividad'}${key === today ? ', hoy' : ''}`} key={key}>{date.getDate()}{active && <span className="calendar-spark" aria-hidden="true">✦</span>}</span>
        })}
      </div>
      <div className="calendar-legend"><span><i /> Día con actividad</span><span>Tu mejor racha: <strong>{longestStreak} días</strong></span></div>
    </section>
  )
}

export default ActivityCalendar
