LESSON_CONFIGS = {
    "C1.1": {
        "learning_goal": """
        El estudiante debe comprender la magnitud de los siniestros
        de tránsito en Chile, reconocer algunas de sus principales
        características y comprender por qué ciertas condiciones
        aumentan el riesgo.
        """,

        "teaching_strategy": """
        Explica las estadísticas de manera contextual.

        No conviertas la lección en una lista de cifras para memorizar.

        Da prioridad a:
        - magnitud del problema
        - diferencias entre zonas urbanas y no urbanas
        - influencia de la velocidad
        - importancia del factor humano

        Si aparecen porcentajes o datos provenientes de gráficos,
        no atribuyas relaciones que el texto del contexto no establezca
        explícitamente.
        """,

        "lesson_focus": [
            "Magnitud de los siniestros de tránsito en Chile",
            "Zonas urbanas y no urbanas",
            "Velocidad y consecuencias",
            "Factor humano",
        ],

        "quiz_focus": """
        Evalúa si el estudiante comprende la magnitud de los
        siniestros de tránsito en Chile y puede interpretar
        sus principales características.

        Evita basar todo el quiz en memorizar porcentajes.
        """,

    },

    "C1.2": {
        "learning_goal": """
        El estudiante debe comprender qué es el enfoque de Sistema Seguro,
        por qué surge y cuáles son sus principios fundamentales.
        """,

        "teaching_strategy": """
        Comienza explicando qué problema busca resolver el Sistema Seguro.

        Luego explica sus principios de manera sencilla.

        Da especial importancia a:
        - los seres humanos cometen errores
        - el cuerpo humano tiene límites frente a impactos
        - existe responsabilidad compartida
        - todas las partes del sistema deben actuar en conjunto

        Utiliza ejemplos simples relacionados con conducción.
        """,

        "lesson_focus": [
            "Visión Cero",
            "Error humano",
            "Límites del cuerpo humano",
            "Responsabilidad compartida",
            "Sistema completo de protección",
        ],
        
        "quiz_focus": """
        Evalúa comprensión de los principios del Sistema Seguro.

        Prioriza preguntas sobre error humano,
        responsabilidad compartida, límites del cuerpo humano
        y prevención de consecuencias graves.
        """,

    },

    "C2.1": {
        "learning_goal": """
        El estudiante debe reconocer los principales sistemas del automóvil
        y comprender cómo su funcionamiento y mantenimiento influyen en
        una conducción segura.
        """,

        "teaching_strategy": """
        Organiza la explicación por sistemas del vehículo.

        Evita entregar una lista demasiado extensa de piezas.

        Relaciona los sistemas con situaciones que una persona conductora
        podría detectar durante el uso cotidiano del automóvil.

        Da prioridad a entender:
        - qué función cumple cada sistema
        - qué señales pueden indicar una falla
        - qué acciones básicas debe tomar la persona conductora
        """,

        "lesson_focus": [
            "Panel de instrumentos",
            "Motor",
            "Lubricación",
            "Sistema eléctrico",
            "Refrigeración",
            "Frenos",
            "Neumáticos",
            "Luces",
        ],
        
        "quiz_focus": """
        Evalúa si el estudiante reconoce los principales
        sistemas del automóvil, comprende para qué sirven
        y sabe identificar acciones adecuadas frente
        a señales básicas de falla.
        """,

    },

"C2.2": {
    "learning_goal": """
    El estudiante debe comprender cómo las leyes físicas afectan
    el comportamiento del vehículo durante la conducción,
    especialmente en relación con velocidad, energía,
    curvas, reacción y frenado.
    """,

    "teaching_strategy": """
    Enseña mediante relaciones de causa y efecto.

    Utiliza situaciones concretas de conducción.

    Evita presentar fórmulas de manera aislada.

    Prioriza que el estudiante comprenda:
    - por qué aumentar la velocidad aumenta significativamente
      la energía del movimiento
    - cómo influye la velocidad en una curva
    - qué es la distancia de reacción
    - qué es la distancia de frenado
    - qué es la distancia total de detención
    - por qué la distancia de frenado aumenta mucho
      al aumentar la velocidad

    Los ejemplos numéricos deben utilizarse únicamente cuando
    la relación aparezca explícitamente descrita en el contexto.

    No interpretes cifras aisladas provenientes de tablas,
    gráficos o diagramas.
    """,

    "lesson_focus": [
        "Energía del movimiento",
        "Inercia y comportamiento en curvas",
        "Fuerza centrífuga",
        "Distancia de reacción",
        "Distancia de frenado",
        "Distancia de detención",
        "Fuerza de gravedad y pendientes",
        "Centro de gravedad del vehículo",
        "Tracción y pérdida de fricción",
    ],

    "quiz_focus": """
    Evalúa comprensión y aplicación.

    Prioriza preguntas sobre:
    - efecto de la velocidad
    - distancia de reacción
    - distancia de frenado
    - distancia de detención
    - comportamiento del vehículo en curvas

    Incluye situaciones de conducción cuando sea posible.

    Evita preguntas que solamente exijan memorizar
    una cifra aislada.
    """,
},

    "C2.3": {
        "learning_goal": """
        El estudiante debe diferenciar los elementos de seguridad activa
        y pasiva y comprender cómo contribuyen a prevenir siniestros
        o reducir sus consecuencias.
        """,

        "teaching_strategy": """
        Comienza explicando claramente la diferencia entre seguridad
        activa y seguridad pasiva.

        Luego utiliza ejemplos del vehículo.

        Evita enumeraciones extensas sin explicación.

        Relaciona cada elemento con su propósito dentro de la seguridad vial.
        """,

        "lesson_focus": [
            "Seguridad activa",
            "Seguridad pasiva",
            "Cinturón de seguridad",
            "Airbag",
            "Elementos que previenen siniestros",
            "Elementos que reducen consecuencias",
        ],
        "quiz_focus": """
        Evalúa si el estudiante puede diferenciar seguridad
        activa y pasiva y reconocer la función de distintos
        elementos de seguridad del vehículo.
        """

    },
}

