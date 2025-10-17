import React from 'react';
import { t } from '../i18n';

export default function SubjectForm({ form, setForm, courses, subjects = [], lockedHours, editingId, formError, onSubmit, onCancel, daysPerWeek }) {
    const handleChange = (e) => {
        let value;
        if (e.target.type === 'checkbox') {
            value = e.target.checked;
        } else if (e.target.name === 'consecutive_hours' || e.target.name === 'teach_every_day') {
            // convert select string value to boolean
            value = e.target.value === 'true';
        } else {
            value = e.target.value;
        }
        // If course is changed, ensure linked_subject_id still matches the new course
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
            setForm({ ...form, course_id: newCourseId, linked_subject_id: newLinked });
            return;
        }

        setForm({ ...form, [e.target.name]: value });
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
                {t('subjects.course')}
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
                <select
                    name="linked_subject_id"
                    value={form.linked_subject_id || ''}
                    onChange={handleChange}
                    className="subject-select"
                >
                    <option value="">{t('common.dashes') || '—'}</option>
                    {subjects
                        .filter(s => {
                            if (!s || s.id === form.id) return false;
                            const subjCourseId = s.course ? s.course.id : s.course_id;
                            // only include subjects that belong to the same course as current form
                            return form.course_id && subjCourseId && String(subjCourseId) === String(form.course_id);
                        })
                        .map(s => (
                            <option key={s.id} value={s.id}>{s.full_name || s.name}</option>
                        ))}
                </select>
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
