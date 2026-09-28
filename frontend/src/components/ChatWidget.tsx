import {
  useState,
  type SyntheticEvent,
} from 'react'


interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
}


interface ChatApiMessage {
  role: 'user' | 'assistant'
  content: string
}


interface ChatResponse {
  answer: string
}


const API_URL =
  import.meta.env.VITE_API_URL ??
  'http://localhost:8000'


function ChatWidget() {
  const [
    isOpen,
    setIsOpen,
  ] = useState(false)


  const [
    message,
    setMessage,
  ] = useState('')


  const [
    loading,
    setLoading,
  ] = useState(false)


  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>([
    {
      id: 1,
      role: 'assistant',
      content:
        '¡Hola! Soy tu tutor de conducción. Pregúntame lo que quieras sobre conducción y seguridad vial.',
    },
  ])


  // ========================================================
  // ENVIAR MENSAJE
  // ========================================================

  const handleSubmit = async (
    event: SyntheticEvent<HTMLFormElement>
  ) => {
    event.preventDefault()


    const cleanMessage =
      message.trim()


    if (
      !cleanMessage ||
      loading
    ) {
      return
    }


    // ------------------------------------------------------
    // Historial ANTERIOR al mensaje actual
    // ------------------------------------------------------

    const history: ChatApiMessage[] =
      messages.map(
        (chatMessage) => ({
          role: chatMessage.role,
          content: chatMessage.content,
        })
      )


    // ------------------------------------------------------
    // Mensaje usuario
    // ------------------------------------------------------

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: cleanMessage,
    }


    setMessages(
      (currentMessages) => [
        ...currentMessages,
        userMessage,
      ]
    )


    setMessage('')

    setLoading(true)


    // ------------------------------------------------------
    // Backend
    // ------------------------------------------------------

    try {

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            message: cleanMessage,
            history,
          }),
        }
      )


      if (!response.ok) {

        const errorData =
          await response
            .json()
            .catch(() => null)


        throw new Error(
          errorData?.detail ??
            `Error ${response.status}`
        )
      }


      const data:
        ChatResponse =
        await response.json()


      // ----------------------------------------------------
      // Respuesta asistente
      // ----------------------------------------------------

      const assistantMessage:
        ChatMessage = {

        id: Date.now() + 1,

        role: 'assistant',

        content:
          data.answer,
      }


      setMessages(
        (currentMessages) => [
          ...currentMessages,
          assistantMessage,
        ]
      )


    } catch (error) {

      console.error(
        'Error en chat:',
        error
      )


      const errorMessage:
        ChatMessage = {

        id: Date.now() + 1,

        role: 'assistant',

        content:
          'No pude responder en este momento. Intenta nuevamente.',
      }


      setMessages(
        (currentMessages) => [
          ...currentMessages,
          errorMessage,
        ]
      )


    } finally {

      setLoading(false)

    }
  }


  // ========================================================
  // UI
  // ========================================================

  return (
    <div className="chat-widget">

      {isOpen && (
        <section className="chat-panel">

          {/* ============================================== */}
          {/* HEADER                                         */}
          {/* ============================================== */}

          <header className="chat-header">

            <div className="chat-header-info">

              <div className="chat-avatar">
                🐒
              </div>


              <div>

                <strong>
                  Tutor de conducción
                </strong>

                <span>
                  {
                    loading
                      ? 'Pensando...'
                      : 'Asistente Clase B'
                  }
                </span>

              </div>

            </div>


            <button
              className="chat-close-button"
              onClick={() =>
                setIsOpen(false)
              }
              aria-label="Cerrar chat"
            >
              ×
            </button>

          </header>


          {/* ============================================== */}
          {/* MENSAJES                                       */}
          {/* ============================================== */}

          <div className="chat-messages">

            {messages.map(
              (chatMessage) => (

                <div
                  key={chatMessage.id}
                  className={
                    `chat-message ${
                      chatMessage.role
                    }`
                  }
                >

                  <div className="chat-message-bubble">

                    {
                      chatMessage.content
                    }

                  </div>

                </div>

              )
            )}


            {/* ============================================ */}
            {/* INDICADOR DE CARGA                           */}
            {/* ============================================ */}

            {loading && (

              <div
                className="
                  chat-message
                  assistant
                "
              >

                <div
                  className="
                    chat-message-bubble
                    chat-typing
                  "
                >
                  <span />
                  <span />
                  <span />
                </div>

              </div>

            )}

          </div>


          {/* ============================================== */}
          {/* INPUT                                          */}
          {/* ============================================== */}

          <form
            className="chat-input-area"
            onSubmit={handleSubmit}
          >

            <input
              type="text"
              value={message}
              onChange={(event) =>
                setMessage(
                  event.target.value
                )
              }
              placeholder={
                loading
                  ? 'Esperando respuesta...'
                  : 'Pregunta sobre conducción...'
              }
              maxLength={500}
              disabled={loading}
            />


            <button
              type="submit"
              className="chat-send-button"
              disabled={
                !message.trim() ||
                loading
              }
              aria-label="Enviar mensaje"
            >
              ➤
            </button>

          </form>

        </section>
      )}


      {/* ================================================== */}
      {/* BOTÓN FLOTANTE                                     */}
      {/* ================================================== */}

      <button
        className={
          `chat-floating-button ${
            isOpen
              ? 'open'
              : ''
          }`
        }
        onClick={() =>
          setIsOpen(
            (current) =>
              !current
          )
        }
        aria-label={
          isOpen
            ? 'Cerrar chat'
            : 'Abrir chat'
        }
      >
        {
          isOpen
            ? '×'
            : '💬'
        }
      </button>

    </div>
  )
}


export default ChatWidget