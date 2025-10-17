import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import SubjectForm from './SubjectForm';
import './SubjectList.css';

function SubjectList() {
  const [subjects, setSubjects] = useState([]);
  const [courses, setCourses] = useState([]);
  const [daysPerWeek, setDaysPerWeek] = useState(5);
  const [sortBy, setSortBy] = useState('name');
  const [sortAsc, setSortAsc] = useState(true);
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [form, setForm] = useState({ name: '', course_id: '', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true });
  const [showForm, setShowForm] = useState(false);
  const [formError, setFormError] = useState('');
  const [lockedHours, setLockedHours] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchSubjects();
    fetchCourses();
    fetchConfig();
  }, []);

  function fetchConfig() {
    api.get('/config').then(cfg => {
      if (cfg && typeof cfg.days_per_week === 'number') setDaysPerWeek(cfg.days_per_week);
    }).catch(() => {});
  }


  function fetchSubjects() {
    api.get('/subjects').then(setSubjects).catch(() => setSubjects([]));
  }

  function fetchCourses() {
    api.get('/courses').then(setCourses).catch(() => setCourses([]));
  }


  function handleSubmit(e) {
    e.preventDefault();
    const payload = {
      id: form.id,
      name: form.name,
      weekly_hours: form.weekly_hours,
      max_hours_per_day: form.max_hours_per_day,
      consecutive_hours: form.consecutive_hours ?? true,
      teach_every_day: !!form.teach_every_day,
      course_id: form.course_id
    };
    setFormError('');
    const action = editingId ? api.put(`/subjects/${editingId}`, payload) : api.post('/subjects', payload);
    action.then(() => {
      fetchSubjects();
  setForm({ id: '', name: '', course_id: '', weekly_hours: 2, max_hours_per_day: 2, consecutive_hours: true });
      setEditingId(null);
      setShowForm(false);
      setLockedHours(false);
    }).catch(err => setFormError(err.message));
  }

  function handleEdit(subject) {
    setForm({ 
      name: subject.name, 
      course_id: subject.course ? subject.course.id : '', 
      id: subject.id, 
      weekly_hours: subject.weekly_hours ?? 2,
      max_hours_per_day: subject.max_hours_per_day ?? 2,
      consecutive_hours: subject.consecutive_hours ?? true,
      teach_every_day: subject.teach_every_day ?? false,
    });
    const isLocked = subject.subject_groups && subject.subject_groups.length > 0;
    setLockedHours(Boolean(isLocked));
    setEditingId(subject.id);
    setShowForm(true);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    api.del(`/subjects/${deleteId}`).then(() => {
      fetchSubjects();
      setShowDeleteModal(false);
      setDeleteId(null);
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

  const courseOptions = Array.from(new Set(subjects.map(s => s.course ? s.course.name : t('subjects.no_course'))));

  const filteredSubjects = subjects.filter(subject => {
    const matchesName = subject.name.toLowerCase().includes(search.toLowerCase());
    const matchesCourse = courseFilter === '' || (subject.course ? subject.course.name : t('subjects.no_course')) === courseFilter;
    return matchesName && matchesCourse;
  });

  const sortedSubjects = [...filteredSubjects].sort((a, b) => {
    let aField, bField;
    if (sortBy === 'name') {
      aField = a.name || '';
      bField = b.name || '';
    } else if (sortBy === 'course') {
      aField = a.course ? a.course.name : '';
      bField = b.course ? b.course.name : '';
    }
    if (aField < bField) return sortAsc ? -1 : 1;
    if (aField > bField) return sortAsc ? 1 : -1;
    return 0;
  });

  return (
    <div>
      <ConfirmDeleteModal
        open={showDeleteModal}
        entity={t('subjects.title')}
        id={deleteId}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
      <h2>{t('subjects.title')}</h2>
      {showForm ? (
  <FormModal open={showForm} onClose={() => { setForm({ id: '', name: '', course_id: '', weekly_hours: 2, max_hours_per_day: 1, consecutive_hours: true }); setEditingId(null); setShowForm(false); }}>
          <SubjectForm
            form={form}
            setForm={setForm}
            courses={courses}
            lockedHours={lockedHours}
            editingId={editingId}
            daysPerWeek={daysPerWeek}
            formError={formError}
            onSubmit={handleSubmit}
            onCancel={() => { setForm({ id: '', name: '', course_id: '', weekly_hours: 2, max_hours_per_day: 1, consecutive_hours: true }); setEditingId(null); setShowForm(false); }}
          />
        </FormModal>
      ) : (
  <button className="subject-btn-add" onClick={() => { setForm({ id: '', name: '', course_id: '', weekly_hours: 2, max_hours_per_day: 1, consecutive_hours: true }); setShowForm(true); }}>
          {t('subjects.add_subject')}
        </button>
      )}
      <div className="subject-search-bar">
        <input
          type="text"
          placeholder={t('common.search_placeholder')}
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="subject-search-input"
        />
        <select
          value={courseFilter}
          onChange={e => setCourseFilter(e.target.value)}
          className="subject-search-select"
        >
          <option value="">{t('common.all_courses')}</option>
          {courseOptions.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>
      <table className="modern-table">
        <thead>
          <tr>
            <th>{t('common.id') || 'ID'}</th>
            <th className="subject-table-th-sort" onClick={() => handleSort('name')}>
              {t('common.name') || 'Name'} {sortBy === 'name' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="subject-table-th-sort" onClick={() => handleSort('course')}>
              {t('subjects.course') || 'Course'} {sortBy === 'course' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>{t('subjects.group')}</th>
            <th className="subject-table-th-sort" onClick={() => handleSort('weekly_hours')}>
              {t('subjects.weekly_hours')} {sortBy === 'weekly_hours' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="subject-table-th-sort" onClick={() => handleSort('max_hours_per_day')}>
              {t('subjects.max_hours_per_day')} {sortBy === 'max_hours_per_day' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>{t('common_actions.actions')}</th>
          </tr>
        </thead>
        <tbody>
          {sortedSubjects.map(subject => (
            <tr key={subject.id}>
              <td>{subject.id}</td>
              <td>{subject.name}</td>
              <td>{subject.course ? subject.course.name : t('subjects.no_course')}</td>
              <td>
                {subject.subject_groups && subject.subject_groups.length ? (
                  <div className="group-chip-list">
                    {subject.subject_groups.map(g => (
                      <span key={g.id} className="group-chip">{g.name}</span>
                    ))}
                  </div>
                ) : '—'}
              </td>
              <td>{subject.weekly_hours}</td>
              <td>{subject.max_hours_per_day || 2}</td>
              <td>
                <button
                  title={t('common.edit')}
                  style={{ marginRight: 8, padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                  onClick={() => handleEdit(subject)}
                >
                  <span role="img" aria-label={t('common.edit')} style={{ fontSize: '1.2em', color: '#fbbf24' }}>✏️</span>
                </button>
                <button
                  title={t('common.delete')}
                  style={{ padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                  onClick={() => handleDelete(subject.id)}
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

export default SubjectList;
