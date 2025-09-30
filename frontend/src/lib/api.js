// Small centralized API helper using Vite env var VITE_API_BASE (defaults to /api)
const API_BASE = import.meta.env.VITE_API_BASE || '/api';

function buildUrl(path, { cacheBust } = {}) {
    const p = path.startsWith('/') ? path : `/${path}`;
    let url = `${API_BASE}${p}`;
    if (cacheBust) {
        const sep = url.includes('?') ? '&' : '?';
        url = `${url}${sep}_ts=${Date.now()}`;
    }
    return url;
}

async function request(method, path, body = undefined, opts = {}) {
    const { responseType = 'json', cacheBust = false, headers = {} } = opts;
    const url = buildUrl(path, { cacheBust });
    // attach locale header so backend can localize per-request
    let locale = 'en';
    try { locale = localStorage.getItem('locale') || (navigator.language && navigator.language.startsWith('es') ? 'es' : 'en'); } catch { /* ignore */ }
    const init = { method, headers: { 'X-Locale': locale, ...headers } };
    if (body !== undefined) {
        init.body = JSON.stringify(body);
        init.headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(url, init);

    const contentType = res.headers.get('content-type') || '';

    // Try to parse error body for better messages
    if (!res.ok) {
        let errText = `HTTP ${res.status}`;
        try {
            if (contentType.includes('application/json')) {
                const json = await res.json();
                errText = json.error || json.message || JSON.stringify(json);
            } else {
                const text = await res.text();
                if (text) errText = text;
            }
        } catch {
            /* ignore parsing errors */
        }
        const err = new Error(errText);
        err.status = res.status;
        throw err;
    }

    if (responseType === 'text' || contentType.indexOf('text/') === 0) {
        return res.text();
    }
    if (responseType === 'json') {
        // Some endpoints may return empty body
        const text = await res.text();
        try {
            return text ? JSON.parse(text) : null;
        } catch {
            return text;
        }
    }
    // fallback
    return res;
}

export const api = {
    get: (path, opts) => request('GET', path, undefined, opts),
    post: (path, body, opts) => request('POST', path, body, opts),
    put: (path, body, opts) => request('PUT', path, body, opts),
    del: (path, opts) => request('DELETE', path, undefined, opts),
    API_BASE,
};

export default api;
