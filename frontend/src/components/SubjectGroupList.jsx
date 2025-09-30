import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import SubjectGroupForm from './SubjectGroupForm';
import './SubjectGroupList.css';

export default function SubjectGroupList() {
    const [groups, setGroups] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [form, setForm] = useState({ name: '', subjects: [] });
    const [formError, setFormError] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteId, setDeleteId] = useState(null);

    useEffect(() => {
        fetchGroups();
        fetchSubjects();
    }, []);

    function fetchGroups() {
        api.get('/subject-groups').then(setGroups).catch(() => setGroups([]));
    }

    function fetchSubjects() {
        api.get('/subjects').then(setSubjects).catch(() => setSubjects([]));
    }



    function handleSubmit(e) {
        e.preventDefault();

        setFormError('');
        const selectedSubjects = subjects.filter(s => form.subjects.includes(String(s.id)) || form.subjects.includes(Number(s.id)));
        if (selectedSubjects.length > 0) {
            const hoursSet = new Set(selectedSubjects.map(s => s.weekly_hours));
            if (hoursSet.size > 1) {
                setFormError(t('subject_groups.error_hours_mismatch'));
                return;
            }
        }

        const payload = { name: form.name, subjects: form.subjects };
        const action = editingId ? api.put(`/subject-groups/${editingId}`, payload) : api.post('/subject-groups', payload);
        action.then(() => {
            fetchGroups();
            setForm({ name: '', subjects: [] });
            setEditingId(null);
            setShowForm(false);
        }).catch(err => setFormError(err.message));
    }

    function handleEdit(group) {
        setForm({ name: group.name || '', subjects: group.subjects ? group.subjects.map(s => String(s.id)) : [] });
        setEditingId(group.id);
        setShowForm(true);
    }

    function handleDelete(id) {
        setDeleteId(id);
        setShowDeleteModal(true);
    }

    function confirmDelete() {
        api.del(`/subject-groups/${deleteId}`).then(() => {
            fetchGroups();
            setShowDeleteModal(false);
            setDeleteId(null);
        }).catch(() => { });
    }

    function cancelDelete() {
        setShowDeleteModal(false);
        setDeleteId(null);
    }

    return (
        <div>
            <ConfirmDeleteModal
                open={showDeleteModal}
                entity={t('subject_groups.title')}
                id={deleteId}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
            />
            <h2>{t('subject_groups.title')}</h2>
            {showForm ? (
                <FormModal open={showForm} onClose={() => { setForm({ name: '', subjects: [] }); setEditingId(null); setShowForm(false); setFormError(''); }}>
                    <SubjectGroupForm
                        form={form}
                        setForm={setForm}
                        subjects={subjects}
                        formError={formError}
                        onSubmit={handleSubmit}
                        onCancel={() => { setForm({ name: '', subjects: [] }); setEditingId(null); setShowForm(false); }}
                    />
                </FormModal>
            ) : (
                <button className="subject-btn-add" onClick={() => { setForm({ name: '', subjects: [] }); setShowForm(true); }}>{t('subject_groups.add_group')}</button>
            )}

            <table className="modern-table">
                <thead>
                    <tr>
                        <th>{t('common.id') || 'ID'}</th>
                        <th>{t('common.name') || 'Name'}</th>
                        <th>{t('subject_groups.subjects') || 'Subjects'}</th>
                        <th>{t('common_actions.actions')}</th>
                    </tr>
                </thead>
                <tbody>
                    {groups.map(g => (
                        <tr key={g.id}>
                            <td>{g.id}</td>
                            <td>{g.name}</td>
                            <td>{g.subjects ? g.subjects.map(s => s.full_name || s.name).join(', ') : ''}</td>
                            <td>
                                <button
                                    title={t('common.edit')}
                                    style={{ marginRight: 8, padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                                    onClick={() => handleEdit(g)}
                                >
                                    <span role="img" aria-label={t('common.edit')} style={{ fontSize: '1.2em', color: '#fbbf24' }}>✏️</span>
                                </button>
                                <button
                                    title={t('common.delete')}
                                    style={{ padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                                    onClick={() => handleDelete(g.id)}
                                >
                                    <span role="img" aria-label={t('common.delete')} style={{ fontSize: '1.2em', color: '#ef4444' }}>🗑️</span>
                                </button>
                            </td>

                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
