import { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import FixedSlotForm from './FixedSlotForm';
import SectionLayout from './SectionLayout';
import './FixedSlotList.css';

export default function FixedSlotList({ standalone = true }) {
    const [courseSlots, setCourseSlots] = useState([]);
    const [teacherSlots, setTeacherSlots] = useState([]);
    const [form, setForm] = useState({ position: '', label: '', time_range: '' });
    const [formError, setFormError] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [creatingType, setCreatingType] = useState(null);
    const [editingId, setEditingId] = useState(null);
    const [selectedEntity, setSelectedEntity] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteId, setDeleteId] = useState(null);

    useEffect(() => {
        fetchSlots();
    }, []);

    function fetchSlots() {
        api.get('/fixed-slots?type=course')
            .then(data => setCourseSlots(data.sort((a, b) => a.position - b.position)))
            .catch(() => setCourseSlots([]));
        api.get('/fixed-slots?type=teacher')
            .then(data => setTeacherSlots(data.sort((a, b) => a.position - b.position)))
            .catch(() => setTeacherSlots([]));
    }

    function handleSubmit(e) {
        e.preventDefault();
        setFormError('');
        const slotType = editingId ? selectedEntity.slot_type : creatingType;
        const payload = {
            slot_type: slotType,
            position: parseInt(form.position, 10),
            label: form.label,
            time_range: form.time_range,
        };
        if (isNaN(payload.position) || payload.position < 1) {
            setFormError('Position must be a positive number');
            return;
        }
        const action = editingId
            ? api.put(`/fixed-slots/${editingId}`, payload)
            : api.post('/fixed-slots', payload);
        action.then(() => {
            fetchSlots();
            setForm({ position: '', label: '', time_range: '' });
            setEditingId(null);
            setShowForm(false);
            setSelectedEntity(null);
            setCreatingType(null);
        }).catch(err => setFormError(err.message));
    }

    function handleEdit(slot) {
        setForm({
            position: String(slot.position),
            label: slot.label,
            time_range: slot.time_range,
        });
        setEditingId(slot.id);
        setShowForm(false);
        setSelectedEntity(slot);
        setCreatingType(null);
    }

    function handleDelete(id) {
        setDeleteId(id);
        setShowDeleteModal(true);
    }

    function confirmDelete() {
        api.del(`/fixed-slots/${deleteId}`).then(() => {
            fetchSlots();
            setShowDeleteModal(false);
            setDeleteId(null);
            setSelectedEntity(null);
            setEditingId(null);
            setForm({ position: '', label: '', time_range: '' });
        }).catch(() => {});
    }

    function cancelDelete() {
        setShowDeleteModal(false);
        setDeleteId(null);
    }

    function handleAdd(type) {
        setForm({ position: '', label: '', time_range: '' });
        setCreatingType(type);
        setShowForm(true);
        setSelectedEntity(null);
        setEditingId(null);
    }

    function handleCloseForm() {
        setForm({ position: '', label: '', time_range: '' });
        setEditingId(null);
        setShowForm(false);
        setSelectedEntity(null);
        setCreatingType(null);
        setFormError('');
    }

    function renderTable(slots) {
        if (slots.length === 0) {
            return <p className="text-muted">{t('fixed_slots.no_slots')}</p>;
        }
        return (
            <table className="modern-table">
                <thead>
                    <tr>
                        <th>{t('fixed_slots.position')}</th>
                        <th>{t('fixed_slots.time_range')}</th>
                        <th>{t('fixed_slots.label')}</th>
                    </tr>
                </thead>
                <tbody>
                    {slots.map(s => (
                        <tr key={s.id} onClick={() => handleEdit(s)} style={{ cursor: 'pointer' }}>
                            <td>{s.position}</td>
                            <td>{s.time_range}</td>
                            <td>{s.label}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    }

    function renderSection(type) {
        const slots = type === 'course' ? courseSlots : teacherSlots;
        return (
            <div className="fixed-slots-section">
                <div className="fixed-slots-section-header">
                    <h3 className="fixed-slots-section-title">
                        {type === 'course' ? t('fixed_slots.course_tab') : t('fixed_slots.teacher_tab')}
                    </h3>
                    {!showForm && !selectedEntity && (
                        <button
                            className="btn btn--primary btn--compact"
                            onClick={() => handleAdd(type)}
                        >
                            {t('fixed_slots.add_slot')}
                        </button>
                    )}
                </div>
                {renderTable(slots)}
            </div>
        );
    }

    function renderContent() {
        return (
            <>
                {formError && (
                    <div role="alert" className="state-error mb-md">{formError}</div>
                )}
                {renderSection('course')}
                {renderSection('teacher')}
            </>
        );
    }

    return (
        <>
            <ConfirmDeleteModal
                open={showDeleteModal}
                entity={t('fixed_slots.title')}
                id={deleteId}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
            />
            {(showForm || selectedEntity) && (
                <FormModal open={showForm || !!selectedEntity} onClose={handleCloseForm}>
                    <FixedSlotForm
                        form={form}
                        setForm={setForm}
                        formError={formError}
                        onSubmit={handleSubmit}
                        onCancel={handleCloseForm}
                        onDelete={selectedEntity ? () => handleDelete(selectedEntity.id) : undefined}
                    />
                </FormModal>
            )}
            {standalone ? (
                <SectionLayout title={t('fixed_slots.title')}>
                    {renderContent()}
                </SectionLayout>
            ) : (
                <div className="fixed-slots-embedded">
                    {renderContent()}
                </div>
            )}
        </>
    );
}
