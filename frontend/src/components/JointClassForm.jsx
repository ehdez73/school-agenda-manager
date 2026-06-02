import { useMemo } from 'react';
import { t } from '../i18n';
import useEscapeToCancel from './useEscapeToCancel';

function generateLineLetters(numLines) {
    return Array.from({ length: numLines }, (_, i) => String.fromCharCode(65 + i));
}

export default function JointClassForm({
    form, setForm, courses = [], subjects = [], teachers = [],
    formError, onSubmit, onCancel, onDelete,
}) {
    useEscapeToCancel(onCancel);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    const selectedCourse = courses?.find(c => c.id === form.course_id);
    const numLines = selectedCourse ? selectedCourse.num_lines : 0;
    const lineLetters = useMemo(() => generateLineLetters(numLines), [numLines]);

    const filteredSubjects = useMemo(() => {
        if (!form.course_id) return [];
        return subjects.filter(s => {
            const cid = s.course ? s.course.id : s.course_id;
            return cid === form.course_id;
        });
    }, [form.course_id, subjects]);

    const filteredTeachers = useMemo(() => {
        if (!form.subject_id) return teachers;
        return teachers.filter(t =>
            t.subjects?.some(s => String(s.id) === String(form.subject_id))
        );
    }, [form.subject_id, teachers]);

    const handleLineToggle = (lineLetter) => {
        const current = form.lines || [];
        const idx = current.indexOf(lineLetter);
        let next;
        if (idx >= 0) {
            next = current.filter(l => l !== lineLetter);
        } else {
            next = [...current, lineLetter].sort();
        }
        setForm({ ...form, lines: next });
    };

    const isLineSelected = (letter) => {
        return (form.lines || []).includes(letter);
    };

    return (
        <form onSubmit={onSubmit} className="subject-form">
            {formError && <div className="form-error">{formError}</div>}

            <label className="subject-label">
                {t('joint_classes.course')}
                <select
                    name="course_id"
                    value={form.course_id || ''}
                    onChange={handleChange}
                    className="subject-input"
                    required
                >
                    <option value="">--</option>
                    {courses.map(c => (
                        <option key={c.id} value={c.id}>{c.id}</option>
                    ))}
                </select>
            </label>

            <label className="subject-label">
                {t('joint_classes.subject')}
                <select
                    name="subject_id"
                    value={form.subject_id || ''}
                    onChange={handleChange}
                    className="subject-input"
                    required
                    disabled={!form.course_id}
                >
                    <option value="">--</option>
                    {filteredSubjects.map(s => (
                        <option key={s.id} value={s.id}>{s.full_name || s.name}</option>
                    ))}
                </select>
            </label>

            <label className="subject-label">
                {t('joint_classes.teacher')}
                <select
                    name="teacher_id"
                    value={form.teacher_id ?? ''}
                    onChange={e => setForm({
                        ...form,
                        teacher_id: e.target.value === '' ? null : (Number(e.target.value) || e.target.value),
                    })}
                    className="subject-input"
                    disabled={!form.subject_id}
                >
                    <option value="">{t('joint_classes.teacher_none')}</option>
                    {filteredTeachers.map(tch => (
                        <option key={tch.id} value={tch.id}>{tch.name}</option>
                    ))}
                </select>
            </label>

            <label className="subject-label">
                {t('joint_classes.name')}
                <input
                    name="name"
                    value={form.name || ''}
                    onChange={handleChange}
                    placeholder={t('joint_classes.name_placeholder')}
                    className="subject-input"
                />
            </label>

            <label className="subject-label">
                {t('joint_classes.shared_hours')}
                <input
                    name="shared_hours"
                    type="number"
                    min="1"
                    value={form.shared_hours ?? ''}
                    onChange={e => setForm({
                        ...form,
                        shared_hours: e.target.value === '' ? null : Number(e.target.value),
                    })}
                    placeholder={t('joint_classes.all_hours')}
                    className="subject-input"
                />
            </label>

            {numLines > 1 && (
                <fieldset className="lines-fieldset">
                    <legend>{t('joint_classes.lines')}</legend>
                    <p className="lines-hint">{t('subjects.lines')}</p>
                    <div className="lines-checkboxes">
                        {lineLetters.map((letter) => (
                            <label key={letter} className="line-checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={isLineSelected(letter)}
                                    onChange={() => handleLineToggle(letter)}
                                />
                                {letter}
                            </label>
                        ))}
                    </div>
                    {(form.lines || []).length < 2 && (
                        <div className="form-error" style={{ marginTop: 'var(--space-sm)' }}>
                            Select at least 2 lines
                        </div>
                    )}
                </fieldset>
            )}

            <div className="form-actions">
                <button type="submit" className="btn btn--primary" disabled={(form.lines || []).length < 2}>
                    {t('common.save')}
                </button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>
                    {t('common.cancel')}
                </button>
                {onDelete && (
                    <button type="button" className="btn btn--danger" onClick={onDelete}>
                        {t('common.delete')}
                    </button>
                )}
            </div>
        </form>
    );
}
