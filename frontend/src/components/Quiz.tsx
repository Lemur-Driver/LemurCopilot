import { useState } from 'react'

export interface QuizQuestion {
  exerciseId: string
  question: string
  options: string[]
}

export interface QuizResultAnswer {
  exerciseId: string
  selectedIndex: number
}

export interface QuizAnswerResult extends QuizResultAnswer {
  correctIndex: number
  isCorrect: boolean
  explanation?: string
}

export interface QuizSubmissionResult {
  score: number
  passed: boolean
}

interface QuizProps {
  questions: QuizQuestion[]
  onAnswer: (answer: QuizResultAnswer) => Promise<QuizAnswerResult>
  onComplete: () => Promise<QuizSubmissionResult>
  onRetry?: () => Promise<void> | void
  onNextLesson?: () => void
  onExplain?: (question: QuizQuestion,selectedIndex: number) => void
}


function Quiz({
  questions,
  onAnswer,
  onComplete,
  onRetry,
  onNextLesson,
  onExplain,
}: QuizProps) {

  const [
    currentQuestion,
    setCurrentQuestion,
  ] = useState(0)

  const [
    selectedAnswer,
    setSelectedAnswer,
  ] = useState<number | null>(null)

  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [result, setResult] = useState<QuizSubmissionResult | null>(null)
  const [questionResults, setQuestionResults] = useState<QuizAnswerResult[]>([])

  const score = result?.score ?? 0
  const passed = result?.passed ?? false


  const question =
    questions[currentQuestion]


  const answerResult = questionResults.find(
    (answer) => answer.exerciseId === question.exerciseId,
  )
  const isCorrect = answerResult?.isCorrect ?? false


  const completeQuiz = async () => {
    setIsSaving(true)
    setSaveError(null)
    try {
      const submission = await onComplete()
      setResult(submission)
    } catch {
      setSaveError('No pudimos finalizar el quiz. Intenta nuevamente.')
    } finally {
      setIsSaving(false)
    }
  }

  const submitAnswer = async (index: number) => {
    if (isSaving) return
    setIsSaving(true)
    setSaveError(null)

    const answer: QuizResultAnswer = {
      exerciseId: question.exerciseId,
      selectedIndex: index,
    }

    try {
      const submittedResult = await onAnswer(answer)
      const existingResult = questionResults.some(
        (current) => current.exerciseId === question.exerciseId,
      )
      if (!existingResult) {
        setQuestionResults((current) => [...current, submittedResult])
      }

      if (currentQuestion === questions.length - 1) {
        try {
          const submission = await onComplete()
          setResult(submission)
        } catch {
          setSaveError('No pudimos finalizar el quiz. Intenta nuevamente.')
        }
      }
    } catch {
      setSaveError('No pudimos guardar tu respuesta. Intenta nuevamente.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleAnswer = (index: number) => {
    if (selectedAnswer !== null || isSaving || result !== null) return
    setSelectedAnswer(index)
    void submitAnswer(index)
  }

  const retryCurrentAnswer = () => {
    if (selectedAnswer === null || isSaving) return
    if (answerResult && currentQuestion === questions.length - 1) {
      void completeQuiz()
    } else {
      void submitAnswer(selectedAnswer)
    }
  }


  const retryQuiz = async () => {
    if (!onRetry || isSaving) return
    setIsSaving(true)
    setSaveError(null)
    try {
      await onRetry()
    } catch {
      setSaveError('No se pudo preparar otro quiz. Intenta nuevamente.')
    } finally {
      setIsSaving(false)
    }
  }

  const nextQuestion = () => {
    if (isSaving || !answerResult) return

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

            if (answerResult) {
              if (index === answerResult.correctIndex) {
                className += ' correct'
              } else if (index === selectedAnswer) {
                className += ' incorrect'
              }
            }


            return (
              <button
                key={index}
                className={className}
                disabled={selectedAnswer !== null || isSaving || result !== null}
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
            {answerResult
              ? (isCorrect ? '🎉 ¡Correcto!' : '💡 No exactamente.')
              : 'Revisando tu respuesta...'}
          </p>


          {answerResult?.explanation && (
            <p className="quiz-explanation">
              {answerResult.explanation}
            </p>
          )}

          {saveError && (
            <div className="quiz-completion-modal" role="alert">
              <p className="quiz-error">{saveError}</p>
              <button className="next-button" onClick={retryCurrentAnswer} disabled={isSaving}>
                Reintentar
              </button>
            </div>
          )}

          {answerResult && !isCorrect && (
            <button
              type="button"
              className="explain-button"
              onClick={() => {

                if (selectedAnswer === null) {
                  return
                }

                onExplain?.(
                  question,
                  selectedAnswer,
                )
              }}
            >
              💬 Explicar
            </button>
          )}


          {currentQuestion < questions.length - 1 && (
            <button
              className="next-button"
              onClick={nextQuestion}
              disabled={isSaving || answerResult === undefined}
            >
              Siguiente pregunta →
            </button>
          )}

          {currentQuestion === questions.length - 1 && (
            <div className="quiz-completion">
              {isSaving && <p>{answerResult ? 'Guardando tu resultado...' : 'Revisando tu respuesta...'}</p>}
              {result && !saveError && (
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
                    <button className="next-button" onClick={() => void retryQuiz()}>
                      Rehacer quiz
                    </button>
                  )}
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