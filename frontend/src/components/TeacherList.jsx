import React, { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import FormModal from './FormModal';
import TeacherForm from './TeacherForm';
import './TeacherList.css';

export default function TeacherList() {
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortAsc, setSortAsc] = useState(true);
   const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('');
  const [form, setForm] = useState({ name: '', subjects: [], max_hours_week: 1, preferences: {} });
  const [classesPerDay, setClassesPerDay] = useState(5);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [courseFilter, setCourseFilter] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    fetchTeachers();
    fetchSubjects();
    fetchCourses();
    api.get('/config').then(cfg => setClassesPerDay(cfg?.classes_per_day || 5)).catch(() => setClassesPerDay(5));
  }, []);

  function fetchSubjects() {
    api.get('/subjects').then(setSubjects).catch(() => setSubjects([]));
  }

  function fetchCourses() {
    api.get('/courses').then(setCourses).catch(() => setCourses([]));
  }

  function fetchTeachers() {
    api.get('/teachers').then(setTeachers).catch(() => setTeachers([]));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const preferences_obj = form.preferences || {};
    const payload = {
      name: form.name,
      subjects: form.subjects,
      tutor_group: form.tutor_group || null,
      max_hours_week: Number(form.max_hours_week) > 0 ? Number(form.max_hours_week) : 1,
      preferences: preferences_obj
    };
    const action = editingId
      ? api.put(`/teachers/${editingId}`, payload)
      : api.post('/teachers', payload);

    action.then(() => {
      fetchTeachers();
      setForm({ name: '', subjects: [], max_hours_week: 1, preferences: {}, tutor_group: null });
      setEditingId(null);
      setShowForm(false);
    }).catch(() => { });
  }

  function handleEdit(teacher) {
    setForm({
      id: teacher.id,
      name: teacher.name,
      subjects: teacher.subjects ? teacher.subjects.map(s => String(s.id)) : [],
      tutor_group: teacher.tutor_group ?? null,
      max_hours_week: teacher.max_hours_week ?? 1,
      preferences: teacher.preferences || {}
    });
    setEditingId(teacher.id);
    setShowForm(true);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    api.del(`/teachers/${deleteId}`).then(() => {
      fetchTeachers();
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

  const subjectOptions = Array.from(new Set(
    teachers.flatMap(t => t.subjects ? t.subjects.map(s => s.name) : [])
  ));

  const courseOptions = Array.from(new Set(
    subjects.filter(s => s.course).map(s => s.course.name)
  ));

  // Build a list of concrete groups (course + letter), e.g. '1ºA', '1ºB'
  const groupsList = courses.flatMap(course => {
    const num = Number(course.num_lines) || 1;
    return Array.from({ length: num }, (_, i) => {
      const name = `${course.name}${String.fromCharCode(65 + i)}`;
      return { id: name, name };
    });
  }).map(g => {
    // detect if any teacher has this group assigned (teacher.tutor_group expected to be group id/name)
    const tutor = teachers.find(t => String(t.tutor_group) === String(g.id));
    return { ...g, tutor_id: tutor ? tutor.id : null };
  });

  const filteredTeachers = teachers.filter(teacher => {
    const matchesName = (teacher.name || '').toLowerCase().includes(search.toLowerCase());
    const matchesSubject = subjectFilter === '' || (teacher.subjects && teacher.subjects.map(s => s.name).includes(subjectFilter));
    const matchesCourse = courseFilter === '' || (teacher.subjects && teacher.subjects.some(s => s.course && s.course.name === courseFilter));
    return matchesName && matchesSubject && matchesCourse;
  });

  const sortedTeachers = [...filteredTeachers].sort((a, b) => {
    let aField, bField;
    if (sortBy === 'name') {
      aField = a.name || '';
      bField = b.name || '';
    } else if (sortBy === 'subjects') {
      aField = a.subjects ? a.subjects.map(s => s.name).join(', ') : '';
      bField = b.subjects ? b.subjects.map(s => s.name).join(', ') : '';
    }
    if (aField < bField) return sortAsc ? -1 : 1;
    if (aField > bField) return sortAsc ? 1 : -1;
    return 0;
  });

  return (
    <div>
      <ConfirmDeleteModal
        open={showDeleteModal}
        entity={t('teachers.title')}
        id={deleteId}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
      <h2>{t('teachers.title')}</h2>
      {showForm ? (
        <FormModal open={showForm} onClose={() => { setForm({ name: '', subjects: [], max_hours_week: 1, preferences: {}, tutor_group: null }); setEditingId(null); setShowForm(false); }}>
          <TeacherForm
            form={form}
            setForm={setForm}
            subjects={subjects}
            groups={groupsList}
            classesPerDay={classesPerDay}
            onSubmit={handleSubmit}
            onCancel={() => { setForm({ name: '', subjects: [], max_hours_week: 1, preferences: {}, tutor_group: null }); setEditingId(null); setShowForm(false); }}
          />
        </FormModal>
      ) : (
        <button className="teacher-btn teacher-btn-add" onClick={() => { setForm({ name: '', subjects: [], max_hours_week: 1, preferences: {}, tutor_group: null }); setShowForm(true); }}>
          {t('teachers.add_teacher')}
        </button>
      )}
      <div className="teacher-search-bar">
        <input
          type="text"
          placeholder={t('common.search_placeholder')}
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="teacher-search-input"
        />
        <select
          value={subjectFilter}
          onChange={e => setSubjectFilter(e.target.value)}
          className="teacher-search-select"
        >
          <option value="">{t('common.all_subjects')}</option>
          {subjectOptions.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={courseFilter}
          onChange={e => setCourseFilter(e.target.value)}
          className="teacher-search-select"
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
            <th className="teacher-table-th-sort" onClick={() => handleSort('name')}>
              {t('common.name') || 'Name'} {sortBy === 'name' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th className="teacher-table-th-sort" onClick={() => handleSort('subjects')}>
              {t('teachers_table.subjects') || 'Subjects'} {sortBy === 'subjects' ? (sortAsc ? '▲' : '▼') : ''}
            </th>
            <th>{t('teachers.tutor_group') || 'Tutor'}</th>
            <th>{t('teachers.hours_week')}</th>
            <th>{t('common_actions.actions')}</th>
          </tr>
        </thead>
        <tbody>
          {sortedTeachers.map(teacher => (
            <tr key={teacher.id}>
              <td>{teacher.id}</td>
              <td>{teacher.name}</td>
              <td>{teacher.subjects ? teacher.subjects.map(s => `${s.full_name}`).join(', ') : ''}</td>
              <td>{teacher.tutor_group ?? ''}</td>
              <td>{teacher.max_hours_week ?? ''}</td>
              <td>
                <button
                  title={t('common.edit')}
                  style={{ marginRight: 8, padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                  onClick={() => handleEdit(teacher)}
                >
                  <span role="img" aria-label={t('common.edit')} style={{ fontSize: '1.2em', color: '#fbbf24' }}>✏️</span>
                </button>
                <button
                  title={t('common.delete')}
                  style={{ padding: '4px', borderRadius: 4, border: 'none', background: 'transparent', cursor: 'pointer' }}
                  onClick={() => handleDelete(teacher.id)}
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
