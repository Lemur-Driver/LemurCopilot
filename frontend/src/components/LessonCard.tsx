import { useNavigate } from 'react-router-dom'
import type { Lesson } from '../data/course'
import type { MasteryEntry } from '../data/mastery'

interface LessonCardProps {
  lesson: Lesson
  number: number
  mastery?: MasteryEntry
  locked: boolean
}

function LessonCard({
  lesson,
  number,
  mastery,
  locked,
}: LessonCardProps) {
  const score = mastery?.best_score ?? 0
  const completed = score >= 0.6
  const started = Boolean(mastery?.attempts)
  const actionLabel =
  locked
    ? 'Bloqueada'
    : completed
      ? 'Repasar'
      : started
        ? 'Continuar'
        : 'Aprender'

  const navigate = useNavigate()

  return (
      <button
        className={
          locked
            ? 'lesson-card lesson-card-locked'
            : 'lesson-card'
        }
        disabled={locked}
        onClick={() => {
          if (locked) return

          navigate(
            `/lesson/${lesson.id}`
          )
        }}
      >

      <div className="lesson-node">

        <span className="lesson-node-number">
          {locked ? '🔒' : number}
        </span>

      </div>


      <div className="lesson-info">

        <div className="lesson-meta">

          <span className="lesson-code">
            {lesson.code}
          </span>

          <span className="lesson-duration">
            ⏱ 5–10 min
          </span>

        </div>


        <h3>
          {lesson.title}
        </h3>


        <p>
          {lesson.description}
        </p>

      </div>


      <div className="lesson-action">

        <span>
          {actionLabel}
        </span>

        <div className="lesson-arrow">
          →
        </div>

      </div>

    </button>
  )
}

export default LessonCard