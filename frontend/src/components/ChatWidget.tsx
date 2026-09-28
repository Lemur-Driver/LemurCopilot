import {
  useState,
  type SyntheticEvent,
} from 'react'


// ============================================================
// TYPES
// ============================================================

interface ChatSource {
  topic: string | null
  title: string | null
  page: number | null
  score: number | null
}


interface ChatMessage {
  id: number

  role:
    | 'user'
    | 'assistant'

  content: string

  sources?: ChatSource[]
}


interface ChatApiMessage {
  role:
    | 'user'
    | 'assistant'

  content: string
}


// ============================================================
// API
// ============================================================

const API_URL =
  import.meta.env.VITE_API_URL ??
  'http://localhost:8000'


// ============================================================
// COMPONENT
// ============================================================

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

      role:
        'assistant',

      content:
        '¡Hola! Soy tu tutor de conducción. Pregúntame lo que quieras sobre conducción y seguridad vial.',

      sources: [],
    },
  ])


  // ========================================================
  // ENVIAR MENSAJE
  // ========================================================

  const handleSubmit = async (
    event:
      SyntheticEvent<HTMLFormElement>
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
    // HISTORIAL
    // ------------------------------------------------------
    //
    // Por ahora enviamos máximo los últimos 10 mensajes.
    // Así evitamos que el contexto crezca indefinidamente.
    // ------------------------------------------------------

    const history:
      ChatApiMessage[] =
      messages
        .slice(-10)
        .map(
          (chatMessage) => ({
            role:
              chatMessage.role,

            content:
              chatMessage.content,
          })
        )


    // ------------------------------------------------------
    // MENSAJE DEL USUARIO
    // ------------------------------------------------------

    const userMessage:
      ChatMessage = {

      id:
        Date.now(),

      role:
        'user',

      content:
        cleanMessage,

      sources:
        [],
    }


    // ------------------------------------------------------
    // ID DE LA RESPUESTA DEL ASISTENTE
    // ------------------------------------------------------
    //
    // Esta burbuja se crea VACÍA.
    //
    // Después iremos agregándole texto a medida que
    // llegan tokens desde FastAPI.
    // ------------------------------------------------------

    const assistantId =
      Date.now() + 1


    const assistantMessage:
      ChatMessage = {

      id:
        assistantId,

      role:
        'assistant',

      content:
        '',

      sources:
        [],
    }


    // ------------------------------------------------------
    // MOSTRAR AMBOS MENSAJES
    // ------------------------------------------------------

    setMessages(
      (currentMessages) => [
        ...currentMessages,
        userMessage,
        assistantMessage,
      ]
    )


    setMessage('')

    setLoading(true)


    // ======================================================
    // STREAMING
    // ======================================================

    try {

      const response =
        await fetch(
          `${API_URL}/chat/stream`,
          {
            method:
              'POST',

            headers: {
              'Content-Type':
                'application/json',
            },

            body:
              JSON.stringify({
                message:
                  cleanMessage,

                history,
              }),
          }
        )


      // ----------------------------------------------------
      // ERROR HTTP
      // ----------------------------------------------------

      if (!response.ok) {

        const errorData =
          await response
            .json()
            .catch(
              () => null
            )


        throw new Error(
          errorData?.detail ??
            `Error ${response.status}`
        )

      }


      // ----------------------------------------------------
      // VERIFICAR QUE EXISTA STREAM
      // ----------------------------------------------------

      if (!response.body) {

        throw new Error(
          'No se recibió un stream válido.'
        )

      }


      // ----------------------------------------------------
      // READER DEL STREAM
      // ----------------------------------------------------

      const reader =
        response.body.getReader()


      const decoder =
        new TextDecoder()


      let buffer = ''


      // ====================================================
      // LEER STREAM
      // ====================================================

      while (true) {

        const {
          value,
          done,
        } = await reader.read()


        if (done) {
          break
        }


        // --------------------------------------------------
        // Convertir bytes → texto
        // --------------------------------------------------

        buffer += decoder.decode(
          value,
          {
            stream: true,
          }
        )


        // --------------------------------------------------
        // El backend manda un JSON por línea.
        // --------------------------------------------------

        const lines =
          buffer.split('\n')


        // --------------------------------------------------
        // La última línea podría estar incompleta.
        //
        // La guardamos para juntarla con el siguiente chunk.
        // --------------------------------------------------

        buffer =
          lines.pop() ?? ''


        // --------------------------------------------------
        // Procesar eventos completos
        // --------------------------------------------------

        for (const line of lines) {

          const cleanLine =
            line.trim()


          if (!cleanLine) {
            continue
          }


          let streamEvent


          try {

            streamEvent =
              JSON.parse(
                cleanLine
              )

          } catch (error) {

            console.error(
              'Evento de stream inválido:',
              cleanLine,
              error
            )

            continue

          }


          // ==================================================
          // FUENTES
          // ==================================================

          if (
            streamEvent.type ===
              'sources'
          ) {

            setMessages(
              (currentMessages) =>
                currentMessages.map(
                  (chatMessage) => {

                    if (
                      chatMessage.id !==
                        assistantId
                    ) {

                      return chatMessage

                    }


                    return {
                      ...chatMessage,

                      sources:
                        streamEvent
                          .sources ??
                        [],
                    }

                  }
                )
            )

          }


          // ==================================================
          // TOKEN
          // ==================================================

          else if (
            streamEvent.type ===
              'token'
          ) {

            setMessages(
              (currentMessages) =>
                currentMessages.map(
                  (chatMessage) => {

                    if (
                      chatMessage.id !==
                        assistantId
                    ) {

                      return chatMessage

                    }


                    return {
                      ...chatMessage,

                      content:
                        chatMessage.content
                        +
                        (
                          streamEvent.content ??
                          ''
                        ),
                    }

                  }
                )
            )

          }


          // ==================================================
          // ERROR DEL STREAM
          // ==================================================

          else if (
            streamEvent.type ===
              'error'
          ) {

            throw new Error(
              streamEvent.message ??
                'Error generando la respuesta.'
            )

          }


          // ==================================================
          // FIN
          // ==================================================

          else if (
            streamEvent.type ===
              'done'
          ) {

            setLoading(false)

          }

        }

      }


      // ----------------------------------------------------
      // Si quedó algo en buffer al terminar,
      // intentamos procesarlo.
      // ----------------------------------------------------

      const finalLine =
        buffer.trim()


      if (finalLine) {

        try {

          const streamEvent =
            JSON.parse(
              finalLine
            )


          if (
            streamEvent.type ===
              'token'
          ) {

            setMessages(
              (currentMessages) =>
                currentMessages.map(
                  (chatMessage) =>

                    chatMessage.id ===
                      assistantId

                      ? {
                          ...chatMessage,

                          content:
                            chatMessage.content
                            +
                            (
                              streamEvent.content ??
                              ''
                            ),
                        }

                      : chatMessage
                )
            )

          }

        } catch (error) {

          console.error(
            'Último evento inválido:',
            finalLine,
            error
          )

        }

      }


    } catch (error) {

      console.error(
        'Error en chat:',
        error
      )


      // ----------------------------------------------------
      // MODIFICAR LA BURBUJA VACÍA
      // ----------------------------------------------------

      setMessages(
        (currentMessages) =>
          currentMessages.map(
            (chatMessage) => {

              if (
                chatMessage.id !==
                  assistantId
              ) {

                return chatMessage

              }


              return {
                ...chatMessage,

                content:
                  chatMessage.content ||
                  'No pude responder en este momento. Intenta nuevamente.',

                sources:
                  chatMessage.sources ??
                  [],
              }

            }
          )
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
                      ? 'Escribiendo...'
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
                  key={
                    chatMessage.id
                  }

                  className={
                    `chat-message ${
                      chatMessage.role
                    }`
                  }
                >

                  <div>

                    {/* ==================================== */}
                    {/* MENSAJE                              */}
                    {/* ==================================== */}

                    {
                      chatMessage.content && (

                        <div className="chat-message-bubble">

                          {
                            chatMessage.content
                          }

                        </div>

                      )
                    }


                    {/* ==================================== */}
                    {/* LOADING ANTES DEL PRIMER TOKEN       */}
                    {/* ==================================== */}

                    {
                      chatMessage.role ===
                        'assistant' &&

                      !chatMessage.content &&

                      loading && (

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

                      )
                    }


                    {/* ==================================== */}
                    {/* FUENTES                              */}
                    {/* ==================================== */}

                    {
                      chatMessage.role ===
                        'assistant' &&

                      chatMessage.sources &&

                      chatMessage.sources.length >
                        0 &&

                      chatMessage.content && (

                        <div className="chat-sources">

                          <div className="chat-sources-title">
                            📚 Fuentes
                          </div>


                          {
                            chatMessage.sources.map(
                              (
                                source,
                                index
                              ) => (

                                <div
                                  className="chat-source"

                                  key={
                                    `${source.topic}-${source.page}-${index}`
                                  }
                                >

                                  <span className="chat-source-topic">

                                    {
                                      source.topic ??
                                        'Manual'
                                    }

                                  </span>


                                  <span>

                                    {
                                      source.title ??
                                        'Manual de conducción'
                                    }


                                    {
                                      source.page !==
                                        null &&
                                      source.page !==
                                        undefined &&
                                      ` · pág. ${source.page}`
                                    }

                                  </span>

                                </div>

                              )
                            )
                          }

                        </div>

                      )
                    }

                  </div>

                </div>

              )
            )}

          </div>


          {/* ============================================== */}
          {/* INPUT                                          */}
          {/* ============================================== */}

          <form
            className="chat-input-area"

            onSubmit={
              handleSubmit
            }
          >

            <input
              type="text"

              value={
                message
              }

              onChange={
                (event) =>
                  setMessage(
                    event.target.value
                  )
              }

              placeholder={
                loading
                  ? 'Esperando respuesta...'
                  : 'Pregunta sobre conducción...'
              }

              maxLength={
                500
              }

              disabled={
                loading
              }
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