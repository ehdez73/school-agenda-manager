import { useEffect } from 'react';
import { t } from '../i18n';
import Select from './Select';

export default function DayIndices({ daysPerWeek = 5, dayIndices = [], setDayIndices = () => { }, suppressResize = false, dayColors = {}, setDayColors = () => {} }) {
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

    const handleColorChange = (dayIdx, value) => {
        setDayColors(prev => ({ ...prev, [String(dayIdx)]: value }));
    };

    return (
        <div className="mt-md">
            <h4 className="day-indices-title">{t('days.names_title')}</h4>
            <div className="day-indices-grid">
                {displayIndices.map((idx, i) => (
                    <div key={i} className="day-index-row">
                        <span className="day-index-row__label">{t('days.label').replace('{n}', String(i + 1))}</span>
                        <Select
                            value={idx}
                            onChange={e => handleDayIndexChange(i, e.target.value)}
                            options={dayOptions}
                        />
                        <input
                            type="color"
                            className="day-index-row__color"
                            value={dayColors[String(idx)] || '#ffffff'}
                            onChange={e => handleColorChange(idx, e.target.value)}
                            title={t('config.day_colors_title')}
                        />
                    </div>
                ))}
            </div>
        </div>
    );
}