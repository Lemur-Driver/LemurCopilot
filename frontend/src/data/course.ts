// POR AHORA, LUEGO ESTO DEBE VENIR DEL BACKEND

export interface Lesson {
  id: string
  code: string
  title: string
  description: string
}

export interface Unit {
  id: string
  code: string
  title: string
  lessons: Lesson[]
}


export const course: Unit[] = [

  // =========================================================
  // UNIDAD 1
  // =========================================================

  {
    id: 'unit-1',
    code: 'Unidad 1',
    title: 'Los siniestros de tránsito',

    lessons: [
      {
        id: 'C1',
        code: 'C1',
        title: 'Los siniestros de tránsito',
        description:
          'Comprende por qué los siniestros de tránsito son prevenibles y cómo las decisiones de las personas influyen en su ocurrencia.',
      },

      {
        id: 'C1.1',
        code: 'C1.1',
        title: 'Estadísticas de siniestros en Chile',
        description:
          'Conoce las principales estadísticas, factores de riesgo y características de los siniestros de tránsito en Chile.',
      },

      {
        id: 'C1.2',
        code: 'C1.2',
        title: 'Sistema Seguro',
        description:
          'Comprende el enfoque de Sistema Seguro, la responsabilidad compartida y la importancia de reducir las consecuencias de los errores humanos.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 2
  // =========================================================

  {
    id: 'unit-2',
    code: 'Unidad 2',
    title: 'Los principios de la conducción',

    lessons: [
      {
        id: 'C2.1',
        code: 'C2.1',
        title: 'Funcionamiento del automóvil',
        description:
          'Conoce los principales sistemas del vehículo, su funcionamiento y las revisiones necesarias para conducir de forma segura.',
      },

      {
        id: 'C2.2',
        code: 'C2.2',
        title: 'La energía y las leyes físicas',
        description:
          'Comprende cómo la velocidad, la energía, la inercia, las curvas y las distancias de reacción y frenado afectan la conducción.',
      },

      {
        id: 'C2.3',
        code: 'C2.3',
        title: 'Elementos de seguridad',
        description:
          'Aprende a distinguir los elementos de seguridad activa y pasiva y cómo reducen el riesgo y las consecuencias de un siniestro.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 3
  // =========================================================

  {
    id: 'unit-3',
    code: 'Unidad 3',
    title: 'Convivencia Vial',

    lessons: [
      {
        id: 'C3',
        code: 'C3',
        title: 'Convivencia Vial',
        description:
          'Comprende cómo el respeto, la responsabilidad, la educación vial y la consideración hacia otras personas contribuyen a una convivencia segura.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 4
  // =========================================================

  {
    id: 'unit-4',
    code: 'Unidad 4',
    title: 'La persona en el tránsito',

    lessons: [
      {
        id: 'C4',
        code: 'C4',
        title: 'La persona en el tránsito',
        description:
          'Comprende cómo la percepción, la atención, la experiencia y las capacidades humanas influyen en la conducción.',
      },

      {
        id: 'C4.1',
        code: 'C4.1',
        title: 'La conducción segura requiere equilibrio emocional',
        description:
          'Analiza cómo las emociones, la agresividad, el estrés y la empatía pueden afectar el comportamiento al conducir.',
      },

      {
        id: 'C4.2',
        code: 'C4.2',
        title: 'Conductas que implican riesgos',
        description:
          'Identifica comportamientos y decisiones que pueden aumentar el riesgo durante la conducción.',
      },

      {
        id: 'C4.3',
        code: 'C4.3',
        title: 'Sobre el alcohol en la conducción',
        description:
          'Comprende cómo el alcohol afecta las capacidades necesarias para conducir y por qué aumenta el riesgo de siniestros.',
      },

      {
        id: 'C4.4',
        code: 'C4.4',
        title: 'Las drogas y estupefacientes',
        description:
          'Conoce cómo distintas drogas pueden alterar la percepción, el tiempo de reacción y la capacidad para conducir de forma segura.',
      },

      {
        id: 'C4.5',
        code: 'C4.5',
        title: 'Enfermedades que pueden afectar a la conducción',
        description:
          'Comprende cómo determinadas enfermedades pueden influir en la conducción y qué precauciones debe tomar una persona conductora.',
      },

      {
        id: 'C4.6',
        code: 'C4.6',
        title: 'Medicamentos que pueden afectar a la conducción',
        description:
          'Identifica medicamentos que pueden disminuir la atención, provocar somnolencia o afectar otras capacidades necesarias para conducir.',
      },

      {
        id: 'C4.7',
        code: 'C4.7',
        title: 'Cansancio, sueño y fatiga',
        description:
          'Reconoce los efectos del cansancio y el sueño al volante y aprende cuándo detenerse y descansar.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 5
  // =========================================================

  {
    id: 'unit-5',
    code: 'Unidad 5',
    title: 'Las y los usuarios vulnerables',

    lessons: [
      {
        id: 'C5',
        code: 'C5',
        title: 'Las y los usuarios vulnerables',
        description:
          'Aprende a identificar y proteger a peatones, personas mayores, ciclistas, motociclistas y otros usuarios especialmente vulnerables.',
      },

      {
        id: 'C5.1',
        code: 'C5.1',
        title: 'Niñas y niños en el automóvil',
        description:
          'Conoce las medidas de seguridad y los sistemas de retención necesarios para transportar niñas y niños de forma segura.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 6
  // =========================================================

  {
    id: 'unit-6',
    code: 'Unidad 6',
    title: 'Normas de circulación',

    lessons: [
      {
        id: 'C6',
        code: 'C6',
        title: 'Normas de circulación',
        description:
          'Introduce las principales normas que permiten organizar el tránsito y circular de forma segura y predecible.',
      },

      {
        id: 'C6.1',
        code: 'C6.1',
        title: 'Señales de tránsito',
        description:
          'Aprende el significado y la función de semáforos, señales verticales, demarcaciones y otras formas de regulación del tránsito.',
      },

      {
        id: 'C6.2',
        code: 'C6.2',
        title: 'Las reglas del tránsito',
        description:
          'Comprende las reglas de circulación, preferencias de paso, virajes, cambios de pista y otras maniobras habituales.',
      },

      {
        id: 'C6.3',
        code: 'C6.3',
        title: 'La velocidad',
        description:
          'Conoce los límites de velocidad y aprende a adaptar la velocidad a las condiciones de la vía, el clima y el tránsito.',
      },

      {
        id: 'C6.4',
        code: 'C6.4',
        title: 'Encuentros y adelantamientos',
        description:
          'Aprende cómo enfrentar cruces con otros vehículos y realizar adelantamientos y sobrepasos de forma segura.',
      },

      {
        id: 'C6.5',
        code: 'C6.5',
        title: 'Estacionamiento y detención',
        description:
          'Conoce dónde y cómo estacionar o detener un vehículo sin generar riesgos ni interferir con la circulación.',
      },

      {
        id: 'C6.6',
        code: 'C6.6',
        title: 'Cruces ferroviarios',
        description:
          'Aprende las precauciones y obligaciones necesarias para atravesar cruces ferroviarios de forma segura.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 7
  // =========================================================

  {
    id: 'unit-7',
    code: 'Unidad 7',
    title: 'Conducción en circunstancias especiales',

    lessons: [
      {
        id: 'C7.1',
        code: 'C7.1',
        title: 'Conducción en la oscuridad',
        description:
          'Aprende a adaptar la velocidad, la distancia y el uso de las luces cuando conduces de noche o con poca visibilidad.',
      },

      {
        id: 'C7.2',
        code: 'C7.2',
        title: 'Conducción con carga',
        description:
          'Comprende cómo la carga y los remolques modifican la estabilidad, el frenado y la maniobrabilidad del vehículo.',
      },

      {
        id: 'C7.3',
        code: 'C7.3',
        title: 'Conducción en autopistas',
        description:
          'Aprende cómo incorporarte, circular y salir de autopistas de manera segura y cómo actuar ante situaciones especiales.',
      },

      {
        id: 'C7.4',
        code: 'C7.4',
        title: 'Conducción en distintas condiciones climáticas',
        description:
          'Conoce las precauciones necesarias para conducir con lluvia, niebla, viento y otras condiciones que reducen la adherencia o visibilidad.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 8
  // =========================================================

  {
    id: 'unit-8',
    code: 'Unidad 8',
    title: 'Conducción eficiente',

    lessons: [
      {
        id: 'C8.1',
        code: 'C8.1',
        title: 'Recomendaciones antes de partir tu viaje',
        description:
          'Aprende cómo preparar el vehículo y planificar el viaje para conducir de manera segura y eficiente.',
      },

      {
        id: 'C8.2',
        code: 'C8.2',
        title: 'Recomendaciones durante tu trayecto',
        description:
          'Aplica técnicas de conducción que permitan reducir el consumo, anticiparse al tránsito y mantener una conducción fluida.',
      },

      {
        id: 'C8.3',
        code: 'C8.3',
        title: 'Seguridad',
        description:
          'Relaciona los principios de conducción segura con una conducción eficiente y responsable.',
      },
    ],
  },


  // =========================================================
  // UNIDAD 9
  // =========================================================

  {
    id: 'unit-9',
    code: 'Unidad 9',
    title: 'Informaciones importantes',

    lessons: [
      {
        id: 'C9.1',
        code: 'C9.1',
        title: 'Cómo comportarse en caso de siniestro',
        description:
          'Aprende cómo actuar, prestar ayuda y cumplir las obligaciones correspondientes ante un siniestro de tránsito.',
      },

      {
        id: 'C9.2',
        code: 'C9.2',
        title: 'Disposiciones aplicables a los vehículos',
        description:
          'Conoce los documentos, seguros, revisiones y requisitos necesarios para que un vehículo pueda circular legalmente.',
      },

      {
        id: 'C9.3',
        code: 'C9.3',
        title: 'Responsabilidad de la persona conductora',
        description:
          'Comprende las responsabilidades de quien conduce y las consecuencias de incumplir las normas de tránsito.',
      },

      {
        id: 'C9.4',
        code: 'C9.4',
        title: 'Recomendaciones para frenadas fuertes',
        description:
          'Aprende cómo actuar correctamente durante una frenada de emergencia con vehículos con y sin sistema ABS.',
      },

      {
        id: 'C9.5',
        code: 'C9.5',
        title: 'Tránsito y medio ambiente',
        description:
          'Comprende cómo la conducción influye en las emisiones y cómo adoptar hábitos que reduzcan el impacto ambiental.',
      },

      {
        id: 'C9.6',
        code: 'C9.6',
        title: 'Conducción de un vehículo eléctrico',
        description:
          'Conoce las principales consideraciones de seguridad, autonomía y carga asociadas a vehículos eléctricos e híbridos.',
      },
    ],
  },


  // =========================================================
  // ANEXOS
  // =========================================================

  {
    id: 'unit-annexes',
    code: 'Anexos',
    title: 'Material complementario',

    lessons: [
      {
        id: 'A1',
        code: 'A1',
        title: 'Señales de tránsito verticales',
        description:
          'Consulta las principales señales reglamentarias, preventivas e informativas utilizadas en las vías.',
      },

      {
        id: 'A2.1',
        code: 'A2.1',
        title: 'Glosario',
        description:
          'Consulta definiciones de conceptos y términos utilizados a lo largo del manual de conducción.',
      },

      {
        id: 'A2.2',
        code: 'A2.2',
        title: 'Referencias',
        description:
          'Revisa las fuentes y documentos utilizados como referencia para la elaboración del manual.',
      },

      {
        id: 'A3',
        code: 'A3',
        title: 'Proceso de obtención de Licencia de Conducir',
        description:
          'Conoce las etapas generales, evaluaciones y trámites necesarios para obtener una Licencia de Conducir.',
      },
    ],
  },
]