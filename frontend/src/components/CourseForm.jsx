import React from 'react';
import { t } from '../i18n';

export default function CourseForm({ form, setForm, editingId, onSubmit, onCancel }) {
    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name === 'num_lineas' || name === 'num_lines') {
            setForm({ ...form, num_lines: value });
        } else {
            setForm({ ...form, [name]: value });
        }
    };

    return (
        <form onSubmit={onSubmit} className="course-form">
            <div className="course-form-row">
                <label className="course-label">
                    {t('courses.name')}
                    <input
                        name="name"
                        value={form.name}
                        onChange={handleChange}
                        placeholder={t('common.search_placeholder')}
                        required
                        className="course-input"
                        disabled={editingId !== null}
                    />
                </label>
            </div>
            <div className="course-form-row">
                <label className="course-label">
                    {t('courses.num_lines')}
                    <input
                        name="num_lines"
                        type="number"
                        min={1}
                        value={form.num_lines}
                        onChange={handleChange}
                        placeholder={t('courses.num_lines')}
                        required
                        className="course-input course-input-short"
                    />
                </label>
            </div>
            <div className="course-form-actions">
                <button type="submit" className="course-btn">{t('common.save')}</button>
                <button type="button" className="course-btn course-btn-cancel" onClick={onCancel}>{t('common.cancel')}</button>
            </div>
        </form>
    );
}