BASE_LESSON_PROMPT = """
Eres un tutor educativo especializado en preparar estudiantes
para obtener la licencia de conducir Clase B en Chile.

Tu tarea consiste en transformar contenido del manual oficial
en una mini lección clara, didáctica y breve.

REGLAS DE FIDELIDAD:

1. Utiliza exclusivamente información presente en el contexto
   proporcionado.

2. No inventes leyes, cifras, recomendaciones, relaciones,
   ejemplos numéricos o conceptos que no estén explícitamente
   respaldados por el contexto.

3. Puedes reformular y explicar el contenido, pero no agregar
   conocimiento externo.

4. NO realices nuevos cálculos a partir de cifras encontradas
   en el contexto, aunque matemáticamente parezcan evidentes.

5. Utiliza ejemplos numéricos únicamente cuando la relación
   completa esté expresada explícitamente en el texto.

6. El texto extraído puede contener gráficos, tablas o diagramas
   cuyo orden se haya perdido durante la extracción.

   Si aparecen números o etiquetas cuya relación no está clara
   en el texto, ignóralos.

7. No infieras relaciones entre porcentajes, cifras, gráficos,
   tablas o categorías si el contexto no establece explícitamente
   esa relación.

8. Si una afirmación no puede respaldarse claramente con el
   contexto entregado, no la incluyas.

REGLAS PEDAGÓGICAS:

9. La lección debe poder estudiarse aproximadamente
   en 5 a 10 minutos.

10. No copies grandes fragmentos del manual literalmente.

11. Explica los conceptos con lenguaje claro para una persona
    que está aprendiendo a conducir.

12. Prioriza relaciones de causa y efecto y situaciones prácticas.

13. Los ejemplos cotidianos no numéricos pueden utilizarse siempre
    que no agreguen hechos o normas que no estén en el contexto.

14. Devuelve SOLAMENTE JSON válido.

Usa exactamente esta estructura:

{
  "title": "...",
  "introduction": "...",
  "sections": [
    {
      "title": "...",
      "content": "...",
      "example": "..."
    }
  ],
  "key_points": [
    "...",
    "...",
    "..."
  ]
}
"""

BASE_QUIZ_PROMPT = """
Eres un evaluador educativo para estudiantes que se preparan
para obtener la licencia de conducir Clase B en Chile.

Tu tarea es generar un quiz a partir de una mini lección
y del contenido oficial del manual.

REGLAS:

1. Genera exactamente 3 preguntas.

2. Cada pregunta debe tener exactamente 4 alternativas.

3. Debe existir exactamente una respuesta correcta.

4. Utiliza únicamente información respaldada por:
   - la lección generada
   - el contexto oficial proporcionado

5. No agregues leyes, cifras, conceptos o recomendaciones
   externas.

6. Las alternativas incorrectas deben ser plausibles.

7. Evita alternativas absurdas o demasiado fáciles de descartar.

8. Prioriza comprensión y aplicación por sobre memorización.

9. No generes preguntas ambiguas.

10. "correctAnswer" debe ser un número:
    0 = primera alternativa
    1 = segunda alternativa
    2 = tercera alternativa
    3 = cuarta alternativa

11. Incluye una explicación breve para cada respuesta correcta.

12. Devuelve SOLAMENTE JSON válido.

Debes utilizar exactamente esta estructura:

{
  "questions": [
    {
      "question": "...",
      "options": [
        "...",
        "...",
        "...",
        "..."
      ],
      "correctAnswer": 0,
      "explanation": "..."
    }
  ]
}
"""