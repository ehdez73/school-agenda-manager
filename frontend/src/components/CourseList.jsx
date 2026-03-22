import React, { useEffect, useState } from 'react';
import { t } from '../i18n';
import './CourseList.css';
import FormModal from './FormModal';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import CourseForm from './CourseForm';
import SectionLayout from './SectionLayout';

export default function CourseList() {
  const [courses, setCourses] = useState([]);
  const [sortAsc] = useState(true);
  const [search, setSearch] = useState('');
  const [form, setForm] = useState({ name: '', num_lines: 1 });
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = import.meta.env.VITE_API_BASE || '/api';

  const fetchCourses = React.useCallback(() => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/courses`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => setCourses(data))
      .catch(err => setError(err.message || 'Failed to load courses'))
      .finally(() => setLoading(false));
  }, [API_BASE]);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);



  function handleSubmit(e) {
    e.preventDefault();
    const method = editingId ? 'PUT' : 'POST';
    const url = editingId
      ? `${API_BASE}/courses/${form.name}`
      : `${API_BASE}/courses`;

    const payload = {
      name: form.name,
      num_lines: form.num_lines
    };
    fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => {
        if (!res.ok) throw new Error('Save failed');
        return res.json();
      })
      .then(() => {
        fetchCourses();
        setForm({ name: '', num_lines: 1 });
        setEditingId(null);
        setShowForm(false);
      })
      .catch(err => setError(err.message || 'Failed to save'));
  }

  function handleEdit(course) {
    setForm({ name: course.name, num_lines: course.num_lines });
    setEditingId(course.name);
    setShowForm(true);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    fetch(`${API_BASE}/courses/${deleteId}`, { method: 'DELETE' })
      .then(res => {
        if (!res.ok) throw new Error('Delete failed');
        fetchCourses();
        setShowDeleteModal(false);
        setDeleteId(null);
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
    if (a.name < b.name) return sortAsc ? -1 : 1;
    if (a.name > b.name) return sortAsc ? 1 : -1;
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
        title={t('courses.title')}
        actions={
          <button
            className="btn btn--primary btn--compact"
            onClick={() => { setForm({ name: '', num_lines: 1 }); setShowForm(true); }}
          >
            {t('courses.add_course')}
          </button>
        }
      >
        {error && (
          <div role="alert" className="state-error mb-md">
            {error}
          </div>
        )}
        {loading && (
          <div className="state-loading" role="status" aria-live="polite">
            <span className="visually-hidden">{t('courses.loading')}</span>
          </div>
        )}
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
            <th>{t('common_actions.actions')}</th>
          </tr>
        </thead>
        <tbody>
          {sortedCourses.map(course => {
            const grupos = Array.from({ length: course.num_lines }, (_, i) => `${course.name}${String.fromCharCode(65 + i)}`);
            return (
              <tr key={course.name}>
                <td>{course.name}</td>
                <td>{course.num_lines}</td>
                <td>{grupos.join(', ')}</td>
                <td>
                  <button
                    title={t('common.edit')}
                    style={{ marginRight: 8, padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                    onClick={() => handleEdit(course)}
                  >
                    <span role="img" aria-label={t('common.edit')} style={{ fontSize: '1.2em', color: '#fbbf24' }}>✏️</span>
                  </button>
                  <button
                    title={t('common.delete')}
                    style={{ padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                    onClick={() => handleDelete(course.name)}
                  >
                    <span role="img" aria-label={t('common.delete')} style={{ fontSize: '1.2em', color: '#ef4444' }}>🗑️</span>
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      </SectionLayout>
    </>
  );
}
