// Minimal i18n helper for the frontend
import en from './locales/en.json';
import es from './locales/es.json';

const LOCALES = { en, es };

function detectLocale() {
    try {
        const stored = localStorage.getItem('locale');
        if (stored && LOCALES[stored]) return stored;
    } catch (err) { console.debug('i18n: detectLocale localStorage error', err); }
    const nav = navigator.language || navigator.userLanguage || 'en';
    return nav.startsWith('es') ? 'es' : 'en';
}

let current = detectLocale();

export function setLocale(l) {
    if (LOCALES[l]) {
        current = l;
        try { localStorage.setItem('locale', l); } catch (err) { console.debug('i18n: setLocale localStorage error', err); }
    }
}

export function getLocale() {
    return current;
}

export function t(key, vars) {
    const bundle = LOCALES[current] || LOCALES.en;
    let v = bundle[key]; // Buscar clave completa primero
    if (v === undefined) {
        // Si no, buscar anidada
        const parts = key.split('.');
        v = bundle;
        for (const p of parts) {
            v = v && v[p];
            if (v === undefined) break;
        }
    }
    if (v === undefined) return key;
    if (vars) {
        return v.replace(/\{(\w+)\}/g, (_, name) => (vars[name] !== undefined ? String(vars[name]) : `{${name}}`));
    }
    return v;
}

export default { t, setLocale, getLocale };
