import React from 'react';
import { t } from '../i18n';

export default function SubjectGroupForm({ form, setForm, subjects, formError, onSubmit, onCancel }) {
    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    return (
        <form onSubmit={onSubmit} className="subject-form">
            <label className="subject-label">
                {t('subject_groups.name')}
                <input name="name" value={form.name} onChange={handleChange} placeholder={t('subject_groups.name_placeholder')} required className="subject-input" />
            </label>
            <label className="subject-label">
                {t('subject_groups.title') + ' - ' + t('subjects.title')}
                <select
                    name="subjectsDropdown"
                    value=""
                    onChange={e => {
                        const id = e.target.value;
                        if (id && !form.subjects.includes(id)) {
                            setForm(f => ({ ...f, subjects: [...f.subjects, id] }));
                        }
                    }}
                    className="subject-select"
                >
                    <option value="">{t('subjects.add_subject')}</option>
                    {subjects
                        .filter(s => !form.subjects.includes(String(s.id)))
                        .sort((a, b) => (a.full_name || a.name).localeCompare(b.full_name || b.name))
                        .map(s => (
                            <option key={s.id} value={s.id}>{s.full_name || s.name}</option>
                        ))}
                </select>
            </label>
            {formError && <div className="form-error">{formError}</div>}
            <div className="teacher-subject-list">
                {form.subjects.map(id => {
                    const subj = subjects.find(s => String(s.id) === String(id));
                    if (!subj) return null;
                    return (
                        <span key={id} className="chip">
                            {subj.full_name || subj.name}
                            <button type="button" className="chip__remove" onClick={() => setForm(f => ({ ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)) }))}>×</button>
                        </span>
                    );
                })}
            </div>
            <div className="subject-form-actions">
                <button type="submit" className="subject-btn">{t('common.save')}</button>
                <button type="button" className="subject-btn subject-btn-cancel" onClick={onCancel}>{t('common.cancel')}</button>
            </div>
        </form>
    );
}
