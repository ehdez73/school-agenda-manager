import React from 'react';
import AutocompleteSelect from './AutocompleteSelect';
import PreferencesGrid from './PreferencesGrid';
import { t } from '../i18n';
import useEscapeToCancel from './useEscapeToCancel';

export default function TeacherForm({ form, setForm, subjects, classesPerDay, onSubmit, onCancel, onDelete, groups = [] }) {
    useEscapeToCancel(onCancel);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    const tutorGroups = form.tutor_groups || [];
    const availableGroups = groups.filter(group => {
        if (!group) return false;
        if (!group.tutor_ids || group.tutor_ids.length === 0) return true;
        return group.tutor_ids.some(id => String(id) === String(form.id));
    });

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
                    <AutocompleteSelect
                        items={availableGroups.sort((a, b) => (a.name || '').localeCompare(b.name || ''))}
                        selectedIds={tutorGroups}
                        onAdd={id => setForm(f => ({ ...f, tutor_groups: [...(f.tutor_groups || []), id] }))}
                        onRemove={id => setForm(f => ({ ...f, tutor_groups: (f.tutor_groups || []).filter(groupId => String(groupId) !== String(id)) }))}
                        placeholder={t('teachers.tutor_group') + '...'}
                        noResultsText="No tutor groups found"
                    />
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
