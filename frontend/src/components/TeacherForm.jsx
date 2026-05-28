import React from 'react';
import AutocompleteSelect from './AutocompleteSelect';
import PreferencesGrid from './PreferencesGrid';
import { t } from '../i18n';

export default function TeacherForm({ form, setForm, subjects, classesPerDay, onSubmit, onCancel, onDelete, groups = [] }) {
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
                    <AutocompleteSelect
                        items={subjects}
                        selectedIds={form.subjects}
                        onAdd={id => setForm(f => ({ ...f, subjects: [...f.subjects, id] }))}
                        onRemove={id => setForm(f => ({ ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)) }))}
                        placeholder={t('subjects.add_subject') + '...'}
                        noResultsText="No subjects found"
                    />
                    <label className="teacher-label teacher-label-margin">{t('teachers.tutor_group')}:</label>
                    <select
                        name="tutor_group"
                        value={form.tutor_group || ''}
                        onChange={handleChange}
                        className="teacher-select"
                    >
                        <option value="">{t('teachers.no_tutor')}</option>
                        {groups
                            .filter(g => (g.tutor_id == null) || String(g.tutor_id) === String(form.id))
                            .sort((a, b) => (a.name || '').localeCompare(b.name || ''))
                            .map(g => (
                                <option key={g.id} value={g.id}>
                                    {g.name}
                                </option>
                            ))}
                    </select>
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
