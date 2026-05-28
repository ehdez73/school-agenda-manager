import React, { useMemo } from 'react';
import AutocompleteSelect from './AutocompleteSelect';
import { t } from '../i18n';
import useEscapeToCancel from './useEscapeToCancel';

function generateLineLetters(numLines) {
    return Array.from({ length: numLines }, (_, i) => String.fromCharCode(65 + i));
}

function toggleLine(included, lineIndex, numLines) {
    if (included === null) {
        const result = [];
        for (let i = 0; i < numLines; i++) {
            if (i !== lineIndex) result.push(i);
        }
        return result.length === numLines ? null : result;
    }
    const set = new Set(included);
    if (set.has(lineIndex)) {
        set.delete(lineIndex);
    } else {
        set.add(lineIndex);
    }
    const result = Array.from(set).sort((a, b) => a - b);
    return result.length === 0 ? null : result;
}

export default function SubjectGroupForm({ form, setForm, subjects, formError, onSubmit, onCancel, onDelete, courses }) {
    useEscapeToCancel(onCancel);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    const courseIds = useMemo(() => {
        const ids = new Set();
        for (const sid of form.subjects) {
            const s = subjects.find(sbj => String(sbj.id) === String(sid));
            if (s) {
                const cid = s.course ? s.course.id : s.course_id;
                if (cid) ids.add(cid);
            }
        }
        return Array.from(ids);
    }, [form.subjects, subjects]);

    const selectedCourse = useMemo(() => {
        if (courseIds.length === 1) {
            return courses.find(c => c.id === courseIds[0]);
        }
        return null;
    }, [courseIds, courses]);

    const numLines = selectedCourse ? selectedCourse.num_lines : 0;
    const lineLetters = useMemo(() => generateLineLetters(numLines), [numLines]);

    const handleLineToggle = (lineIndex) => {
        const current = form.included_lines;
        const next = toggleLine(current, lineIndex, numLines);
        setForm({ ...form, included_lines: next });
    };

    const isLineChecked = (lineIndex) => {
        if (form.included_lines === null) return true;
        return form.included_lines.includes(lineIndex);
    };

    return (
        <form onSubmit={onSubmit} className="subject-form">
            <label className="subject-label">
                {t('subject_groups.name')}
                <input name="name" value={form.name} onChange={handleChange} placeholder={t('subject_groups.name_placeholder')} required className="subject-input" />
            </label>
            <label className="subject-label">
                {t('subject_groups.color')}
                <div className="subject-color-row">
                    <input
                        name="color"
                        type="color"
                        value={form.color || '#fef3c7'}
                        onChange={handleChange}
                        className="subject-color-picker"
                    />
                    <span className="subject-color-value">{(form.color || '#fef3c7').toUpperCase()}</span>
                </div>
            </label>
            <label className="subject-label">
                {t('subject_groups.title') + ' - ' + t('subjects.title')}
            </label>
            <AutocompleteSelect
                items={subjects}
                selectedIds={form.subjects}
                onAdd={id => setForm(f => ({ ...f, subjects: [...f.subjects, id] }))}
                onRemove={id => setForm(f => ({ ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)) }))}
                placeholder={t('subjects.add_subject') + '...'}
                noResultsText="No subjects found"
            />
            {numLines > 1 && courseIds.length === 1 && (
                <fieldset className="lines-fieldset">
                    <legend>{t('subjects.lines')}</legend>
                    <div className="lines-checkboxes">
                        {lineLetters.map((letter, idx) => (
                            <label key={idx} className="line-checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={isLineChecked(idx)}
                                    onChange={() => handleLineToggle(idx)}
                                />
                                {letter}
                            </label>
                        ))}
                        <span className="lines-hint">
                            {form.included_lines === null ? '(all)' : ''}
                        </span>
                    </div>
                </fieldset>
            )}
            {formError && <div className="form-error">{formError}</div>}
            <div className="form-actions">
                <button type="submit" className="btn btn--primary">{t('common.save')}</button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                {onDelete && <button type="button" className="btn btn--danger" onClick={onDelete}>{t('common.delete')}</button>}
            </div>
        </form>
    );
}
