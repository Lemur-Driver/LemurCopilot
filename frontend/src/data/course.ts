//POR AHORA, LUEGO ESTO DEBE VENIR DE BACKEND

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
  {
    id: 'unit-1',
    code: 'Unidad 1',
    title: 'Los siniestros de tránsito',
    lessons: [
      {
        id: 'C1.1',
        code: 'C1.1',
        title: 'Estadísticas de siniestros en Chile',
        description:
          'Conoce las principales estadísticas y factores relacionados con los siniestros de tránsito en Chile.',
      },
      {
        id: 'C1.2',
        code: 'C1.2',
        title: 'Sistema Seguro',
        description:
          'Comprende el enfoque de Sistema Seguro y cómo busca reducir las consecuencias de los errores humanos.',
      },
    ],
  },
  {
  id: 'unit-2',
  code: 'Unidad 2',
  title: 'El automóvil y las leyes físicas',

  lessons: [
    {
      id: 'C2.1',
      code: 'C2.1',
      title: 'Funcionamiento del automóvil',
      description:
        'Conoce los principales sistemas del vehículo y cómo su funcionamiento influye en una conducción segura.',
    },

    {
      id: 'C2.2',
      code: 'C2.2',
      title: 'La energía y las leyes físicas',
      description:
        'Comprende cómo la velocidad, la energía, las curvas y las distancias de detención afectan la conducción.',
    },

    {
      id: 'C2.3',
      code: 'C2.3',
      title: 'Elementos de seguridad',
      description:
        'Aprende a distinguir los elementos de seguridad activa y pasiva y su función en el vehículo.',
    },
  ],
},

]