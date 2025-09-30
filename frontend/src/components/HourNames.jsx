import React, { useEffect } from 'react';
import { t } from '../i18n';

export default function HourNames({ classesPerDay = 5, hourNames = [], setHourNames = () => { }, suppressResize = false }) {
    useEffect(() => {
        const n = Number(classesPerDay) || 0;
        if (!n) return;
        if (suppressResize) return;
        setHourNames(prev => {
            const copy = Array.isArray(prev) ? [...prev] : [];
            if (copy.length === n) return copy;
            if (copy.length < n) {
                for (let i = copy.length; i < n; i++) copy.push(`Hora ${i + 1}`);
            } else if (copy.length > n) {
                copy.length = n;
            }
            return copy;
        });
    }, [classesPerDay, suppressResize, setHourNames]);

    const handleHourNameChange = (index, value) => {
        setHourNames(prev => {
            const copy = Array.isArray(prev) ? [...prev] : [];
            copy[index] = value;
            return copy;
        });
    };

    const n = Math.max(0, Number(classesPerDay) || 0);
    const displayNames = Array.from({ length: n }, (_, i) => hourNames[i] ?? t('hours.label').replace('{n}', String(i + 1)));

    return (
        <div style={{ marginTop: '1rem' }}>
            <h4 style={{ margin: '0 0 0.5rem 0' }}>{t('hours.names_title')}</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.5rem' }}>
                {displayNames.map((name, idx) => (
                    <label key={idx} className="config-form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {t('hours.label').replace('{n}', String(idx + 1))}:
                        <input
                            type="text"
                            value={name}
                            onChange={e => handleHourNameChange(idx, e.target.value)}
                            className="config-form-input"
                        />
                    </label>
                ))}
            </div>
        </div>
    );
}
