import React, { useState, useEffect } from 'react';
import api from '../lib/api';
import { t } from '../i18n';

export default function PreferencesGrid({ value = {}, onChange = () => { }, days, classesPerDay = 5 }) {

    const [dayNames, setDayNames] = useState([]);

    const daysList = React.useMemo(() => days ?? dayNames, [days, dayNames]);

    const normalizeIncoming = React.useCallback((val) => {
        if (!val) return {};
        const out = {};

        Object.keys(val).forEach(k => {
            const maybeNum = Number(k);
            const idx = Number.isFinite(maybeNum) && !Number.isNaN(maybeNum) ? maybeNum : null;

            let dayIndex = idx;
            if (dayIndex === null) {
                const nameIndex = daysList.findIndex(d => d === k);
                dayIndex = nameIndex >= 0 ? nameIndex : k; // if not found, preserve key (fallback)
            }
            out[dayIndex] = val[k];
        });
        return out;
    }, [daysList]);

    const [localValue, setLocalValue] = useState(() => normalizeIncoming(value));
    const [hourNames, setHourNames] = useState(() => Array.from({ length: classesPerDay }, (_, i) => `Hora ${i}`));

    useEffect(() => {
        api.get('/config').then(cfg => {
            if (cfg) {
                setDayNames(cfg.day_names || []);
                if (Array.isArray(cfg.hour_names) && cfg.hour_names.length) {
                    setHourNames(cfg.hour_names.slice(0, classesPerDay));
                } else {
                    setHourNames(Array.from({ length: classesPerDay }, (_, i) => `Hora ${i}`));
                }
            } else {
                setDayNames([]);
                setHourNames(Array.from({ length: classesPerDay }, (_, i) => `Hora ${i}`));
            }
        }).catch(() => {
            setDayNames([]);
            setHourNames(Array.from({ length: classesPerDay }, (_, i) => `Hora ${i}`));
        });
    }, [classesPerDay]);

    useEffect(() => {
        setLocalValue(normalizeIncoming(value));
    }, [value, normalizeIncoming]);

    const getStatus = (dayIndex, hour) => {
        const dayVal = localValue && localValue[dayIndex];
        if (!dayVal) return '';
        if (Array.isArray(dayVal)) {
            return dayVal.includes(hour) ? 'unavailable' : '';
        }
        if (dayVal && typeof dayVal === 'object') {
            if (Array.isArray(dayVal.unavailable) && dayVal.unavailable.includes(hour)) return 'unavailable';
            if (Array.isArray(dayVal.preferred) && dayVal.preferred.includes(hour)) return 'preferred';
        }
        return '';
    };

    const emitNormalized = (obj) => {
        const out = {};
        Object.keys(obj).forEach(k => {
            out[k] = obj[k];
        });
        onChange(out);
    };

    const toggle = (dayIndex, hour) => {
        const next = { ...(localValue || {}) };
        let dayObj = { unavailable: [], preferred: [] };
        const existing = next[dayIndex];
        if (Array.isArray(existing)) {
            dayObj.unavailable = [...existing];
        } else if (existing && typeof existing === 'object') {
            dayObj.unavailable = Array.isArray(existing.unavailable) ? [...existing.unavailable] : [];
            dayObj.preferred = Array.isArray(existing.preferred) ? [...existing.preferred] : [];
        }

        const statusLocal = (Array.isArray(dayObj.unavailable) && dayObj.unavailable.includes(hour)) ? 'unavailable' : (Array.isArray(dayObj.preferred) && dayObj.preferred.includes(hour) ? 'preferred' : '');
        if (statusLocal === '') {
            // add to unavailable
            dayObj.unavailable = Array.from(new Set([...dayObj.unavailable, hour])).sort((a, b) => a - b);
            // ensure removed from preferred
            dayObj.preferred = dayObj.preferred.filter(h => h !== hour);
        } else if (statusLocal === 'unavailable') {
            // move to preferred
            dayObj.unavailable = dayObj.unavailable.filter(h => h !== hour);
            dayObj.preferred = Array.from(new Set([...dayObj.preferred, hour])).sort((a, b) => a - b);
        } else {
            // clear
            dayObj.unavailable = dayObj.unavailable.filter(h => h !== hour);
            dayObj.preferred = dayObj.preferred.filter(h => h !== hour);
        }

        const newNext = { ...next };
        if (dayObj.unavailable.length === 0 && dayObj.preferred.length === 0) {
            delete newNext[dayIndex];
        } else {
            newNext[dayIndex] = { unavailable: dayObj.unavailable.slice().sort((a, b) => a - b), preferred: dayObj.preferred.slice().sort((a, b) => a - b) };
        }

        setLocalValue(newNext);
        emitNormalized(newNext);
    };

    return (
        <table className="unavailable-grid-table" role="grid" style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
                <tr>
                    <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>Hora</th>
                    {daysList.map((day, idx) => (
                        <th key={idx} style={{ textAlign: 'center', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>{day}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {Array.from({ length: classesPerDay }).map((_, hour) => (
                    <tr key={hour}>
                        <td style={{ padding: '0.25rem 0.5rem', verticalAlign: 'middle', borderBottom: '1px solid #f2f2f2' }}>{hourNames[hour] ?? `Hora ${hour}`}</td>
                        {daysList.map((day, idx) => {
                            const status = getStatus(idx, hour);
                            const classNames = ['unavailable-slot'];
                            if (status === 'unavailable') classNames.push('selected');
                            if (status === 'preferred') classNames.push('preferred', 'selected');
                            const state = status === 'preferred' ? 'preferred' : (status === 'unavailable' ? 'unavailable' : 'available');
                            const ariaPressed = state === 'available' ? 'false' : (state === 'preferred' ? 'mixed' : 'true');
                            const pref = state === 'available' ? t('preferences.none') : (state === 'unavailable' ? t('preferences.unavailable') : t('preferences.preferred'));
                            const slotLabel = `${day} ${hourNames[hour] ?? `Hora ${hour}`} ${pref}`;
                            return (
                                <td key={idx} style={{ textAlign: 'center', padding: '0.25rem', borderBottom: '1px solid #f9f9f9' }}>
                                    <button
                                        type="button"
                                        className={classNames.join(' ')}
                                        data-state={state}
                                        onClick={() => toggle(idx, hour)}
                                        aria-pressed={ariaPressed}
                                        aria-label={slotLabel}
                                        title={slotLabel}
                                    >
                                        <span className="slot-toggle" aria-hidden="true">
                                            <span className="slot-toggle-handle" />
                                        </span>
                                    </button>
                                </td>
                            );
                        })}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}
