import { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import SubjectGroupForm from './SubjectGroupForm';
import './SubjectGroupList.css';
import SectionLayout from './SectionLayout';

export default function SubjectGroupList({ standalone = true }) {
    const [groups, setGroups] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [courses, setCourses] = useState([]);
    const [form, setForm] = useState({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null });
    const [formError, setFormError] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [selectedEntity, setSelectedEntity] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteId, setDeleteId] = useState(null);
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState('name');
    const [sortAsc, setSortAsc] = useState(true);

    useEffect(() => {
        fetchGroups();
        fetchSubjects();
        fetchCourses();
    }, []);

    function fetchGroups() {
        api.get('/subject-groups').then(setGroups).catch(() => setGroups([]));
    }

    function fetchSubjects() {
        api.get('/subjects').then(setSubjects).catch(() => setSubjects([]));
    }

    function fetchCourses() {
        api.get('/courses').then(setCourses).catch(() => setCourses([]));
    }



    function handleSubmit(e) {
        e.preventDefault();

        setFormError('');
        const selectedSubjects = subjects.filter(s => form.subjects.includes(String(s.id)) || form.subjects.includes(Number(s.id)));
        if (selectedSubjects.length > 0) {
            const sharedHours = form.shared_hours;
            if (sharedHours !== null && sharedHours !== undefined) {
                const minHours = Math.min(...selectedSubjects.map(s => s.weekly_hours));
                if (sharedHours < 1 || sharedHours > minHours) {
                    setFormError(t('subject_groups.error_shared_hours_invalid') || 'Shared hours must be between 1 and the minimum weekly hours of selected subjects.');
                    return;
                }
            } else {
                const hoursSet = new Set(selectedSubjects.map(s => s.weekly_hours));
                if (hoursSet.size > 1) {
                    setFormError(t('subject_groups.error_hours_mismatch'));
                    return;
                }
            }
        }

        const payload = { name: form.name, color: form.color || '#fef3c7', subjects: form.subjects, included_lines: form.included_lines, shared_hours: form.shared_hours };
        const action = editingId ? api.put(`/subject-groups/${editingId}`, payload) : api.post('/subject-groups', payload);
        action.then(() => {
            fetchGroups();
            setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null });
            setEditingId(null);
            setShowForm(false);
            setSelectedEntity(null);
        }).catch(err => setFormError(err.message));
    }

    function handleEdit(group) {
        setForm({
            name: group.name || '',
            color: group.color || '#fef3c7',
            subjects: group.subjects ? group.subjects.map(s => String(s.id)) : [],
            included_lines: group.included_lines ?? null,
            shared_hours: group.shared_hours ?? null,
        });
        setEditingId(group.id);
        setShowForm(false);
        setSelectedEntity(group);
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
            setSelectedEntity(null);
            setEditingId(null);
            setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null });
        }).catch(() => { });
    }

    function cancelDelete() {
        setShowDeleteModal(false);
        setDeleteId(null);
    }

    function handleSort(field) {
        if (sortBy === field) {
            setSortAsc(!sortAsc);
        } else {
            setSortBy(field);
            setSortAsc(true);
        }
    }

    const filteredGroups = groups.filter(g => {
        const q = search.toLowerCase();
        if (g.name.toLowerCase().includes(q)) return true;
        if (g.subjects?.some(s => (s.full_name || s.name).toLowerCase().includes(q))) return true;
        return false;
    });

    const locale = navigator.language || 'es';
    const sortedGroups = [...filteredGroups].sort((a, b) => {
        let aField, bField;
        if (sortBy === 'name') {
            aField = a.name || '';
            bField = b.name || '';
        } else if (sortBy === 'subjects') {
            aField = a.subjects ? a.subjects.map(s => s.full_name || s.name).join(', ') : '';
            bField = b.subjects ? b.subjects.map(s => s.full_name || s.name).join(', ') : '';
        }
        return sortAsc
            ? aField.localeCompare(bField, locale)
            : bField.localeCompare(aField, locale);
    });

    const addButton = !showForm && !selectedEntity && (
        <button
            className="btn btn--primary btn--compact"
            onClick={() => { setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null }); setShowForm(true); }}
        >
            {t('subject_groups.add_group')}
        </button>
    );

    const tableContent = (
        <>
            {formError && (
                <div role="alert" className="state-error mb-md">{formError}</div>
            )}

        <div className="search-bar">
          <input
            type="text"
            placeholder={t('common.search_placeholder')}
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input search-input"
          />
        </div>
        <table className="modern-table subject-group-table">
            <thead>
                <tr>
                    <th className={`subject-table-th-sort${sortBy === 'name' ? ' active' : ''}`} onClick={() => handleSort('name')}>
                        {t('common.name') || 'Name'} <span className={sortBy === 'name' ? '' : 'sort-arrow--inactive'}>{sortBy === 'name' ? (sortAsc ? '▲' : '▼') : '▲'}</span>
                    </th>
                    <th className={`subject-table-th-sort${sortBy === 'subjects' ? ' active' : ''}`} onClick={() => handleSort('subjects')}>
                        {t('subject_groups.subjects') || 'Subjects'} <span className={sortBy === 'subjects' ? '' : 'sort-arrow--inactive'}>{sortBy === 'subjects' ? (sortAsc ? '▲' : '▼') : '▲'}</span>
                    </th>
                    <th>{t('subject_groups.shared_hours') || 'Shared h.'}</th>
                </tr>
            </thead>
            <tbody>
                {sortedGroups.map(g => (
                    <tr key={g.id} onClick={() => handleEdit(g)} style={{ cursor: 'pointer' }}>
                        <td>
                            <span className="group-color-chip" style={{ backgroundColor: g.color || '#fef3c7' }} aria-hidden="true" />
                            {g.name}
                        </td>
                        <td>{g.subjects ? g.subjects.map(s => s.full_name || s.name).join(', ') : ''}</td>
                        <td>{g.shared_hours != null ? g.shared_hours : t('common.all') || 'All'}</td>
                    </tr>
                ))}
            </tbody>
        </table>
        </>
    );

    return (
        <>
            <ConfirmDeleteModal
                open={showDeleteModal}
                entity={t('subject_groups.title')}
                id={deleteId}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
            />
            {showForm && (
                <FormModal open={showForm} onClose={() => { setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null }); setEditingId(null); setShowForm(false); setFormError(''); }}>
                    <SubjectGroupForm
                        form={form}
                        setForm={setForm}
                        subjects={subjects}
                        formError={formError}
                        onSubmit={handleSubmit}
                        onCancel={() => { setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null }); setEditingId(null); setShowForm(false); }}
                    />
                </FormModal>
            )}
            {selectedEntity && (
                <FormModal open={!!selectedEntity} onClose={() => { setSelectedEntity(null); setEditingId(null); setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null }); }}>
                    <SubjectGroupForm
                        form={form}
                        setForm={setForm}
                        subjects={subjects}
                        courses={courses}
                        formError={formError}
                        onSubmit={handleSubmit}
                        onCancel={() => { setSelectedEntity(null); setEditingId(null); setForm({ name: '', color: '#fef3c7', subjects: [], included_lines: null, shared_hours: null }); }}
                        onDelete={() => handleDelete(selectedEntity.id)}
                    />
                </FormModal>
            )}
            {standalone ? (
                <SectionLayout
                    title={t('subject_groups.title')}
                    actions={addButton}
                >
                    {tableContent}
                </SectionLayout>
            ) : (
                <div className="subject-groups-embedded">
                    <div className="tab-content-header">
                        {addButton}
                    </div>
                    {tableContent}
                </div>
            )}
        </>
    );
}
