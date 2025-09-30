import React from 'react';
import { t } from '../i18n';

export default function SubjectForm({ form, setForm, courses, lockedHours, editingId, formError, onSubmit, onCancel }) {
    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    return (
        <form onSubmit={onSubmit} className="subject-form">
            <label className="subject-label">
                {t('common.add')} ID
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
                {t('subjects.title')}
                <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    placeholder={t('subjects.title')}
                    required
                    className="subject-input"
                />
            </label>
            <label className="subject-label">
                {t('courses.name')}
                <select
                    name="course_id"
                    value={form.course_id}
                    onChange={handleChange}
                    required
                    className="subject-select"
                >
                    <option value="">{t('common.search_placeholder')}</option>
                    {courses.map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                </select>
            </label>
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
                    disabled={lockedHours}
                />
            </label>
            {lockedHours && <div className="form-error">{t('subject_groups.error_hours_mismatch')}</div>}
            {formError && <div className="form-error">{formError}</div>}
            <div className="subject-form-actions">
                <button type="submit" className="subject-btn">
                    {t('common.save')}
                </button>
                <button type="button" className="subject-btn subject-btn-cancel" onClick={onCancel}>
                    {t('common.cancel')}
                </button>
            </div>
        </form>
    );
}
