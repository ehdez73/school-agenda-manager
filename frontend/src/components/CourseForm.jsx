
import { t } from '../i18n';
import useEscapeToCancel from './useEscapeToCancel';

export default function CourseForm({ form, setForm, editingId, onSubmit, onCancel, onDelete }) {
    useEscapeToCancel(onCancel);

    const getLineSuffix = (index) => {
        let value = index + 1;
        let suffix = '';
        while (value > 0) {
            value -= 1;
            suffix = String.fromCharCode(65 + (value % 26)) + suffix;
            value = Math.floor(value / 26);
        }
        return suffix;
    };

    const numLines = Number.parseInt(form.num_lines, 10);
    const safeNumLines = Number.isFinite(numLines) && numLines > 0 ? numLines : 0;
    const courseName = (form.name || '').trim();
    const groupPreview = safeNumLines > 0 && courseName
        ? Array.from({ length: safeNumLines }, (_, i) => `${courseName}${getLineSuffix(i)}`).join(', ')
        : '';

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
                        placeholder={t('courses.name_placeholder')}
                        required
                        className="course-input"
                        disabled={editingId !== null}
                    />
                </label>
            </div>
            <div className="course-form-row course-form-row--split">
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
                <div className="course-preview" aria-live="polite">
                    <span className="course-preview__label">{t('courses.groups')}</span>
                    <span className="course-preview__value">{groupPreview || '-'}</span>
                </div>
            </div>
            <div className="course-form-actions">
                <button type="submit" className="btn btn--primary">{t('common.save')}</button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                {onDelete && <button type="button" className="btn btn--danger" onClick={onDelete}>{t('common.delete')}</button>}
            </div>
        </form>
    );
}
