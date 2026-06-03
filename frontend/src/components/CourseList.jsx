import { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import './CourseList.css';
import FormModal from './FormModal';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import CourseForm from './CourseForm';
import SectionLayout from './SectionLayout';

export default function CourseList({ onViewTimetable }) {
  const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ name: '', num_lines: 1 });
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timetableExists, setTimetableExists] = useState(false);

  function fetchCourses() {
    setLoading(true);
    setError(null);
    api.get('/courses')
      .then(data => setCourses(data))
      .catch(err => setError(err.message || 'Failed to load courses'))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    fetchCourses();
    api.get('/timetable/exists').then(data => setTimetableExists(data?.exists ?? false)).catch(() => setTimetableExists(false));
  }, []);



  function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      name: form.name,
      num_lines: form.num_lines
    };
    const action = editingId
      ? api.put(`/courses/${form.name}`, payload)
      : api.post('/courses', payload);

    action
      .then(() => {
        fetchCourses();
        setForm({ name: '', num_lines: 1 });
        setEditingId(null);
        setShowForm(false);
        setSelectedEntity(null);
      })
      .catch(err => setError(err.message || 'Failed to save'));
  }

  function handleEdit(course) {
    setForm({ name: course.name, num_lines: course.num_lines });
    setEditingId(course.name);
    setShowForm(false);
    setSelectedEntity(course);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    api.del(`/courses/${deleteId}`)
      .then(() => {
        fetchCourses();
        setShowDeleteModal(false);
        setDeleteId(null);
        setSelectedEntity(null);
        setEditingId(null);
        setForm({ name: '', num_lines: 1 });
      })
      .catch(err => setError(err.message || 'Failed to delete'));
  }

  function cancelDelete() {
    setShowDeleteModal(false);
    setDeleteId(null);
  }

  const filteredCourses = courses.filter(course =>
    course.name.toLowerCase().includes(search.toLowerCase())
  );

  const sortedCourses = [...filteredCourses].sort((a, b) => {
    if (a.name < b.name) return -1;
    if (a.name > b.name) return 1;
    return 0;
  });

  return (
    <>
      <ConfirmDeleteModal
        open={showDeleteModal}
        entity={t('courses.title').toLowerCase()}
        id={deleteId}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
      {showForm && (
        <FormModal open={showForm} onClose={() => { setForm({ name: '', num_lines: 1 }); setEditingId(null); setShowForm(false); }}>
          <CourseForm
            form={form}
            setForm={setForm}
            editingId={editingId}
            onSubmit={handleSubmit}
            onCancel={() => { setForm({ name: '', num_lines: 1 }); setEditingId(null); setShowForm(false); }}
          />
        </FormModal>
      )}
      <SectionLayout
        title={selectedEntity ? `${t('common.edit')}: ${selectedEntity.name}` : t('courses.title')}
        actions={
          !showForm && !selectedEntity && (
            <button
              className="btn btn--primary btn--compact"
              onClick={() => { setForm({ name: '', num_lines: 1 }); setShowForm(true); }}
            >
              {t('courses.add_course')}
            </button>
          )
        }
        state={loading ? 'loading' : error ? 'error' : courses.length === 0 && !selectedEntity ? 'empty' : 'ready'}
        errorMsg={error}
        emptyMsg={t('courses.empty')}
      >
        {selectedEntity ? (
          <div className="edit-view">
            <CourseForm
              form={form}
              setForm={setForm}
              editingId={editingId}
              onSubmit={handleSubmit}
              onCancel={() => { setSelectedEntity(null); setEditingId(null); setForm({ name: '', num_lines: 1 }); }}
              onDelete={() => handleDelete(selectedEntity.name)}
            />
          </div>
        ) : (
          <>
            <div className="search-bar">
              <input
                type="text"
                className="input search-input"
                placeholder={t('common.search_placeholder')}
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <table className="modern-table">
              <thead>
                <tr>
                  <th>{t('courses.name')}</th>
                  <th>{t('courses.num_lines')}</th>
                  <th>{t('courses.groups')}</th>
                </tr>
              </thead>
              <tbody>
                {sortedCourses.map(course => {
                  const grupos = Array.from({ length: course.num_lines }, (_, i) => `${course.name}${String.fromCharCode(65 + i)}`);
                  return (
                    <tr key={course.name} onClick={() => handleEdit(course)} className="table-row-clickable">
                      <td>{course.name}</td>
                      <td>{course.num_lines}</td>
                      <td className={timetableExists ? 'course-group-link' : ''} onClick={(e) => { if (timetableExists) { e.stopPropagation(); onViewTimetable(grupos); } }}>{grupos.join(', ')}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </>
        )}
      </SectionLayout>
    </>
  );
}
