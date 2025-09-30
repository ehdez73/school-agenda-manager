import React, { useEffect } from 'react';
import { t } from '../i18n';

export default function DayIndices({ daysPerWeek = 5, dayIndices = [], setDayIndices = () => { }, suppressResize = false }) {
    useEffect(() => {
        const n = Number(daysPerWeek) || 0;
        if (!n) return;
        if (suppressResize) return;
        setDayIndices(prev => {
            const copy = Array.isArray(prev) ? [...prev] : [];
            if (copy.length === n) return copy;
            if (copy.length < n) {
                for (let i = copy.length; i < n; i++) copy.push(i);
            } else if (copy.length > n) {
                copy.length = n;
            }
            return copy;
        });
    }, [daysPerWeek, suppressResize, setDayIndices]);

    const handleDayIndexChange = (index, value) => {
        const numValue = Number(value);
        setDayIndices(prev => {
            const copy = Array.isArray(prev) ? [...prev] : [];
            copy[index] = numValue;
            return copy;
        });
    };

    const n = Math.max(0, Number(daysPerWeek) || 0);
    const displayIndices = Array.from({ length: n }, (_, i) => dayIndices[i] ?? i);

    const dayOptions = Array.from({ length: 7 }, (_, i) => ({ value: i, label: t(`day.${i}`) }));

    return (
        <div style={{ marginTop: '1rem' }}>
            <h4 style={{ margin: '0 0 0.5rem 0' }}>{t('days.names_title')}</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.5rem' }}>
                {displayIndices.map((idx, i) => (
                    <label key={i} className="config-form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {`Day ${i + 1}:`}
                        <select
                            value={idx}
                            onChange={e => handleDayIndexChange(i, e.target.value)}
                            className="config-form-input"
                        >
                            {dayOptions.map(option => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </label>
                ))}
            </div>
        </div>
    );
}