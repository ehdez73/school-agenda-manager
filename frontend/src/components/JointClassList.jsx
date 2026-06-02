import { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import JointClassForm from './JointClassForm';
import SectionLayout from './SectionLayout';
import Select from './Select';
import './JointClassList.css';

const INITIAL_FORM = {
    name: '',
    course_id: '',
    subject_id: '',
    teacher_id: null,
    lines: [],
    shared_hours: null,
};

export default function JointClassList({ standalone = true }) {
    const [items, setItems] = useState([]);
    const [courses, setCourses] = useState([]);
    const [subjects, setSubjects] = useState([]);
    const [teachers, setTeachers] = useState([]);
    const [form, setForm] = useState({ ...INITIAL_FORM });
    const [formError, setFormError] = useState('');
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [selectedEntity, setSelectedEntity] = useState(null);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteId, setDeleteId] = useState(null);
    const [search, setSearch] = useState('');
    const [courseFilter, setCourseFilter] = useState('');
    const [sortBy, setSortBy] = useState('name');
    const [sortAsc, setSortAsc] = useState(true);
    const [loading, setLoading] = useState(false);
    const [fetchError, setFetchError] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    function fetchData() {
        setLoading(true);
        setFetchError(null);
        Promise.all([
            api.get('/joint-classes'),
            api.get('/courses'),
            api.get('/subjects'),
            api.get('/teachers'),
        ])
            .then(([jc, c, s, tch]) => {
                setItems(jc);
                setCourses(c);
                setSubjects(s);
                setTeachers(tch);
            })
            .catch(err => setFetchError(err.message))
            .finally(() => setLoading(false));
    }

    function handleSubmit(e) {
        e.preventDefault();
        setFormError('');

        if (!form.lines || form.lines.length < 2) {
            setFormError('At least 2 lines must be selected.');
            return;
        }

        const payload = {
            name: form.name || null,
            course_id: form.course_id,
            subject_id: form.subject_id,
            teacher_id: form.teacher_id,
            lines: form.lines,
            shared_hours: form.shared_hours,
        };

        const action = editingId
            ? api.put(`/joint-classes/${editingId}`, payload)
            : api.post('/joint-classes', payload);

        action
            .then(() => {
                fetchData();
                resetForm();
            })
            .catch(err => setFormError(err.message));
    }

    function handleEdit(item) {
        setForm({
            name: item.name || '',
            course_id: item.course_id,
            subject_id: item.subject_id,
            teacher_id: item.teacher_id,
            lines: item.lines || [],
            shared_hours: item.shared_hours ?? null,
        });
        setEditingId(item.id);
        setShowForm(false);
        setSelectedEntity(item);
    }

    function handleDelete(id) {
        setDeleteId(id);
        setShowDeleteModal(true);
    }

    function confirmDelete() {
        api.del(`/joint-classes/${deleteId}`)
            .then(() => {
                fetchData();
                setShowDeleteModal(false);
                setDeleteId(null);
                resetForm();
                setSelectedEntity(null);
            })
            .catch(() => {});
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

    function resetForm() {
        setForm({ ...INITIAL_FORM });
        setEditingId(null);
        setShowForm(false);
        setSelectedEntity(null);
        setFormError('');
    }

    const courseOptions = Array.from(new Set(items.map(i => i.course ? i.course.name : ''))).filter(Boolean).sort((a, b) => a.localeCompare(b));

    const filteredItems = items.filter(item => {
        const q = search.toLowerCase();
        const matchesCourse = courseFilter === '' || (item.course ? item.course.name : '') === courseFilter;
        if (!matchesCourse) return false;
        if ((item.name || '').toLowerCase().includes(q)) return true;
        if ((item.course_id || '').toLowerCase().includes(q)) return true;
        if (item.subject?.name?.toLowerCase().includes(q)) return true;
        if (item.subject?.full_name?.toLowerCase().includes(q)) return true;
        if (item.teacher?.name?.toLowerCase().includes(q)) return true;
        if ((item.lines || []).join(' ').toLowerCase().includes(q)) return true;
        return false;
    });

    const locale = navigator.language || 'es';
    const sortedItems = [...filteredItems].sort((a, b) => {
        let aField, bField;
        if (sortBy === 'name') {
            aField = (a.name || String(a.course_id) + ' ' + (a.lines || []).join('+')) || '';
            bField = (b.name || String(b.course_id) + ' ' + (b.lines || []).join('+')) || '';
        } else if (sortBy === 'course') {
            aField = a.course ? a.course.name : '';
            bField = b.course ? b.course.name : '';
        } else if (sortBy === 'subject') {
            aField = a.subject?.full_name || a.subject?.name || '';
            bField = b.subject?.full_name || b.subject?.name || '';
        }
        return sortAsc
            ? aField.localeCompare(bField, locale)
            : bField.localeCompare(aField, locale);
    });

    const addButton = !selectedEntity && (
        <button
            className="btn btn--primary btn--compact"
            onClick={() => { resetForm(); setShowForm(true); }}
        >
            {t('joint_classes.add')}
        </button>
    );

    const tableContent = (
        <>
            <div className="search-bar">
                <input
                    type="text"
                    className="input search-input"
                    placeholder={t('common.search_placeholder')}
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <Select
                    value={courseFilter}
                    onChange={e => setCourseFilter(e.target.value)}
                    options={[
                        { value: '', label: t('common.all_courses') },
                        ...courseOptions.map(c => ({ value: c, label: c })),
                    ]}
                    className="search-select"
                />
            </div>
            <table className="modern-table joint-class-table">
                <thead>
                    <tr>
                        <th className={`subject-table-th-sort${sortBy === 'name' ? ' active' : ''}`} onClick={() => handleSort('name')}>
                            {t('common.name')} <span className={sortBy === 'name' ? '' : 'sort-arrow--inactive'}>{sortBy === 'name' ? (sortAsc ? '▲' : '▼') : '▲'}</span>
                        </th>
                        <th className={`subject-table-th-sort${sortBy === 'course' ? ' active' : ''}`} onClick={() => handleSort('course')}>
                            {t('joint_classes.course')} <span className={sortBy === 'course' ? '' : 'sort-arrow--inactive'}>{sortBy === 'course' ? (sortAsc ? '▲' : '▼') : '▲'}</span>
                        </th>
                        <th className={`subject-table-th-sort${sortBy === 'subject' ? ' active' : ''}`} onClick={() => handleSort('subject')}>
                            {t('joint_classes.subject')} <span className={sortBy === 'subject' ? '' : 'sort-arrow--inactive'}>{sortBy === 'subject' ? (sortAsc ? '▲' : '▼') : '▲'}</span>
                        </th>
                        <th>{t('joint_classes.lines')}</th>
                        <th>{t('joint_classes.teacher')}</th>
                        <th>{t('joint_classes.shared_hours')}</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedItems.map(item => (
                        <tr key={item.id} onClick={() => handleEdit(item)} style={{ cursor: 'pointer' }}>
                            <td>{item.name || item.course_id + ' ' + (item.lines || []).join('+')}</td>
                            <td className="joint-class-course">{item.course?.name || item.course_id}</td>
                            <td>{item.subject?.full_name || item.subject?.name || item.subject_id}</td>
                            <td>
                                <div className="joint-class-lines-chip">
                                    {(item.lines || []).map(l => (
                                        <span key={l} className="chip">{l}</span>
                                    ))}
                                </div>
                            </td>
                            <td>
                                {item.teacher ? (
                                    <span className="joint-class-teacher">{item.teacher.name}</span>
                                ) : (
                                    <span className="joint-class-teacher joint-class-teacher--auto">
                                        {t('joint_classes.teacher_none')}
                                    </span>
                                )}
                            </td>
                            <td>
                                {item.shared_hours != null
                                    ? `${item.shared_hours}h`
                                    : <span className="joint-class-teacher--auto">{t('joint_classes.all_hours')}</span>}
                            </td>
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
                entity={t('joint_classes.confirm_delete')}
                id={deleteId}
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
            />

            {showForm && (
                <FormModal open={showForm} onClose={resetForm}>
                    <JointClassForm
                        form={form}
                        setForm={setForm}
                        courses={courses}
                        subjects={subjects}
                        teachers={teachers}
                        formError={formError}
                        onSubmit={handleSubmit}
                        onCancel={resetForm}
                    />
                </FormModal>
            )}

            {selectedEntity && (
                <FormModal open={!!selectedEntity} onClose={() => { setSelectedEntity(null); resetForm(); }}>
                    <JointClassForm
                        form={form}
                        setForm={setForm}
                        courses={courses}
                        subjects={subjects}
                        teachers={teachers}
                        formError={formError}
                        onSubmit={handleSubmit}
                        onCancel={() => { setSelectedEntity(null); resetForm(); }}
                        onDelete={() => handleDelete(selectedEntity.id)}
                    />
                </FormModal>
            )}

            {standalone ? (
                <SectionLayout
                    title={selectedEntity
                        ? `${t('common.edit')}: ${selectedEntity.name || selectedEntity.course_id + ' ' + (selectedEntity.lines || []).join('+')}`
                        : t('joint_classes.title')}
                    actions={addButton}
                    state={loading ? 'loading' : fetchError ? 'error' : items.length === 0 && !selectedEntity ? 'empty' : 'ready'}
                    errorMsg={fetchError}
                    emptyMsg={t('joint_classes.empty')}
                >
                    {tableContent}
                </SectionLayout>
            ) : (
                <div className="joint-classes-embedded">
                    <div className="tab-content-header">
                        {addButton}
                    </div>
                    {tableContent}
                </div>
            )}
        </>
    );
}
