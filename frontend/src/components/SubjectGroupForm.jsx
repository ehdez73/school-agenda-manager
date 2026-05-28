import React from 'react';
import AutocompleteSelect from './AutocompleteSelect';
import { t } from '../i18n';

export default function SubjectGroupForm({ form, setForm, subjects, formError, onSubmit, onCancel, onDelete }) {
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
            </label>
            <AutocompleteSelect
                items={subjects}
                selectedIds={form.subjects}
                onAdd={id => setForm(f => ({ ...f, subjects: [...f.subjects, id] }))}
                onRemove={id => setForm(f => ({ ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)) }))}
                placeholder={t('subjects.add_subject') + '...'}
                noResultsText="No subjects found"
            />
            {formError && <div className="form-error">{formError}</div>}
            <div className="form-actions">
                <button type="submit" className="btn btn--primary">{t('common.save')}</button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                {onDelete && <button type="button" className="btn btn--danger" onClick={onDelete}>{t('common.delete')}</button>}
            </div>
        </form>
    );
}
