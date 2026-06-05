
import { t } from '../i18n';
import useEscapeToCancel from './useEscapeToCancel';

export default function FixedSlotForm({ form, setForm, formError, onSubmit, onCancel, onDelete }) {
    useEscapeToCancel(onCancel);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    return (
        <form onSubmit={onSubmit} className="subject-form">
            <label className="subject-label">
                {t('fixed_slots.position')}
                <input
                    name="position"
                    type="number"
                    min="1"
                    step="1"
                    value={form.position}
                    onChange={handleChange}
                    placeholder={t('fixed_slots.position_placeholder')}
                    required
                    className="subject-input"
                />
            </label>
            <label className="subject-label">
                {t('fixed_slots.label')}
                <input
                    name="label"
                    value={form.label}
                    onChange={handleChange}
                    placeholder={t('fixed_slots.label_placeholder')}
                    required
                    className="subject-input"
                />
            </label>
            <label className="subject-label">
                {t('fixed_slots.time_range')}
                <input
                    name="time_range"
                    value={form.time_range}
                    onChange={handleChange}
                    placeholder={t('fixed_slots.time_range_placeholder')}
                    required
                    className="subject-input"
                />
            </label>
            <label className="subject-label">
                {t('fixed_slots.color')}
                <div className="subject-color-row">
                    <input
                        name="color"
                        type="color"
                        value={form.color || '#f1f5f9'}
                        onChange={handleChange}
                        className="subject-color-picker"
                    />
                    <span className="subject-color-value">{(form.color || '#f1f5f9').toUpperCase()}</span>
                </div>
            </label>
            {formError && <div className="form-error">{formError}</div>}
            <div className="form-actions">
                <button type="submit" className="btn btn--primary">{t('common.save')}</button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                {onDelete && <button type="button" className="btn btn--danger" onClick={onDelete}>{t('common.delete')}</button>}
            </div>
        </form>
    );
}
