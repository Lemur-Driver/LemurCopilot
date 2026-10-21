import { Link, useLocation } from 'react-router-dom'
import lemurImage from '../assets/icon.png'

type InfoPageKey = 'about' | 'contact' | 'privacy' | 'terms'

const pages: Record<InfoPageKey, { eyebrow: string; title: string; intro: string; sections: { title: string; body: string }[] }> = {
  about: {
    eyebrow: 'Nuestro propósito',
    title: 'Aprender a conducir también puede sentirse como avanzar.',
    intro: 'Lemur acompaña a quienes se preparan para la licencia Clase B en Chile con explicaciones claras, práctica guiada y un camino que se adapta a su progreso.',
    sections: [
      { title: 'Aprende a tu ritmo', body: 'Dividimos el camino en lecciones pequeñas para que puedas estudiar cuando te acomode y retomar sin perder tu avance.' },
      { title: 'Entiende, no solo memorices', body: 'La práctica y las explicaciones están pensadas para ayudarte a comprender conceptos de seguridad vial y reconocer qué conviene reforzar.' },
      { title: 'Una ayuda para prepararte', body: 'Lemur es una herramienta de estudio complementaria. Para prepararte, consulta también el Libro para la Conducción en Chile y las fuentes oficiales vigentes.' },
    ],
  },
  contact: {
    eyebrow: 'Estamos para ayudarte',
    title: '¿Tienes una pregunta o una idea?',
    intro: 'Nos importa que tu experiencia de aprendizaje sea clara y útil. Si necesitas ayuda con tu cuenta, encontraste un problema o quieres compartir sugerencias, escríbenos.',
    sections: [
      { title: 'Soporte y consultas', body: 'Si encontraste un problema, cuéntanos qué pasó y qué pasos lo provocaron. No envíes contraseñas ni información sensible.' },
      { title: 'Consultas de organizaciones', body: '¿Representas a una escuela, institución o empresa interesada en educación vial? Nos encantará conocer tu propuesta.' },
      { title: 'Al escribirnos', body: 'Por ahora, usa los canales oficiales donde conociste Lemur. No se ha publicado un correo de contacto en este sitio.' },
    ],
  },
  privacy: {
    eyebrow: 'Tu información',
    title: 'Privacidad, explicada con claridad.',
    intro: 'Lemur usa la información necesaria para iniciar tu sesión y guardar tu aprendizaje. Esta página es una explicación general y debe revisarse con los datos legales y operativos definitivos del servicio antes de su publicación.',
    sections: [
      { title: 'Qué información se usa', body: 'Al iniciar sesión con Google, recibimos datos básicos de perfil como nombre, correo e imagen. También guardamos resultados de quizzes, dominio de temas y fechas de actividad para mostrar tu progreso.' },
      { title: 'Para qué se utiliza', body: 'Esta información permite autenticar tu cuenta, mantener el historial de aprendizaje, calcular indicadores de progreso y mejorar la experiencia educativa.' },
      { title: 'Tus opciones y consultas', body: 'Para consultas sobre tus datos, su conservación o eliminación, contacta al equipo de Lemur por el canal oficial de soporte. Agrega aquí el procedimiento definitivo para solicitudes de privacidad antes de publicar.' },
      { title: 'Servicios de terceros', body: 'El acceso utiliza Google Identity Services. Revisa también la política de privacidad de Google para entender cómo Google gestiona sus propios servicios.' },
    ],
  },
  terms: {
    eyebrow: 'Uso responsable',
    title: 'Condiciones para aprender con Lemur.',
    intro: 'Al usar Lemur, aceptas utilizar el servicio de forma responsable y como apoyo a tu estudio. El equipo del producto debe confirmar y completar estas condiciones legales antes de publicar.',
    sections: [
      { title: 'Herramienta educativa', body: 'Lemur ofrece material de aprendizaje y práctica para ayudar a preparar la licencia Clase B. No sustituye el Libro para la Conducción en Chile, la instrucción profesional ni la información oficial vigente.' },
      { title: 'Cuenta y progreso', body: 'Eres responsable de utilizar tu cuenta de manera adecuada. Lemur guarda información de progreso para ofrecer continuidad entre sesiones.' },
      { title: 'Contenido y disponibilidad', body: 'El contenido puede actualizarse para corregirlo y mejorarlo. Aunque buscamos ofrecer explicaciones útiles, consulta siempre fuentes oficiales para confirmar reglas y requisitos vigentes.' },
      { title: 'Contacto y versión definitiva', body: 'Para consultas sobre estas condiciones, contacta al equipo por su canal oficial. Añade la entidad responsable, jurisdicción, fecha de vigencia y condiciones completas antes de lanzar el servicio.' },
    ],
  },
}

function InfoPage() {
  const { pathname } = useLocation()
  const key = pathname.split('/').filter(Boolean)[0] as InfoPageKey
  const page = pages[key] ?? pages.about

  return (
    <main className={`info-page info-page-${key}`}>
      <Link className="info-back" to="/">← Volver a Lemur</Link>
      <section className="info-hero">
        <div><span className="section-kicker">{page.eyebrow}</span><h1>{page.title}</h1><p>{page.intro}</p></div>
        <img src={lemurImage} alt="Lemur, tu compañero de aprendizaje" />
      </section>
      <div className="info-sections">{page.sections.map((section, index) => <article className="info-section" key={section.title}><span className="info-section-number">{String(index + 1).padStart(2, '0')}</span><div><h2>{section.title}</h2><p>{section.body}</p></div></article>)}</div>
      {key === 'contact' && <div className="contact-note"><span aria-hidden="true">✉</span><p>El equipo de Lemur debe definir y publicar un canal de contacto oficial antes del lanzamiento.</p></div>}
    </main>
  )
}

export default InfoPage
