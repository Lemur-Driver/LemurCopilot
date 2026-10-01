LESSON_SEQUENCE = [
    "C1",
    "C1.1",
    "C1.2",

    "C2.1",
    "C2.2",
    "C2.3",

    "C3",

    "C4",
    "C4.1",
    "C4.2",
    "C4.3",
    "C4.4",
    "C4.5",
    "C4.6",
    "C4.7",

    "C5",
    "C5.1",

    "C6",
    "C6.1",
    "C6.2",
    "C6.3",
    "C6.4",
    "C6.5",
    "C6.6",

    "C7.1",
    "C7.2",
    "C7.3",
    "C7.4",

    "C8.1",
    "C8.2",
    "C8.3",

    "C9.1",
    "C9.2",
    "C9.3",
    "C9.4",
    "C9.5",
    "C9.6",

    "A1",
    "A2.1",
    "A2.2",
    "A3",
]


# ============================================================
# CONFIGURACIÓN PEDAGÓGICA
# ============================================================

LESSON_CONFIGS = {

    # ========================================================
    # C1 - LOS SINIESTROS DE TRÁNSITO
    # ========================================================

    "C1": {
        "learning_goal": """
        El estudiante debe comprender por qué los hechos viales
        deben entenderse como siniestros de tránsito y reconocer
        que muchas de sus causas y consecuencias pueden prevenirse.
        """,

        "teaching_strategy": """
        Explica primero la diferencia conceptual entre accidente
        y siniestro.

        Relaciona luego el comportamiento humano, los factores
        de riesgo y la responsabilidad de quienes utilizan las vías.

        Prioriza comprensión por sobre memorización.
        """,

        "lesson_focus": [
            "Concepto de siniestro de tránsito",
            "Diferencia entre accidente y siniestro",
            "Prevención",
            "Responsabilidad de las personas usuarias",
            "Consecuencias humanas y sociales",
            "Factores de riesgo",
        ],

        "quiz_focus": """
        Evalúa si el estudiante comprende por qué los siniestros
        no deben considerarse simplemente hechos azarosos y
        reconoce la importancia de la prevención.
        """,
    },


    "C1.1": {
        "learning_goal": """
        El estudiante debe interpretar las principales estadísticas
        de siniestros de tránsito en Chile e identificar factores
        asociados a su ocurrencia y gravedad.
        """,

        "teaching_strategy": """
        Presenta las cifras únicamente cuando estén claramente
        respaldadas por el contexto.

        Explica qué significan las estadísticas en términos de
        riesgo y prevención.

        No infieras relaciones que no estén expresadas en el manual.
        """,

        "lesson_focus": [
            "Cantidad de siniestros",
            "Personas fallecidas y lesionadas",
            "Zonas urbanas y no urbanas",
            "Velocidad y gravedad",
            "Falla humana",
            "Factores de incidencia",
        ],

        "quiz_focus": """
        Evalúa comprensión de las tendencias y relaciones
        explícitamente descritas por el manual.

        Evita exigir la memorización de cifras aisladas.
        """,
    },


    "C1.2": {
        "learning_goal": """
        El estudiante debe comprender el enfoque de Sistema Seguro
        y sus principios fundamentales para prevenir muertes y
        lesiones graves en el tránsito.
        """,

        "teaching_strategy": """
        Explica el cambio de enfoque desde intentar evitar todo
        error humano hacia diseñar un sistema capaz de proteger
        a las personas incluso cuando cometen errores.

        Relaciona los distintos componentes del sistema.
        """,

        "lesson_focus": [
            "Sistema Seguro",
            "Visión Cero",
            "Error humano",
            "Tolerancia del cuerpo humano",
            "Responsabilidad compartida",
            "Fortalecimiento de los componentes del sistema",
        ],

        "quiz_focus": """
        Evalúa comprensión de los principios del Sistema Seguro
        y de la responsabilidad compartida.
        """,
    },


    # ========================================================
    # C2 - PRINCIPIOS DE LA CONDUCCIÓN
    # ========================================================

    "C2.1": {
        "learning_goal": """
        El estudiante debe reconocer los principales sistemas
        del automóvil, comprender su función básica e identificar
        señales que pueden indicar problemas o necesidad de
        mantenimiento.
        """,

        "teaching_strategy": """
        Organiza la explicación por sistemas del vehículo.

        Relaciona cada sistema con su función y con situaciones
        prácticas de seguridad.

        Evita convertir la lección en una lista mecánica de piezas.
        """,

        "lesson_focus": [
            "Panel de instrumentos",
            "Motor",
            "Lubricación",
            "Sistema eléctrico",
            "Combustible",
            "Refrigeración",
            "Escape",
            "Transmisión",
            "Dirección",
            "Suspensión",
            "Frenos",
            "ABS",
            "Neumáticos",
            "Luces",
            "Espejos",
        ],

        "quiz_focus": """
        Evalúa si el estudiante reconoce la función de los
        principales sistemas y sabe cómo reaccionar ante
        señales básicas de falla.
        """,
    },


    "C2.2": {
        "learning_goal": """
        El estudiante debe comprender cómo las leyes físicas,
        la velocidad y las condiciones del entorno afectan
        el movimiento, el control y la detención del vehículo.
        """,

        "teaching_strategy": """
        Explica los conceptos mediante relaciones de causa y efecto.

        Diferencia claramente distancia de reacción, distancia
        de frenado y distancia de detención.

        Utiliza ejemplos numéricos solo cuando estén explícitamente
        respaldados por el manual.
        """,

        "lesson_focus": [
            "Energía del movimiento",
            "Inercia",
            "Curvas",
            "Fuerza centrífuga",
            "Distancia de reacción",
            "Distancia de frenado",
            "Distancia de detención",
            "Velocidad",
            "Pendientes",
            "Adherencia",
        ],

        "quiz_focus": """
        Evalúa comprensión de la influencia de la velocidad,
        la reacción, el frenado y las fuerzas físicas durante
        la conducción.
        """,
    },


    "C2.3": {
        "learning_goal": """
        El estudiante debe diferenciar los elementos de seguridad
        activa y pasiva y comprender cómo contribuyen a prevenir
        siniestros o reducir sus consecuencias.
        """,

        "teaching_strategy": """
        Comienza diferenciando seguridad activa y pasiva.

        Luego relaciona cada elemento con el momento en que
        protege a las personas: antes o durante un siniestro.
        """,

        "lesson_focus": [
            "Seguridad activa",
            "Seguridad pasiva",
            "Cinturón de seguridad",
            "Airbag",
            "Apoyacabezas",
            "Carrocería",
            "Sistemas de protección",
        ],

        "quiz_focus": """
        Evalúa si el estudiante distingue seguridad activa
        y pasiva y reconoce la finalidad de sus elementos.
        """,
    },


    # ========================================================
    # C3 - CONVIVENCIA VIAL
    # ========================================================

    "C3": {
        "learning_goal": """
        El estudiante debe comprender los principios de convivencia
        vial y reconocer la importancia del respeto, la empatía,
        la responsabilidad y la educación vial.
        """,

        "teaching_strategy": """
        Utiliza situaciones cotidianas de interacción entre
        diferentes personas usuarias de las vías.

        Prioriza actitudes y decisiones responsables.
        """,

        "lesson_focus": [
            "Convivencia vial",
            "Respeto",
            "Empatía",
            "Tolerancia",
            "Responsabilidad",
            "Educación vial",
            "Percepción del riesgo",
            "Conducción defensiva",
        ],

        "quiz_focus": """
        Evalúa decisiones y actitudes que favorecen una convivencia
        vial respetuosa y segura.
        """,
    },


    # ========================================================
    # C4 - LA PERSONA EN EL TRÁNSITO
    # ========================================================

    "C4": {
        "learning_goal": """
        El estudiante debe comprender cómo las capacidades humanas,
        la percepción, la atención y la experiencia influyen
        directamente en la conducción.
        """,

        "teaching_strategy": """
        Relaciona las limitaciones humanas con situaciones
        concretas de tránsito.

        Explica cómo la experiencia modifica la forma de percibir
        y responder al entorno.
        """,

        "lesson_focus": [
            "Percepción",
            "Atención",
            "Procesamiento de información",
            "Tiempo de reacción",
            "Experiencia",
            "Toma de decisiones",
            "Limitaciones humanas",
        ],

        "quiz_focus": """
        Evalúa cómo la percepción, atención y experiencia
        afectan las decisiones de conducción.
        """,
    },


    "C4.1": {
        "learning_goal": """
        El estudiante debe reconocer cómo las emociones y el
        estado psicológico pueden modificar su conducta al volante.
        """,

        "teaching_strategy": """
        Utiliza ejemplos de frustración, estrés, agresividad
        y empatía sin agregar situaciones no respaldadas
        por el contexto.

        Relaciona emociones con decisiones de riesgo.
        """,

        "lesson_focus": [
            "Equilibrio emocional",
            "Agresividad",
            "Estrés",
            "Impulsividad",
            "Empatía",
            "Autocontrol",
        ],

        "quiz_focus": """
        Evalúa si el estudiante reconoce cómo el estado emocional
        puede modificar la seguridad de sus decisiones.
        """,
    },


    "C4.2": {
        "learning_goal": """
        El estudiante debe identificar comportamientos sociales
        y personales que pueden aumentar el riesgo durante
        la conducción.
        """,

        "teaching_strategy": """
        Explica cómo determinadas decisiones pueden surgir por
        presión social, exceso de confianza u otras conductas
        de riesgo descritas en el manual.
        """,

        "lesson_focus": [
            "Conductas de riesgo",
            "Presión social",
            "Exceso de confianza",
            "Toma de decisiones",
            "Responsabilidad personal",
        ],

        "quiz_focus": """
        Evalúa la capacidad de identificar conductas riesgosas
        y escoger decisiones más seguras.
        """,
    },


    "C4.3": {
        "learning_goal": """
        El estudiante debe comprender los efectos del alcohol
        sobre la conducción, su relación con el riesgo de
        siniestros y las reglas descritas en el manual.
        """,

        "teaching_strategy": """
        Explica primero los efectos sobre las capacidades humanas.

        Después aborda alcoholemia, riesgo y eliminación del alcohol
        usando únicamente las cifras presentes en el contexto.
        """,

        "lesson_focus": [
            "Alcohol y conducción",
            "Alcoholemia",
            "Tiempo de reacción",
            "Percepción",
            "Riesgo de siniestro",
            "Eliminación del alcohol",
            "Falsa sensación de seguridad",
        ],

        "quiz_focus": """
        Evalúa efectos del alcohol, riesgos asociados y falsas
        creencias sobre cómo eliminarlo del organismo.
        """,
    },


    "C4.4": {
        "learning_goal": """
        El estudiante debe comprender cómo diferentes drogas
        pueden alterar las capacidades necesarias para conducir.
        """,

        "teaching_strategy": """
        Explica cada efecto descrito en el manual relacionándolo
        con percepción, reacción, concentración o conducta.

        No añadas efectos médicos externos.
        """,

        "lesson_focus": [
            "Drogas y conducción",
            "Cannabis",
            "Cocaína",
            "Percepción",
            "Tiempo de reacción",
            "Concentración",
            "Impulsividad",
            "Riesgo",
        ],

        "quiz_focus": """
        Evalúa si el estudiante reconoce cómo el consumo de
        drogas compromete capacidades necesarias para conducir.
        """,
    },


    "C4.5": {
        "learning_goal": """
        El estudiante debe comprender que determinadas enfermedades
        pueden afectar la capacidad para conducir y reconocer
        las precauciones descritas en el manual.
        """,

        "teaching_strategy": """
        Explica el tema desde la responsabilidad personal.

        Destaca la importancia de conocer la enfermedad,
        reconocer síntomas y seguir indicaciones profesionales.
        """,

        "lesson_focus": [
            "Enfermedades y conducción",
            "Síntomas",
            "Crisis",
            "Tratamiento",
            "Consulta médica",
            "Responsabilidad",
        ],

        "quiz_focus": """
        Evalúa decisiones seguras frente a enfermedades que
        pueden afectar la conducción.
        """,
    },


    "C4.6": {
        "learning_goal": """
        El estudiante debe reconocer que determinados medicamentos
        pueden afectar las capacidades necesarias para conducir.
        """,

        "teaching_strategy": """
        Relaciona los efectos descritos en el manual con la seguridad
        vial, especialmente somnolencia y disminución de capacidades.

        No entregues recomendaciones farmacológicas externas.
        """,

        "lesson_focus": [
            "Medicamentos",
            "Somnolencia",
            "Atención",
            "Antihistamínicos",
            "Interacciones",
            "Alcohol y medicamentos",
            "Consulta profesional",
        ],

        "quiz_focus": """
        Evalúa si el estudiante reconoce situaciones en las que
        un medicamento puede comprometer la conducción.
        """,
    },


    "C4.7": {
        "learning_goal": """
        El estudiante debe reconocer los síntomas y consecuencias
        del cansancio, sueño y fatiga y saber cuándo debe detener
        la conducción para descansar.
        """,

        "teaching_strategy": """
        Explica los efectos de la fatiga sobre atención, percepción,
        reacción y toma de decisiones.

        Destaca las recomendaciones de descanso descritas
        explícitamente en el manual.
        """,

        "lesson_focus": [
            "Fatiga",
            "Sueño",
            "Microsueños",
            "Tiempo de reacción",
            "Atención",
            "Viajes largos",
            "Descanso",
        ],

        "quiz_focus": """
        Evalúa reconocimiento de síntomas de fatiga y decisiones
        apropiadas para reducir el riesgo.
        """,
    },


    # ========================================================
    # C5 - USUARIOS VULNERABLES
    # ========================================================

    "C5": {
        "learning_goal": """
        El estudiante debe identificar a las y los usuarios
        vulnerables y comprender por qué requieren especial
        atención y protección.
        """,

        "teaching_strategy": """
        Explica las características que hacen más vulnerables
        a peatones, personas mayores, ciclistas y motociclistas.

        Utiliza situaciones de anticipación y prevención.
        """,

        "lesson_focus": [
            "Usuarios vulnerables",
            "Peatones",
            "Personas mayores",
            "Ciclistas",
            "Motociclistas",
            "Zona de incertidumbre",
            "Anticipación",
            "Protección",
        ],

        "quiz_focus": """
        Evalúa decisiones seguras al interactuar con usuarios
        vulnerables.
        """,
    },


    "C5.1": {
        "learning_goal": """
        El estudiante debe comprender las medidas de seguridad
        para transportar niñas y niños y la función de los
        Sistemas de Retención Infantil.
        """,

        "teaching_strategy": """
        Explica primero por qué niñas y niños necesitan sistemas
        específicos de protección.

        Luego presenta las reglas y condiciones descritas
        explícitamente en el manual.
        """,

        "lesson_focus": [
            "Niñas y niños como pasajeros",
            "Sistema de Retención Infantil",
            "Asientos traseros",
            "Cinturón de seguridad",
            "Peso",
            "Estatura",
            "Edad",
            "Responsabilidad de quien conduce",
        ],

        "quiz_focus": """
        Evalúa cuándo y cómo deben utilizarse sistemas de
        retención para niñas y niños.
        """,
    },


    # ========================================================
    # C6 - NORMAS DE CIRCULACIÓN
    # ========================================================

    "C6": {
        "learning_goal": """
        El estudiante debe comprender cómo se regula el tránsito
        y reconocer la jerarquía de las instrucciones y señales.
        """,

        "teaching_strategy": """
        Introduce las distintas formas de regulación del tránsito
        y explica cómo actuar cuando coinciden instrucciones.
        """,

        "lesson_focus": [
            "Normas de circulación",
            "Autoridad",
            "Semáforos",
            "Señales",
            "Demarcaciones",
            "Prioridad de instrucciones",
        ],

        "quiz_focus": """
        Evalúa la interpretación correcta de distintas formas
        de regulación del tránsito.
        """,
    },


    "C6.1": {
        "learning_goal": """
        El estudiante debe reconocer los principales tipos
        de señales de tránsito y comprender su función.
        """,

        "teaching_strategy": """
        Clasifica las señales según su finalidad.

        Prioriza interpretar el significado práctico sobre
        memorizar exclusivamente su apariencia.
        """,

        "lesson_focus": [
            "Señales reglamentarias",
            "Advertencia de peligro",
            "Señales informativas",
            "Semáforos",
            "Demarcaciones",
            "Interpretación de señales",
        ],

        "quiz_focus": """
        Evalúa clasificación e interpretación práctica
        de señales de tránsito.
        """,
    },


    "C6.2": {
        "learning_goal": """
        El estudiante debe comprender las principales reglas
        que ordenan la circulación y aplicar correctamente
        preferencias, virajes y cambios de posición.
        """,

        "teaching_strategy": """
        Utiliza escenarios sencillos de tránsito.

        Explica quién debe actuar y por qué según la regla
        descrita en el contexto.
        """,

        "lesson_focus": [
            "Reglas de circulación",
            "Preferencia de paso",
            "Cruces",
            "Virajes",
            "Cambio de pista",
            "Señalización de maniobras",
            "Distancia de seguridad",
        ],

        "quiz_focus": """
        Evalúa aplicación de reglas en situaciones prácticas
        de circulación.
        """,
    },


    "C6.3": {
        "learning_goal": """
        El estudiante debe comprender los límites de velocidad
        y saber adaptar su velocidad a las condiciones reales
        de circulación.
        """,

        "teaching_strategy": """
        Diferencia límite máximo de velocidad y velocidad
        razonable y prudente.

        Relaciona velocidad con visibilidad, vía, tránsito
        y condiciones ambientales.
        """,

        "lesson_focus": [
            "Límites de velocidad",
            "Zona urbana",
            "Zona no urbana",
            "Velocidad razonable y prudente",
            "Visibilidad",
            "Condiciones de la vía",
            "Riesgo",
        ],

        "quiz_focus": """
        Evalúa límites y decisiones de reducción de velocidad
        en diferentes circunstancias.
        """,
    },


    "C6.4": {
        "learning_goal": """
        El estudiante debe comprender cómo realizar encuentros,
        adelantamientos y sobrepasos de manera segura.
        """,

        "teaching_strategy": """
        Diferencia claramente adelantamiento y sobrepaso.

        Explica primero cuándo una maniobra está prohibida
        y luego las condiciones bajo las cuales puede realizarse.
        """,

        "lesson_focus": [
            "Adelantamiento",
            "Sobrepaso",
            "Visibilidad",
            "Eje de calzada",
            "Vehículos en sentido contrario",
            "Prohibiciones",
            "Maniobra segura",
        ],

        "quiz_focus": """
        Evalúa si el estudiante identifica cuándo puede o no
        realizar un adelantamiento o sobrepaso.
        """,
    },


    "C6.5": {
        "learning_goal": """
        El estudiante debe conocer las reglas para estacionar
        y detenerse sin crear riesgos ni obstrucciones.
        """,

        "teaching_strategy": """
        Relaciona las normas con situaciones de estacionamiento
        reales.

        Diferencia estacionamiento, detención y situaciones
        de emergencia.
        """,

        "lesson_focus": [
            "Estacionamiento",
            "Detención",
            "Distancia a la cuneta",
            "Lugares prohibidos",
            "Pendientes",
            "Estacionamiento nocturno",
            "Emergencias",
            "Chaleco de alta visibilidad",
        ],

        "quiz_focus": """
        Evalúa dónde y cómo se puede estacionar o detener
        un vehículo de forma segura.
        """,
    },


    "C6.6": {
        "learning_goal": """
        El estudiante debe comprender los riesgos de los cruces
        ferroviarios y aplicar las precauciones necesarias
        antes y durante el cruce.
        """,

        "teaching_strategy": """
        Destaca que el tren tiene prioridad y posee una gran
        distancia de detención.

        Explica qué verificar antes de cruzar y qué hacer
        frente a una emergencia.
        """,

        "lesson_focus": [
            "Cruces ferroviarios",
            "Preferencia del tren",
            "Barreras",
            "Señales luminosas y acústicas",
            "Detención",
            "Espacio disponible después del cruce",
            "Vehículo detenido sobre las vías",
        ],

        "quiz_focus": """
        Evalúa decisiones correctas antes de atravesar un cruce
        ferroviario y ante situaciones de emergencia.
        """,
    },


    # ========================================================
    # C7 - CIRCUNSTANCIAS ESPECIALES
    # ========================================================

    "C7.1": {
        "learning_goal": """
        El estudiante debe adaptar su conducción a condiciones
        de oscuridad o baja visibilidad.
        """,

        "teaching_strategy": """
        Relaciona iluminación, visibilidad, velocidad y distancia
        de seguridad.

        Explica los riesgos específicos de la conducción nocturna.
        """,

        "lesson_focus": [
            "Conducción nocturna",
            "Visibilidad",
            "Luces",
            "Encandilamiento",
            "Velocidad",
            "Distancia de seguridad",
        ],

        "quiz_focus": """
        Evalúa decisiones apropiadas para conducir con seguridad
        durante la noche.
        """,
    },


    "C7.2": {
        "learning_goal": """
        El estudiante debe comprender cómo la carga y los remolques
        afectan la estabilidad y maniobrabilidad del vehículo.
        """,

        "teaching_strategy": """
        Explica primero cómo cambia el comportamiento del automóvil.

        Luego presenta medidas para distribuir y asegurar la carga
        y utilizar remolques.
        """,

        "lesson_focus": [
            "Carga",
            "Distribución del peso",
            "Estabilidad",
            "Frenado",
            "Maniobrabilidad",
            "Sujeción de carga",
            "Remolque",
            "Enganche",
        ],

        "quiz_focus": """
        Evalúa consecuencias de una carga incorrecta y medidas
        para transportarla de forma segura.
        """,
    },


    "C7.3": {
        "learning_goal": """
        El estudiante debe comprender cómo incorporarse, circular
        y abandonar una autopista de forma segura.
        """,

        "teaching_strategy": """
        Explica el recorrido completo: preparación, incorporación,
        circulación y salida.

        Destaca observación, velocidad y distancia.
        """,

        "lesson_focus": [
            "Autopistas",
            "Pista de aceleración",
            "Incorporación",
            "Prioridad",
            "Distancia de seguridad",
            "Pista de desaceleración",
            "Salida",
            "Túneles",
            "Emergencias",
        ],

        "quiz_focus": """
        Evalúa decisiones correctas para ingresar, circular
        y salir de una autopista.
        """,
    },


    "C7.4": {
        "learning_goal": """
        El estudiante debe reconocer cómo las condiciones climáticas
        modifican la visibilidad, adherencia y control del vehículo.
        """,

        "teaching_strategy": """
        Explica cada condición climática mediante su efecto sobre
        el vehículo y la medida preventiva correspondiente.

        Prioriza relaciones causa-efecto.
        """,

        "lesson_focus": [
            "Lluvia",
            "Calzada mojada",
            "Adherencia",
            "Aquaplaning",
            "Niebla",
            "Viento",
            "Visibilidad",
            "Velocidad",
        ],

        "quiz_focus": """
        Evalúa decisiones ante lluvia, pérdida de adherencia
        y reducción de visibilidad.
        """,
    },


    # ========================================================
    # C8 - CONDUCCIÓN EFICIENTE
    # ========================================================

    "C8.1": {
        "learning_goal": """
        El estudiante debe comprender cómo preparar correctamente
        el vehículo y el viaje antes de iniciar la conducción.
        """,

        "teaching_strategy": """
        Organiza la explicación como una preparación previa
        al viaje.

        Relaciona mantenimiento, planificación y eficiencia.
        """,

        "lesson_focus": [
            "Planificación del viaje",
            "Estado del vehículo",
            "Neumáticos",
            "Carga",
            "Mantenimiento",
            "Preparación previa",
        ],

        "quiz_focus": """
        Evalúa qué aspectos deben revisarse antes de iniciar
        un viaje.
        """,
    },


    "C8.2": {
        "learning_goal": """
        El estudiante debe aplicar técnicas de conducción eficiente
        durante el trayecto sin comprometer la seguridad.
        """,

        "teaching_strategy": """
        Relaciona anticipación, velocidad y uso progresivo
        de los controles del vehículo con eficiencia y seguridad.
        """,

        "lesson_focus": [
            "Conducción eficiente",
            "Anticipación",
            "Aceleración",
            "Frenado",
            "Velocidad constante",
            "Uso de marchas",
            "Consumo",
        ],

        "quiz_focus": """
        Evalúa decisiones de conducción que favorecen eficiencia
        y seguridad durante el trayecto.
        """,
    },


    "C8.3": {
        "learning_goal": """
        El estudiante debe comprender que una conducción eficiente
        debe mantenerse siempre subordinada a la seguridad vial.
        """,

        "teaching_strategy": """
        Relaciona eficiencia energética con conducción preventiva,
        anticipación y control del vehículo.
        """,

        "lesson_focus": [
            "Seguridad",
            "Anticipación",
            "Conducción suave",
            "Distancia",
            "Control del vehículo",
            "Eficiencia y seguridad",
        ],

        "quiz_focus": """
        Evalúa cómo combinar eficiencia y seguridad sin sacrificar
        el control del vehículo.
        """,
    },


    # ========================================================
    # C9 - INFORMACIONES IMPORTANTES
    # ========================================================

    "C9.1": {
        "learning_goal": """
        El estudiante debe saber cómo actuar frente a un siniestro
        de tránsito y reconocer sus obligaciones básicas.
        """,

        "teaching_strategy": """
        Presenta las acciones en una secuencia lógica desde
        la detención hasta la solicitud de ayuda.

        Destaca seguridad y protección de las personas.
        """,

        "lesson_focus": [
            "Detenerse",
            "Proteger el lugar",
            "Prestar ayuda",
            "Avisar a la autoridad",
            "Personas lesionadas",
            "Responsabilidad",
        ],

        "quiz_focus": """
        Evalúa el orden y las acciones correctas tras participar
        o presenciar un siniestro.
        """,
    },


    "C9.2": {
        "learning_goal": """
        El estudiante debe reconocer las principales disposiciones
        y requisitos aplicables a los vehículos que circulan.
        """,

        "teaching_strategy": """
        Organiza los requisitos según documentación, estado
        del vehículo y obligaciones descritas en el manual.
        """,

        "lesson_focus": [
            "Documentación del vehículo",
            "Permiso de circulación",
            "Revisión técnica",
            "Seguro obligatorio",
            "Condiciones para circular",
        ],

        "quiz_focus": """
        Evalúa reconocimiento de los principales requisitos
        necesarios para circular.
        """,
    },


    "C9.3": {
        "learning_goal": """
        El estudiante debe comprender las responsabilidades
        legales y personales asociadas a conducir un vehículo.
        """,

        "teaching_strategy": """
        Relaciona acciones de conducción con sus responsabilidades
        y consecuencias descritas por el manual.

        Evita interpretaciones legales que no estén en el contexto.
        """,

        "lesson_focus": [
            "Responsabilidad de quien conduce",
            "Infracciones",
            "Licencia de conducir",
            "Obligaciones",
            "Consecuencias",
            "Seguridad vial",
        ],

        "quiz_focus": """
        Evalúa reconocimiento de responsabilidades y consecuencias
        de determinadas conductas.
        """,
    },


    "C9.4": {
        "learning_goal": """
        El estudiante debe saber cómo reaccionar correctamente
        durante una frenada fuerte o de emergencia.
        """,

        "teaching_strategy": """
        Diferencia claramente el comportamiento de vehículos
        con ABS y sin ABS.

        Explica cómo mantener el máximo control posible.
        """,

        "lesson_focus": [
            "Frenada de emergencia",
            "ABS",
            "Bloqueo de ruedas",
            "Dirección",
            "Presión sobre el freno",
            "Control del vehículo",
        ],

        "quiz_focus": """
        Evalúa cómo debe reaccionar la persona conductora
        durante una frenada fuerte con y sin ABS.
        """,
    },


    "C9.5": {
        "learning_goal": """
        El estudiante debe comprender cómo el tránsito y sus
        hábitos de conducción afectan al medio ambiente.
        """,

        "teaching_strategy": """
        Relaciona conducción, consumo y contaminación utilizando
        únicamente los efectos y recomendaciones descritos
        en el manual.
        """,

        "lesson_focus": [
            "Tránsito",
            "Contaminación",
            "Consumo de combustible",
            "Emisiones",
            "Conducción eficiente",
            "Impacto ambiental",
        ],

        "quiz_focus": """
        Evalúa hábitos de conducción que pueden reducir
        el impacto ambiental.
        """,
    },


    "C9.6": {
        "learning_goal": """
        El estudiante debe conocer las características básicas
        de conducción y seguridad de vehículos eléctricos.
        """,

        "teaching_strategy": """
        Explica únicamente los aspectos presentes en el manual.

        Relaciona las características del vehículo eléctrico
        con decisiones prácticas de conducción y seguridad.
        """,

        "lesson_focus": [
            "Vehículo eléctrico",
            "Autonomía",
            "Batería",
            "Carga",
            "Seguridad",
            "Conducción",
        ],

        "quiz_focus": """
        Evalúa conocimientos básicos sobre operación y seguridad
        de vehículos eléctricos.
        """,
    },


    # ========================================================
    # ANEXOS
    # ========================================================

    "A1": {
        "learning_goal": """
        El estudiante debe reconocer e interpretar las principales
        señales de tránsito verticales presentadas en el manual.
        """,

        "teaching_strategy": """
        Organiza las señales por categorías y significado.

        Prioriza comprender qué acción o peligro comunica
        cada señal.
        """,

        "lesson_focus": [
            "Señales reglamentarias",
            "Señales de advertencia",
            "Señales informativas",
            "Restricciones",
            "Peligros",
            "Interpretación visual",
        ],

        "quiz_focus": """
        Evalúa interpretación y clasificación de señales verticales.
        """,
    },


    "A2.1": {
        "learning_goal": """
        El estudiante debe comprender el significado de conceptos
        fundamentales utilizados en el manual y en las normas
        de tránsito.
        """,

        "teaching_strategy": """
        Explica los términos mediante definiciones claras
        y relaciones con situaciones de conducción.

        No agregues definiciones externas al glosario.
        """,

        "lesson_focus": [
            "Conceptos de tránsito",
            "Definiciones",
            "Vía",
            "Calzada",
            "Berma",
            "Intersección",
            "Terminología vial",
        ],

        "quiz_focus": """
        Evalúa comprensión del significado de términos del glosario.
        """,
    },


    "A2.2": {
        "learning_goal": """
        El estudiante debe conocer las principales fuentes
        institucionales y normativas utilizadas para elaborar
        el manual.
        """,

        "teaching_strategy": """
        Presenta esta sección de manera breve.

        Explica la función general de las referencias sin convertir
        la lección en memorización bibliográfica.
        """,

        "lesson_focus": [
            "Fuentes del manual",
            "CONASET",
            "Ley de Tránsito",
            "Manuales técnicos",
            "Documentación de referencia",
        ],

        "quiz_focus": """
        Evalúa únicamente comprensión general del origen
        y propósito de las referencias.

        Evita preguntas de memorización bibliográfica.
        """,
    },


    "A3": {
        "learning_goal": """
        El estudiante debe comprender el proceso general para
        obtener una Licencia de Conducir y las etapas que debe
        completar.
        """,

        "teaching_strategy": """
        Presenta el proceso en orden cronológico.

        Diferencia requisitos previos, tramitación municipal,
        evaluaciones y entrega del documento.
        """,

        "lesson_focus": [
            "Requisitos",
            "Municipalidad",
            "Residencia",
            "Exámenes",
            "Evaluación médica",
            "Examen teórico",
            "Examen práctico",
            "Obtención de licencia",
        ],

        "quiz_focus": """
        Evalúa comprensión del orden general y las etapas
        necesarias para obtener la licencia.
        """,
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

15. Si recibes un perfil del estudiante, úsalo únicamente para adaptar énfasis,
profundidad, ejemplos y dificultad. El contexto oficial del manual sigue siendo
la única fuente de verdad; el perfil no puede agregar hechos, leyes, cifras,
normas ni recomendaciones externas.

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

12. Todo el texto visible del quiz debe estar escrito en español neutro
  latinoamericano, incluyendo cada pregunta, todas las alternativas y
  cada explicación. No uses inglés, salvo nombres propios o siglas técnicas.

13. La respuesta debe incluir exactamente la clave raíz "language" con valor
  "es".

14. Devuelve SOLAMENTE JSON válido.

15. Si recibes un perfil del estudiante, úsalo únicamente para adaptar énfasis,
profundidad, ejemplos y dificultad. El contexto oficial del manual sigue siendo
la única fuente de verdad; el perfil no puede agregar hechos, leyes, cifras,
normas ni recomendaciones externas.

16. Las alternativas no deben incluir prefijos como "a)", "b)", "c)" o "d)" (Lo mismo con números), 
esto ya viene directamente en el frontend por lo que no es necesario.

Debes utilizar exactamente esta estructura:

{
  "language": "es",
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