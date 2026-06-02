
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

    function handleLineToggle(subjectId, lineIndex) {
        setForm(f => {
            const current = f.teacher_subject_lines?.[subjectId];
            const subject = subjects.find(s => String(s.id) === String(subjectId));
            const numLines = subject?.course?.num_lines || 1;
            const allLines = Array.from({ length: numLines }, (_, i) => i);
            // undefined or null means all lines checked
            const checked = current === undefined || current === null
                ? [...allLines]
                : [...current];
            const idx = checked.indexOf(lineIndex);
            if (idx >= 0) {
                checked.splice(idx, 1);
            } else {
                checked.push(lineIndex);
                checked.sort((a, b) => a - b);
            }
            const updated = { ...(f.teacher_subject_lines || {}) };
            if (checked.length === numLines || checked.length === 0) {
                delete updated[subjectId];
            } else {
                updated[subjectId] = checked;
            }
            return { ...f, teacher_subject_lines: updated };
        });
    }

    function isLineChecked(subjectId, lineIndex) {
        const current = form.teacher_subject_lines?.[subjectId];
        if (current === undefined || current === null) return true;
        return current.includes(lineIndex);
    }

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
                    <label className="teacher-label teacher-label-margin">{t('teachers.coordination_hours')}:</label>
                    <input
                        name="coordination_hours"
                        type="number"
                        min="0"
                        value={form.coordination_hours}
                        onChange={handleChange}
                        placeholder={t('teachers.coordination_hours')}
                        className="teacher-input"
                    />
                    <label className="teacher-label">{t('subjects.title')}:</label>
                    <AutocompleteSelect
                        items={subjects}
                        selectedIds={form.subjects}
                        onAdd={id => {
                            setForm(f => {
                                const subj = subjects.find(s => String(s.id) === String(id));
                                const numLines = subj?.course?.num_lines || 1;
                                // If the subject's course has only 1 line, no restriction needed
                                if (numLines <= 1) return { ...f, subjects: [...f.subjects, id] };
                                return { ...f, subjects: [...f.subjects, id] };
                            });
                        }}
                        onRemove={id => setForm(f => {
                            const updated = { ...(f.teacher_subject_lines || {}) };
                            delete updated[id];
                            return { ...f, subjects: f.subjects.filter(sid => String(sid) !== String(id)), teacher_subject_lines: updated };
                        })}
                        placeholder={t('subjects.add_subject') + '...'}
                        noResultsText="No subjects found"
                    />

                    {/* Line restrictions: show for subjects whose course has >1 line */}
                    {form.subjects.filter(sid => {
                        const subj = subjects.find(s => String(s.id) === String(sid));
                        return subj && (subj.course?.num_lines || 1) > 1;
                    }).length > 0 && (
                        <div className="teacher-form-section">
                            <label className="teacher-label teacher-label-margin">{t('teachers.line_restrictions')}:</label>
                            {form.subjects.map(sid => {
                                const subj = subjects.find(s => String(s.id) === String(sid));
                                if (!subj) return null;
                                const numLines = subj.course?.num_lines || 1;
                                if (numLines <= 1) return null;
                                return (
                                    <div key={sid} className="teacher-line-row">
                                        <span className="teacher-line-subject">{subj.name} ({subj.course?.name || subj.course_id})</span>
                                        <div className="teacher-lines">
                                            {Array.from({ length: numLines }, (_, i) => (
                                                <label key={i} className="teacher-line-checkbox">
                                                    <input
                                                        type="checkbox"
                                                        checked={isLineChecked(sid, i)}
                                                        onChange={() => handleLineToggle(sid, i)}
                                                    />
                                                    <span>{String.fromCharCode(65 + i)}</span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

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
