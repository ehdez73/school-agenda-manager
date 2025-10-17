import React from 'react';
import PreferencesGrid from './PreferencesGrid';
import { t } from '../i18n';

export default function TeacherForm({ form, setForm, subjects, classesPerDay, onSubmit, onCancel, groups = [] }) {
    const handleChange = (e) => {
        const { name, value, selectedOptions } = e.target;
        if (name === 'subjects') {
            const values = Array.from(selectedOptions, opt => Number(opt.value));
            setForm({ ...form, subjects: values });
        } else {
            setForm({ ...form, [name]: value });
        }
    };

    return (
        <form onSubmit={onSubmit} className="teacher-form">
            <div className="teacher-form-row">
                <div className="teacher-form-col1">
                    <label className="teacher-label">{t('teachers.name')}:</label>
                    <input
                        name="name"
                        value={form.name}
                        onChange={handleChange}
                        placeholder={t('teachers.name_placeholder')}
                        required
                        className="teacher-input"
                    />
                    <label className="teacher-label teacher-label-margin">{t('teachers.hours_week')}:</label>
                    <input
                        name="max_hours_week"
                        type="number"
                        min="0"
                        value={form.max_hours_week}
                        onChange={handleChange}
                        placeholder={t('teachers.hours_week')}
                        className="teacher-input"
                    />
                    <label className="teacher-label">{t('subjects.title')}:</label>
                    <select
                        name="subjectsDropdown"
                        value=""
                        onChange={e => {
                            const id = e.target.value;
                            if (id && !form.subjects.includes(id)) {
                                setForm(f => ({ ...f, subjects: [...f.subjects, id] }));
                            }
                        }}
                        className="teacher-select"
                    >
                        <option value="">{t('subjects.add_subject')}</option>
                        {subjects
                            .filter(s => !form.subjects.includes(String(s.id)))
                            .sort((a, b) => (a.full_name || a.name).localeCompare(b.full_name || b.name))
                            .map(s => (
                                <option key={s.id} value={s.id}>
                                    {s.full_name || s.name}
                                </option>
                            ))}
                    </select>
                    <label className="teacher-label" style={{ marginTop: '0.5rem' }}>{t('teachers.tutor_group')}:</label>
                    <select
                        name="tutor_group"
                        value={form.tutor_group || ''}
                        onChange={handleChange}
                        className="teacher-select"
                    >
                        <option value="">{t('teachers.no_tutor')}</option>
                        {groups
                            // show only groups without a tutor (null/undefined), or the group currently assigned to this teacher
                            .filter(g => (g.tutor_id == null) || String(g.tutor_id) === String(form.id))
                            .sort((a, b) => (a.name || '').localeCompare(b.name || ''))
                            .map(g => (
                                <option key={g.id} value={g.id}>
                                    {g.name}
                                </option>
                            ))}
                    </select>
                    <div className="teacher-subject-list">
                        {form.subjects.map(id => {
                            const subj = subjects.find(s => String(s.id) === String(id));
                            if (!subj) return null;
                            return (
                                <span key={id} className="teacher-subject-chip">
                                    {subj.full_name || subj.name}
                                    <button type="button" className="teacher-chip-btn" onClick={() => setForm(f => ({ ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)) }))}>×</button>
                                </span>
                            );
                        })}
                    </div>
                </div>

            </div>
            {/* Cuadrícula de No disponible / Preferencia */}
            <div className="teacher-form-section">
                <label className="teacher-label teacher-label-margin">{t('common.edit')} (clic para alternar):</label>
                <PreferencesGrid
                    value={form.preferences}
                    onChange={v => setForm(f => ({ ...f, preferences: v }))}
                    classesPerDay={classesPerDay}
                />
                <div className="unavailable-legend">
                    <div className="item"><div className="box unavailable" /> {t('preferences.unavailable')}</div>
                    <div className="item"><div className="box preferred" /> {t('preferences.preferred')}</div>
                </div>
            </div>
            <div className="teacher-form-actions">
                <button type="submit" className="teacher-btn">
                    {t('common.save')}
                </button>
                <button type="button" className="teacher-btn teacher-btn-cancel" onClick={onCancel}>
                    {t('common.cancel')}
                </button>
            </div>
        </form>
    );
}
