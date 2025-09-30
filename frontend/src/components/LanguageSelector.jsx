import React, { useState, useRef, useEffect } from 'react';
import { t, setLocale } from '../i18n';

const LANGS = [
    { code: 'en', flag: '🇬🇧', titleKey: 'nav.language_en' },
    { code: 'es', flag: '🇪🇸', titleKey: 'nav.language_es' }
];

function LanguageSelector({ value, onChange }) {
    const [open, setOpen] = useState(false);
    const [idx, setIdx] = useState(() => LANGS.findIndex(l => l.code === value) || 0);
    const ref = useRef(null);

    useEffect(() => {
        setIdx(LANGS.findIndex(l => l.code === value));
    }, [value]);

    useEffect(() => {
        if (!open) return;
        function onDoc(e) {
            if (!ref.current || ref.current.contains(e.target)) return;
            setOpen(false);
        }
        window.addEventListener('mousedown', onDoc);
        return () => window.removeEventListener('mousedown', onDoc);
    }, [open]);

    const select = React.useCallback((code) => {
        try {
            setLocale(code);
        } catch (err) {
            console.debug('setLocale failed', err);
        }
        if (onChange) onChange(code);
        setOpen(false);
        // Reload the page to apply language changes
        window.location.reload();
    }, [onChange]);

    // keyboard navigation for vertical list: ArrowUp/ArrowDown, Enter, Escape
    useEffect(() => {
        if (!open) return;
        function onKey(e) {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                setIdx(i => (i - 1 + LANGS.length) % LANGS.length);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                setIdx(i => (i + 1) % LANGS.length);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                const code = (LANGS[idx] && LANGS[idx].code) || LANGS[0].code;
                select(code);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                setOpen(false);
            }
        }
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [open, idx, select]);

    const current = LANGS[idx] || LANGS[0];

    return (
        <div className="nav__lang-wrapper" ref={ref}>
            <button
                type="button"
                className={`nav__lang-button ${value === current.code ? 'nav__lang-button--active' : ''}`}
                onClick={() => setOpen(o => !o)}
                aria-haspopup="true"
                aria-expanded={open}
                title={t(current.titleKey) || current.code}
            >
                {LANGS.find(l => l.code === value)?.flag || current.flag}
            </button>
            {open && (
                <div className="nav__lang-popover nav__lang-popover--vertical" role="dialog" aria-label={t('nav.language_label') || 'Language selector'}>
                    <ul className="nav__lang-list" role="listbox" aria-activedescendant={`lang-${LANGS[idx].code}`} tabIndex={-1}>
                        {LANGS.map((l, i) => (
                            <li key={l.code} id={`lang-${l.code}`} role="option" aria-selected={i === idx} className={`nav__lang-item ${i === idx ? 'nav__lang-item--active' : ''}`}>
                                <button
                                    type="button"
                                    className="nav__lang-popover-flag"
                                    onClick={() => select(l.code)}
                                    title={t(l.titleKey) || l.code}
                                    aria-label={t(l.titleKey) || l.code}
                                >
                                    <span className="nav__lang-flag">{l.flag}</span>
                                    <span className="nav__lang-name">{t(l.titleKey) || l.code}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default LanguageSelector;
