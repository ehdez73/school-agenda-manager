import React, { useMemo } from 'react';
import AutocompleteSelect from './AutocompleteSelect';
import { t } from '../i18n';
import useEscapeToCancel from './useEscapeToCancel';

function generateLineLetters(numLines) {
    return Array.from({ length: numLines }, (_, i) => String.fromCharCode(65 + i));
}

function getDefaultIncludedLines(numLines) {
    // null means all lines
    return null;
}

function toggleLine(included, lineIndex, numLines) {
    if (included === null) {
        const result = [];
        for (let i = 0; i < numLines; i++) {
            if (i !== lineIndex) result.push(i);
        }
        return result;
    }
    const set = new Set(included);
    if (set.has(lineIndex)) {
        set.delete(lineIndex);
    } else {
        set.add(lineIndex);
    }
    const result = Array.from(set).sort((a, b) => a - b);
    if (result.length === 0) return [];
    if (result.length === numLines) return null;
    return result;
}

export default function SubjectForm({ form, setForm, courses, subjects = [], editingId, formError, onSubmit, onCancel, onDelete, daysPerWeek, subject }) {
    useEscapeToCancel(onCancel);

    const selectedCourse = useMemo(() => courses.find(c => c.id === form.course_id), [courses, form.course_id]);
    const numLines = selectedCourse ? selectedCourse.num_lines : 0;
    const lineLetters = useMemo(() => generateLineLetters(numLines), [numLines]);

    const handleChange = (e) => {
        let value;
        if (e.target.type === 'checkbox') {
            value = e.target.checked;
        } else if (e.target.name === 'consecutive_hours' || e.target.name === 'teach_every_day') {
            value = e.target.value === 'true';
        } else {
            value = e.target.value;
        }
        if (e.target.name === 'course_id') {
            const newCourseId = value;
            let newLinked = form.linked_subject_id;
            if (newLinked) {
                const linkedObj = subjects.find(s => s.id === newLinked);
                const linkedCourseId = linkedObj ? (linkedObj.course ? linkedObj.course.id : linkedObj.course_id) : null;
                if (!linkedCourseId || String(linkedCourseId) !== String(newCourseId)) {
                    newLinked = '';
                }
            }
            setForm({ ...form, course_id: newCourseId, linked_subject_id: newLinked, included_lines: null });
            return;
        }

        setForm({ ...form, [e.target.name]: value });
    };

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
                ID
                <input
                    name="id"
                    value={form.id || ''}
                    onChange={handleChange}
                    placeholder={t('common.add') + ' ID'}
                    required
                    className="subject-input"
                    disabled={editingId !== null}
                />
            </label>
            <label className="subject-label">
                {t('subjects.name')}
                <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder={t('subjects.name_placeholder')}
                    required
                    className="subject-input"
                />
            </label>
            <label className="subject-label">
                {t('subjects.color')}
                <div className="subject-color-row">
                    <input
                        name="color"
                        type="color"
                        value={form.color || '#f1f5f9'}
                        onChange={handleChange}
                        className="subject-color-picker"
                    />
                    <span className="subject-color-value">{(form.color || '#f1f5f9').toUpperCase()}</span>
                </div>
            </label>
            <label className="subject-label">
                {t('subjects.course')}
                <select
                    name="course_id"
                    value={form.course_id}
                    onChange={handleChange}
                    required
                    className="subject-select"
                >
                    <option value="">{t('common.search_placeholder')}</option>
                    {[...courses].sort((a, b) => (a.name || '').localeCompare(b.name || '')).map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                </select>
            </label>
            {numLines > 1 && (
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
                            {form.included_lines === null ? t('common.all') : ''}
                        </span>
                    </div>
                </fieldset>
            )}
            <label className="subject-label">
                {t('subjects.weekly_hours')}
                <input
                    name="weekly_hours"
                    type="number"
                    min={1}
                    value={form.weekly_hours}
                    onChange={handleChange}
                    placeholder={t('subjects.weekly_hours')}
                    required
                    className="subject-input subject-input-short"
                />
            </label>
            <label className="subject-label">
                {t('subjects.max_hours_per_day')}
                <input
                    name="max_hours_per_day"
                    type="number"
                    min={1}
                    value={form.max_hours_per_day}
                    onChange={handleChange}
                    placeholder={t('subjects.max_hours_per_day')}
                    required
                    className="subject-input subject-input-short"
                />
            </label>
            {form.max_hours_per_day > 1 && (
                <label className="subject-label">
                    {t('subjects.consecutive_hours')}
                    <select
                        name="consecutive_hours"
                        value={String(form.consecutive_hours ?? true)}
                        onChange={handleChange}
                        className="subject-select"
                    >
                        <option value="true">{t('common.yes') || 'Yes'}</option>
                        <option value="false">{t('common.no') || 'No'}</option>
                    </select>
                </label>
            )}
           
            {typeof daysPerWeek === 'number' && Number(form.weekly_hours) >= daysPerWeek && (
                <label className="subject-label">
                    {t('subjects.teach_every_day') || 'Teach every day'}
                    <select
                        name="teach_every_day"
                        value={String(form.teach_every_day ?? false)}
                        onChange={handleChange}
                        className="subject-select"
                    >
                        <option value="true">{t('common.yes') || 'Yes'}</option>
                        <option value="false">{t('common.no') || 'No'}</option>
                    </select>
                </label>
            )}
             <label className="subject-label">
                {t('subjects.linked_subject') || 'Linked subject'}
            </label>
            <AutocompleteSelect
                items={subjects.filter(s => {
                    if (!s || s.id === form.id) return false;
                    const subjCourseId = s.course ? s.course.id : s.course_id;
                    return form.course_id && subjCourseId && String(subjCourseId) === String(form.course_id);
                })}
                selectedIds={form.linked_subject_id ? [form.linked_subject_id] : []}
                onAdd={id => setForm({ ...form, linked_subject_id: id })}
                onRemove={() => setForm({ ...form, linked_subject_id: '' })}
                placeholder={`${t('subjects.add_subject')}...`}
                noResultsText="No subjects available"
                singleSelect={true}
            />
            {formError && <div className="form-error">{formError}</div>}
            {subject && (
                <div className="subject-teachers">
                    <h4>{t('subjects.assigned_teachers')}</h4>
                    {subject.teachers && subject.teachers.length > 0 ? (
                        <ul className="teacher-list">
                            {subject.teachers.map(t => (
                                <li key={t.id}>{t.name}</li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-muted">{t('subjects.no_teachers')}</p>
                    )}
                </div>
            )}
            <div className="form-actions">
                <button type="submit" className="btn btn--primary">
                    {t('common.save')}
                </button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>
                    {t('common.cancel')}
                </button>
                {onDelete && <button type="button" className="btn btn--danger" onClick={onDelete}>{t('common.delete')}</button>}
            </div>
        </form>
    );
}
