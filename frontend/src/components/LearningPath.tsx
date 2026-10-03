import type { Unit } from '../data/course'
import LessonCard from './LessonCard'

import type { MasteryMap } from '../data/mastery'

interface LearningPathProps {
  unit: Unit
  mastery: MasteryMap
}

interface LearningPathProps {
  unit: Unit
  mastery: MasteryMap
  locked: boolean
}

function LearningPath({
  unit,
  mastery,
  locked,
}: LearningPathProps) {
  const completedLessons = unit.lessons.filter(
    (lesson) => (mastery[lesson.id]?.best_score ?? 0) >= 0.6,
  ).length
  const progress = unit.lessons.length
    ? Math.round((completedLessons / unit.lessons.length) * 100)
    : 0

  return (
    <section
      className={
        locked
          ? 'unit-section unit-section-locked'
          : 'unit-section'
      }
    >

      <div className="unit-header">

        <div className="unit-heading">

          <span className="unit-label">
            {unit.code}
          </span>


          <div>

            <h2>
              {unit.title}
            </h2>

            <p>
              {locked
                ? 'Completa la unidad anterior para desbloquear.'
                : 'Completa cada parada del camino.'}
            </p>

          </div>

        </div>


        <div className="unit-progress">

          <div className="unit-progress-info">

            <span>
              Progreso
            </span>

            <strong>
              {progress}%
            </strong>

          </div>


          <div className="unit-progress-track">

            <div
              className="unit-progress-fill"
              style={{
                width: `${progress}%`,
              }}
            />

          </div>

        </div>

      </div>


      <div className="learning-path">

        {unit.lessons.map(
          (lesson, index) => (
            <LessonCard
        key={lesson.id}
        lesson={lesson}
        number={index + 1}
        mastery={mastery[lesson.id]}
        locked={locked}
            />
          )
        )}

      </div>

    </section>
  )
}

export default LearningPath