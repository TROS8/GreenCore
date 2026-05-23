/**
 * GreenCore — Sistema de gestion de invernadero
 * Configuracion de i18next para internacionalizacion ES/EN del frontend.
 *
 * @module i18n/index
 * @version 1.0.0
 */
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import es from './locales/es.json'
import en from './locales/en.json'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      es: { translation: es },
      en: { translation: en },
    },
    lng: 'es',
    fallbackLng: 'es',
    interpolation: { escapeValue: false },
  })

export default i18n
