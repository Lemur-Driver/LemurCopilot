import { useState } from 'react'

export interface QuizQuestion {
  question: string
  options: string[]
  correctAnswer: number
  explanation?: string
}

export interface QuizResultAnswer {
  question: string
  selectedIndex: number
  correctIndex: number
  isCorrect: boolean
}

interface QuizProps {
  questions: QuizQuestion[]
  onComplete?: (answers: QuizResultAnswer[]) => Promise<void> | void
  onRetry?: () => void
  onNextLesson?: () => void
}

function Quiz({
  questions,
  onComplete,
  onRetry,
  onNextLesson,
}: QuizProps) {

  const [
    currentQuestion,
    setCurrentQuestion,
  ] = useState(0)

  const [
    selectedAnswer,
    setSelectedAnswer,
  ] = useState<number | null>(null)

  const [answers, setAnswers] = useState<QuizResultAnswer[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [completed, setCompleted] = useState(false)

  const score = answers.length
    ? answers.filter((answer) => answer.isCorrect).length / answers.length
    : 0
  const passed = score === 1


  const question =
    questions[currentQuestion]


  const isCorrect =
    selectedAnswer !== null &&
    selectedAnswer ===
      question.correctAnswer


  const handleAnswer = (
    index: number
  ) => {

    if (
      selectedAnswer !== null
    ) {
      return
    }

    setSelectedAnswer(index)

    const answer: QuizResultAnswer = {
      question: question.question,
      selectedIndex: index,
      correctIndex: question.correctAnswer,
      isCorrect: index === question.correctAnswer,
    }
    const nextAnswers = [...answers, answer]
    setAnswers(nextAnswers)

    if (currentQuestion === questions.length - 1) {
      setIsSaving(true)
      setSaveError(null)
      void Promise.resolve(onComplete?.(nextAnswers))
        .then(() => setCompleted(true))
        .catch(() => setSaveError('No pudimos guardar tu resultado. Intenta nuevamente.'))
        .finally(() => setIsSaving(false))
    }
  }


  const nextQuestion = () => {

    setSelectedAnswer(null)

    if (
      currentQuestion <
      questions.length - 1
    ) {
      setCurrentQuestion(
        currentQuestion + 1
      )
    }

  }


  const progress =
    ((currentQuestion + 1) /
      questions.length) *
    100


  return (
    <section className="quiz">

      <div className="quiz-header">

        <div>

          <span className="quiz-label">
            🎯 Desafío
          </span>

          <h2>
            Demuestra lo que aprendiste
          </h2>

        </div>


        <div className="quiz-counter">
          {currentQuestion + 1}
          {' / '}
          {questions.length}
        </div>

      </div>


      <div className="quiz-progress">

        <div
          className="quiz-progress-fill"
          style={{
            width: `${progress}%`,
          }}
        />

      </div>


      <div className="quiz-question">

        <span>
          Pregunta {currentQuestion + 1}
        </span>

        <h3>
          {question.question}
        </h3>

      </div>


      <div className="quiz-options">

        {question.options.map(
          (option, index) => {

            let className =
              'quiz-option'

            if (
              selectedAnswer !== null
            ) {

              if (
                index ===
                question.correctAnswer
              ) {

                className +=
                  ' correct'

              } else if (
                index ===
                selectedAnswer
              ) {

                className +=
                  ' incorrect'

              }

            }


            return (
              <button
                key={index}
                className={className}
                onClick={() =>
                  handleAnswer(index)
                }
              >

                <span className="option-letter">
                  {String.fromCharCode(
                    65 + index
                  )}
                </span>


                <span className="option-text">
                  {option}
                </span>

              </button>
            )
          }
        )}

      </div>


      {selectedAnswer !== null && (
        <div className="quiz-feedback">

          <p>
            {isCorrect
              ? '🎉 ¡Correcto!'
              : '💡 No exactamente.'}
          </p>


          {question.explanation && (
            <p className="quiz-explanation">
              {question.explanation}
            </p>
          )}


          {currentQuestion < questions.length - 1 && (
            <button
              className="next-button"
              onClick={nextQuestion}
            >
              Siguiente pregunta →
            </button>
          )}

          {currentQuestion === questions.length - 1 && (
            <div className="quiz-completion">
              {isSaving && <p>Guardando tu resultado...</p>}
              {completed && !saveError && (
                <div className="quiz-completion-modal" role="status">
                  <h3>✅ Quiz completado</h3>
                  <p>
                    Obtuviste {Math.round(score * 100)}% y tu resultado fue guardado.
                  </p>
                  {passed ? (
                    <button className="next-button" onClick={onNextLesson}>
                      Siguiente lección →
                    </button>
                  ) : (
                    <button className="next-button" onClick={onRetry}>
                      Rehacer quiz
                    </button>
                  )}
                </div>
              )}
              {saveError && (
                <div className="quiz-completion-modal" role="alert">
                  <h3>No se pudo guardar el quiz</h3>
                  <p className="quiz-error">{saveError}</p>
                  <button className="next-button" onClick={onRetry}>
                    Intentar nuevamente
                  </button>
                </div>
              )}
            </div>
          )}

        </div>
      )}

    </section>
  )
}

export default Quiz