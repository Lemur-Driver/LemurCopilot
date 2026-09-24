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
]