import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(HttpBackend) 
  .use(LanguageDetector) 
  .use(initReactI18next) 
  .init({
    fallbackLng: 'en', 
    debug: false, 
    interpolation: {
      escapeValue: false,
    },
    backend: {
      loadPath: '/locales/{{lng}}/translation.json', 
    },
    detection: {
      order: ['queryString', 'cookie', 'localStorage', 'navigator'], 
      caches: ['localStorage'],
    },
  });

export default i18n;